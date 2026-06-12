from collections.abc import AsyncIterator
from uuid import UUID

from fastapi import HTTPException, status

from app.models.entities import AgentMessage, AgentSession, User
from app.schemas.agent import AgentSessionResponse
from app.schemas.apps import GeneratedCodePayload
from app.services.codegen_service import codegen_service
from app.services.llm_service import get_llm_provider
from app.services.repository import repository


class AgentService:
    def create_session(self, user: User, title: str | None = None) -> AgentSessionResponse:
        session = repository.add_session(
            AgentSession(user_id=user.id, title=title or "新的创作会话")
        )
        return AgentSessionResponse(id=session.id, title=session.title, messages=session.messages)

    def append_user_message(self, user: User, session_id: UUID, prompt: str) -> None:
        session = self._get_owned_session(user, session_id)
        session.messages.append(AgentMessage(role="user", content=prompt))

    async def stream_generation(self, user: User, session_id: UUID) -> AsyncIterator[str]:
        session = self._get_owned_session(user, session_id)
        prompt = session.messages[-1].content if session.messages else ""
        provider = get_llm_provider()
        response_text = ""

        async for chunk in provider.stream(prompt):
            response_text += chunk
            yield chunk

        session.messages.append(AgentMessage(role="assistant", content=response_text))

    async def generate_code(self, user: User, session_id: UUID) -> GeneratedCodePayload:
        session = self._get_owned_session(user, session_id)
        prompt = session.messages[-1].content if session.messages else ""
        return await codegen_service.generate_app(prompt)

    def _get_owned_session(self, user: User, session_id: UUID) -> AgentSession:
        session = repository.get_session(session_id)
        if not session or session.user_id != user.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
        return session


agent_service = AgentService()
