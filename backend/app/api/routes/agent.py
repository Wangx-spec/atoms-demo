from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.api.deps import get_current_user
from app.models.entities import User
from app.schemas.agent import CreateSessionRequest, SendMessageRequest, SendMessageResponse
from app.schemas.apps import GeneratedCodePayload
from app.services.agent_service import agent_service

router = APIRouter()


@router.post("/sessions")
async def create_session(
    payload: CreateSessionRequest,
    current_user: User = Depends(get_current_user),
):
    return agent_service.create_session(current_user, payload.title)


@router.post("/sessions/{session_id}/messages", response_model=SendMessageResponse)
async def send_message(
    session_id: UUID,
    payload: SendMessageRequest,
    current_user: User = Depends(get_current_user),
) -> SendMessageResponse:
    agent_service.append_user_message(current_user, session_id, payload.prompt)
    return SendMessageResponse(
        session_id=session_id,
        stream_url=f"/api/agent/sessions/{session_id}/stream",
    )


@router.get("/sessions/{session_id}/stream")
async def stream_session(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
) -> StreamingResponse:
    async def event_stream():
        async for chunk in agent_service.stream_generation(current_user, session_id):
            yield f"data: {chunk}\n\n"
        yield "event: done\ndata: ok\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.post("/sessions/{session_id}/generate-code", response_model=GeneratedCodePayload)
async def generate_code(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
) -> GeneratedCodePayload:
    return await agent_service.generate_code(current_user, session_id)
