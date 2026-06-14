from collections.abc import AsyncIterator
from datetime import UTC, datetime
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.nodes import (
    analyze_requirement,
    generate_code_node,
    plan_structure,
    review_code_node,
)
from app.agents.state import AgentState
from app.db.session import async_session
from app.models.db import AgentSessionORM, UserORM
from app.repositories.agent_sessions import AgentSessionRepository
from app.schemas.agent import AgentSessionResponse, AgentSessionSummary
from app.schemas.apps import GeneratedCodePayload
from app.schemas.events import AgentEvent, AgentEventType
from app.services.codegen_service import codegen_service


def _message(role: str, content: str) -> dict:
    return {"role": role, "content": content, "created_at": datetime.now(UTC).isoformat()}


class AgentService:
    def __init__(self, db: AsyncSession) -> None:
        self.sessions = AgentSessionRepository(db)

    async def create_session(self, user: UserORM, title: str | None = None) -> AgentSessionResponse:
        session = await self.sessions.create(user_id=user.id, title=title or "新的创作会话")
        return AgentSessionResponse(id=session.id, title=session.title, messages=session.messages)

    async def list_sessions(self, user: UserORM) -> list[AgentSessionSummary]:
        sessions = await self.sessions.list_by_user(user.id)
        return [AgentSessionSummary.model_validate(s, from_attributes=True) for s in sessions]

    async def get_session(self, user: UserORM, session_id: UUID) -> AgentSessionResponse:
        session = await self._get_owned_session(user, session_id)
        return AgentSessionResponse(id=session.id, title=session.title, messages=session.messages)

    async def rename_session(
        self, user: UserORM, session_id: UUID, title: str
    ) -> AgentSessionResponse:
        session = await self._get_owned_session(user, session_id)
        updated = await self.sessions.update(session, {"title": title})
        return AgentSessionResponse(id=updated.id, title=updated.title, messages=updated.messages)

    async def delete_session(self, user: UserORM, session_id: UUID) -> None:
        session = await self._get_owned_session(user, session_id)
        await self.sessions.delete(session)

    async def append_user_message(self, user: UserORM, session_id: UUID, prompt: str) -> None:
        session = await self._get_owned_session(user, session_id)
        await self.sessions.append_message(session, _message("user", prompt))

    async def generate_code(self, user: UserORM, session_id: UUID) -> GeneratedCodePayload:
        session = await self._get_owned_session(user, session_id)
        cached = (session.context or {}).get("last_code")
        if cached and cached.get("html"):
            return GeneratedCodePayload(
                html=cached.get("html", ""),
                css=cached.get("css", ""),
                js=cached.get("js", ""),
            )
        prompt = session.messages[-1]["content"] if session.messages else ""
        return await codegen_service.generate_app(prompt)

    async def _get_owned_session(self, user: UserORM, session_id: UUID) -> AgentSessionORM:
        session = await self.sessions.get(session_id)
        if not session or session.user_id != user.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
        return session


async def stream_generation(user: UserORM, session_id: UUID) -> AsyncIterator[str]:
    """Run the multi-agent workflow and emit structured SSE events.

    Runs inside the StreamingResponse body (after the request-scoped DB session
    has closed), so it opens its own session to load the conversation and persist
    the assistant message + generated code at the end.
    """
    async with async_session() as db:
        repo = AgentSessionRepository(db)
        session = await repo.get(session_id)
        if not session or session.user_id != user.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

        prompt = session.messages[-1]["content"] if session.messages else ""
        state: AgentState = {"prompt": prompt}

        try:
            yield AgentEvent(type=AgentEventType.analysis_started, message="开始分析需求").to_sse()
            state.update(await analyze_requirement(state))
            yield AgentEvent(
                type=AgentEventType.analysis_completed,
                message="需求分析完成",
                data={"analysis": state.get("analysis", "")},
            ).to_sse()

            state.update(await plan_structure(state))
            yield AgentEvent(
                type=AgentEventType.structure_planned,
                message="页面结构规划完成",
                data={"structure": state.get("structure", "")},
            ).to_sse()

            yield AgentEvent(type=AgentEventType.code_generating, message="正在生成代码").to_sse()
            state.update(await generate_code_node(state))

            yield AgentEvent(type=AgentEventType.reviewing, message="正在审查代码").to_sse()
            state.update(await review_code_node(state))

            code = state.get("code", {})
            yield AgentEvent(
                type=AgentEventType.completed,
                message="生成完成",
                data={"code": code, "review_notes": state.get("review_notes", [])},
            ).to_sse()

            session.context = {**(session.context or {}), "last_code": code}
            await repo.update(
                session,
                {
                    "context": session.context,
                    "messages": [
                        *session.messages,
                        _message("assistant", state.get("analysis", "生成完成")),
                    ],
                },
            )
        except Exception as exc:  # surface a clean error event to the client
            yield AgentEvent(
                type=AgentEventType.error, message="生成失败", data={"detail": str(exc)}
            ).to_sse()
