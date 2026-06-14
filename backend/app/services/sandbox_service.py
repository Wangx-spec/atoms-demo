"""Docker-based code sandbox.

Runs generated projects inside isolated containers with strict resource limits.
Security defaults: no network, capped memory/CPU, auto-reaped after a timeout.

The backend process must have access to the Docker daemon (e.g. mount
``/var/run/docker.sock``). All docker SDK calls are sync, so they run in a thread.
"""
from __future__ import annotations

import asyncio
import io
import tarfile
import time
from dataclasses import dataclass, field

from app.core.config import settings


@dataclass
class SandboxInstance:
    app_id: str
    container_id: str
    port: int
    runtime: str
    preview_url: str
    status: str = "running"
    started_at: float = field(default_factory=time.time)
    error: str | None = None


class SandboxError(RuntimeError):
    pass


class SandboxService:
    def __init__(self) -> None:
        self._instances: dict[str, SandboxInstance] = {}
        self._used_ports: set[int] = set()
        self._client = None
        self._lock = asyncio.Lock()

    def _get_client(self):
        if self._client is None:
            import docker

            self._client = docker.from_env()
        return self._client

    def _alloc_port(self) -> int:
        for port in range(settings.sandbox_port_start, settings.sandbox_port_end + 1):
            if port not in self._used_ports:
                self._used_ports.add(port)
                return port
        raise SandboxError("No free sandbox port available")

    def _build_files(self, app) -> dict[str, str]:
        """Assemble a project file tree from stored files or the html/css/js."""
        index = (
            "<!doctype html><html lang=\"zh-CN\"><head><meta charset=\"UTF-8\"/>"
            f"<style>{app.css or ''}</style></head><body>{app.html or ''}"
            f"<script>{app.js or ''}</script></body></html>"
        )
        return {"index.html": index}

    def _tar_bytes(self, files: dict[str, str]) -> bytes:
        buffer = io.BytesIO()
        with tarfile.open(fileobj=buffer, mode="w") as tar:
            for path, content in files.items():
                data = content.encode("utf-8")
                info = tarfile.TarInfo(name=path)
                info.size = len(data)
                tar.addfile(info, io.BytesIO(data))
        return buffer.getvalue()

    def _image_and_target(self, runtime: str) -> tuple[str, str, int, str | None]:
        """Return (image, dest_dir, container_port, command)."""
        if runtime == "node-vite":
            return (
                settings.sandbox_node_image,
                "/app",
                80,
                "sh -c 'npm install && npm run dev -- --host 0.0.0.0 --port 80'",
            )
        if runtime == "python-fastapi":
            return (
                settings.sandbox_python_image,
                "/app",
                80,
                "sh -c 'pip install fastapi uvicorn && uvicorn main:app --host 0.0.0.0 --port 80'",
            )
        # static-html
        return (settings.sandbox_static_image, "/usr/share/nginx/html", 80, None)

    async def start(self, app) -> SandboxInstance:
        if not settings.sandbox_enabled:
            raise SandboxError("Sandbox is disabled (set SANDBOX_ENABLED=true)")

        app_id = str(app.id)
        async with self._lock:
            existing = self._instances.get(app_id)
            if existing and existing.status == "running":
                return existing
            return await asyncio.to_thread(self._start_sync, app)

    def _start_sync(self, app) -> SandboxInstance:
        runtime = getattr(app, "runtime", "static-html") or "static-html"
        image, dest_dir, container_port, command = self._image_and_target(runtime)
        files = self._build_files(app)
        port = self._alloc_port()
        # node/python need network to install deps; static html does not.
        network_disabled = settings.sandbox_network_disabled and runtime == "static-html"

        try:
            client = self._get_client()
            container = client.containers.create(
                image=image,
                command=command,
                detach=True,
                working_dir=dest_dir if runtime != "static-html" else None,
                ports={f"{container_port}/tcp": port},
                mem_limit=settings.sandbox_mem_limit,
                nano_cpus=int(settings.sandbox_cpus * 1_000_000_000),
                network_disabled=network_disabled,
                labels={"atoms.sandbox": "1", "atoms.app_id": str(app.id)},
            )
            container.put_archive(dest_dir, self._tar_bytes(files))
            container.start()
        except Exception as exc:  # surface docker errors as SandboxError
            self._used_ports.discard(port)
            raise SandboxError(f"Failed to start sandbox: {exc}") from exc

        instance = SandboxInstance(
            app_id=str(app.id),
            container_id=container.id,
            port=port,
            runtime=runtime,
            preview_url=f"http://{settings.sandbox_public_host}:{port}",
        )
        self._instances[str(app.id)] = instance
        return instance

    def get(self, app_id: str) -> SandboxInstance | None:
        return self._instances.get(app_id)

    async def logs(self, app_id: str) -> str:
        instance = self._instances.get(app_id)
        if not instance:
            return ""
        return await asyncio.to_thread(self._logs_sync, instance.container_id)

    def _logs_sync(self, container_id: str) -> str:
        try:
            container = self._get_client().containers.get(container_id)
            return container.logs(tail=200).decode("utf-8", errors="replace")
        except Exception as exc:
            return f"<unable to read logs: {exc}>"

    async def stop(self, app_id: str) -> None:
        async with self._lock:
            instance = self._instances.pop(app_id, None)
        if not instance:
            return
        self._used_ports.discard(instance.port)
        await asyncio.to_thread(self._stop_sync, instance.container_id)

    def _stop_sync(self, container_id: str) -> None:
        try:
            container = self._get_client().containers.get(container_id)
            container.remove(force=True)
        except Exception:
            pass

    async def reap_loop(self) -> None:
        """Background loop: stop containers older than the configured timeout."""
        while True:
            await asyncio.sleep(30)
            now = time.time()
            expired = [
                app_id
                for app_id, inst in list(self._instances.items())
                if now - inst.started_at > settings.sandbox_timeout_seconds
            ]
            for app_id in expired:
                await self.stop(app_id)


sandbox_service = SandboxService()
