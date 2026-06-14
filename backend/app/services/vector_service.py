"""Vector store (Qdrant) integration for semantic search and recommendations.

The client is created lazily so the API boots without Qdrant running.
"""
from __future__ import annotations

from uuid import UUID

from app.core.config import settings
from app.services.embedding_service import get_embedding_provider


class VectorService:
    def __init__(self) -> None:
        self._client = None
        self._ready = False

    def _get_client(self):
        if self._client is None:
            from qdrant_client import QdrantClient

            self._client = QdrantClient(url=settings.qdrant_url)
        return self._client

    def _ensure_collection(self) -> None:
        if self._ready:
            return
        from qdrant_client.models import Distance, VectorParams

        client = self._get_client()
        existing = {c.name for c in client.get_collections().collections}
        if settings.qdrant_collection not in existing:
            client.create_collection(
                collection_name=settings.qdrant_collection,
                vectors_config=VectorParams(
                    size=settings.embedding_dim, distance=Distance.COSINE
                ),
            )
        self._ready = True

    async def upsert(self, app_id: UUID, text: str, payload: dict) -> None:
        from qdrant_client.models import PointStruct

        self._ensure_collection()
        vector = await get_embedding_provider().embed(text)
        self._get_client().upsert(
            collection_name=settings.qdrant_collection,
            points=[PointStruct(id=str(app_id), vector=vector, payload=payload)],
        )

    async def search(self, query: str, limit: int = 20) -> list[str]:
        self._ensure_collection()
        vector = await get_embedding_provider().embed(query)
        results = self._get_client().search(
            collection_name=settings.qdrant_collection, query_vector=vector, limit=limit
        )
        return [str(point.id) for point in results]

    async def similar(self, app_id: UUID, limit: int = 8) -> list[str]:
        self._ensure_collection()
        results = self._get_client().recommend(
            collection_name=settings.qdrant_collection,
            positive=[str(app_id)],
            limit=limit,
        )
        return [str(point.id) for point in results]

    def delete(self, app_id: UUID) -> None:
        try:
            self._ensure_collection()
            self._get_client().delete(
                collection_name=settings.qdrant_collection, points_selector=[str(app_id)]
            )
        except Exception:
            pass


vector_service = VectorService()


async def run_embed_artwork(app_id: UUID) -> None:
    """Embed a public artwork into the vector store. Used by Celery / inline fallback."""
    from app.db.session import async_session
    from app.repositories.generated_apps import GeneratedAppRepository

    async with async_session() as db:
        app = await GeneratedAppRepository(db).get(app_id)
        if not app or app.visibility != "public":
            return
        text = "\n".join(
            filter(
                None,
                [app.title, app.prompt, app.tags, (app.html or "")[:500]],
            )
        )
        payload = {
            "app_id": str(app.id),
            "user_id": str(app.user_id),
            "title": app.title,
            "prompt": app.prompt,
            "tags": app.tags,
            "preview_url": app.preview_url,
        }
        try:
            await vector_service.upsert(app.id, text, payload)
        except Exception:
            # Vector store unavailable; embedding will be retried on next publish.
            pass
