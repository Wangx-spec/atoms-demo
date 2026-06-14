from enum import StrEnum
from typing import Any

from pydantic import BaseModel


class AgentEventType(StrEnum):
    analysis_started = "analysis_started"
    analysis_completed = "analysis_completed"
    structure_planned = "structure_planned"
    code_generating = "code_generating"
    reviewing = "reviewing"
    completed = "completed"
    error = "error"


class AgentEvent(BaseModel):
    type: AgentEventType
    message: str = ""
    data: dict[str, Any] | None = None

    def to_sse(self) -> str:
        payload = self.model_dump_json()
        return f"event: {self.type.value}\ndata: {payload}\n\n"
