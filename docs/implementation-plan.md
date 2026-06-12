# Atoms Demo Implementation Plan

## MVP Scope

- JWT auth with a development in-memory repository.
- Agent sessions with SSE streaming.
- Mock LLM provider and replaceable provider interface.
- Generated HTML/CSS/JS previewed in a sandboxed iframe.
- Generated app save/list/detail APIs.

## Next Backend Steps

1. Replace `InMemoryRepository` with SQLAlchemy repositories.
2. Add Alembic migrations for `users`, `agent_sessions`, `generated_apps`, `tasks`.
3. Add DeepSeek/Qwen providers behind `LLMProvider`.
4. Move long-running generation into Celery tasks.
5. Add S3/MinIO storage for preview snapshots and multimodal assets.

## Next Frontend Steps

1. Replace textarea editor with Monaco Editor.
2. Add login/register screens instead of automatic demo user creation.
3. Add saved app gallery and app detail page.
4. Add WebSocket task progress for image/music generation.
5. Add responsive preview controls for desktop/tablet/mobile widths.
