"""Object storage (MinIO) helper.

Lazily constructs the clients so the API can boot without MinIO running; the
connection is only established on first upload.

Two clients are used:

- An *internal* client pointed at ``minio_endpoint`` (e.g. ``minio:9000`` inside
  Docker) for bucket creation and uploads.
- A *public* client pointed at ``minio_public_endpoint`` (e.g. ``localhost:9100``)
  used only to sign presigned GET URLs. Signing is offline, so the public client
  does not need to be network-reachable from the server process - only the host
  it points at needs to be reachable from the browser.
"""
from __future__ import annotations

import io
import uuid
from datetime import timedelta

from app.core.config import settings


class StorageService:
    def __init__(self) -> None:
        self._client = None
        self._public_client = None
        self._bucket_ready = False

    def _get_client(self):
        if self._client is None:
            from minio import Minio

            self._client = Minio(
                settings.minio_endpoint,
                access_key=settings.minio_access_key,
                secret_key=settings.minio_secret_key,
                secure=settings.minio_secure,
                region=settings.minio_region,
            )
        return self._client

    def _get_public_client(self):
        if self._public_client is None:
            from minio import Minio

            # ``region`` is required here: without it presigned_get_object would
            # trigger a GetBucketLocation network call against the (possibly
            # unreachable) public endpoint instead of signing offline.
            self._public_client = Minio(
                settings.minio_public_endpoint,
                access_key=settings.minio_access_key,
                secret_key=settings.minio_secret_key,
                secure=settings.minio_secure,
                region=settings.minio_region,
            )
        return self._public_client

    def _ensure_bucket(self) -> None:
        if self._bucket_ready:
            return
        client = self._get_client()
        if not client.bucket_exists(settings.minio_bucket):
            client.make_bucket(settings.minio_bucket)
        self._bucket_ready = True

    def upload_bytes(self, data: bytes, content_type: str, ext: str) -> str:
        """Upload bytes and return the stored object key (not a URL)."""
        self._ensure_bucket()
        object_name = f"{uuid.uuid4().hex}.{ext.lstrip('.')}"
        client = self._get_client()
        client.put_object(
            settings.minio_bucket,
            object_name,
            io.BytesIO(data),
            length=len(data),
            content_type=content_type,
        )
        return object_name

    def presigned_url(self, object_key: str, expires: int = 3600) -> str:
        """Generate a browser-reachable presigned GET URL for an object key."""
        client = self._get_public_client()
        return client.presigned_get_object(
            settings.minio_bucket,
            object_key,
            expires=timedelta(seconds=expires),
        )


storage_service = StorageService()
