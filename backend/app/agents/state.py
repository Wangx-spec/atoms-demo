from typing import TypedDict


class AgentState(TypedDict, total=False):
    prompt: str
    analysis: str
    code: dict[str, str]
    review_notes: list[str]
