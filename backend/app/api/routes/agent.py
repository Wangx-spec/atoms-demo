from uuid import UUID

from fastapi import APIRouter, Depends, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.db import UserORM
from app.schemas.agent import (
    AgentSessionResponse,
    AgentSessionSummary,
    CreateSessionRequest,
    SendMessageRequest,
    SendMessageResponse,
    UpdateSessionRequest,
)
from app.schemas.apps import GeneratedCodePayload
from app.services.agent_service import AgentService, stream_generation

router = APIRouter()


@router.post("/sessions", response_model=AgentSessionResponse)
async def create_session(
    payload: CreateSessionRequest,
    current_user: UserORM = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AgentSessionResponse:
    return await AgentService(db).create_session(current_user, payload.title)


@router.get("/sessions", response_model=list[AgentSessionSummary])
async def list_sessions(
    current_user: UserORM = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[AgentSessionSummary]:
    return await AgentService(db).list_sessions(current_user)


@router.get("/sessions/{session_id}", response_model=AgentSessionResponse)
async def get_session(
    session_id: UUID,
    current_user: UserORM = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AgentSessionResponse:
    return await AgentService(db).get_session(current_user, session_id)


@router.patch("/sessions/{session_id}", response_model=AgentSessionResponse)
async def rename_session(
    session_id: UUID,
    payload: UpdateSessionRequest,
    current_user: UserORM = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AgentSessionResponse:
    return await AgentService(db).rename_session(current_user, session_id, payload.title)


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    session_id: UUID,
    current_user: UserORM = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    await AgentService(db).delete_session(current_user, session_id)


@router.post("/sessions/{session_id}/messages", response_model=SendMessageResponse)
async def send_message(
    session_id: UUID,
    payload: SendMessageRequest,
    current_user: UserORM = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SendMessageResponse:
    await AgentService(db).append_user_message(current_user, session_id, payload.prompt)
    return SendMessageResponse(
        session_id=session_id,
        stream_url=f"/api/agent/sessions/{session_id}/stream",
    )


@router.get("/sessions/{session_id}/stream")
async def stream_session(
    session_id: UUID,
    current_user: UserORM = Depends(get_current_user),
) -> StreamingResponse:
    async def event_stream():
        async for sse_chunk in stream_generation(current_user, session_id):
            yield sse_chunk
        yield "event: done\ndata: ok\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.post("/sessions/{session_id}/generate-code", response_model=GeneratedCodePayload)
async def generate_code(
    session_id: UUID,
    current_user: UserORM = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> GeneratedCodePayload:
    return await AgentService(db).generate_code(current_user, session_id)
