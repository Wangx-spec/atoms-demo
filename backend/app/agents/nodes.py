"""Agent workflow nodes.

Each node is an async function ``(AgentState) -> partial AgentState`` so it can be
used both inside a LangGraph StateGraph and by the streaming orchestrator in
``agent_service`` (which emits structured SSE events around each node).
"""
from __future__ import annotations

from app.agents.state import AgentState
from app.services.codegen_service import codegen_service
from app.services.llm_service import get_llm_provider

ANALYST_SYSTEM = "你是一名资深产品经理，请用简洁中文分析用户的应用需求，列出核心功能点。"
ARCHITECT_SYSTEM = "你是一名前端架构师，请规划单页应用的页面结构与主要区块，用简洁中文分点描述。"
REVIEWER_SYSTEM = "你是一名前端代码审查员，请指出 HTML/CSS/JS 代码可能的问题，用简短中文分点列出；若无明显问题回复“通过”。"


async def analyze_requirement(state: AgentState) -> AgentState:
    provider = get_llm_provider()
    analysis = await provider.complete(state.get("prompt", ""), system=ANALYST_SYSTEM)
    return {"analysis": analysis}


async def plan_structure(state: AgentState) -> AgentState:
    provider = get_llm_provider()
    prompt = f"需求：{state.get('prompt', '')}\n需求分析：{state.get('analysis', '')}"
    structure = await provider.complete(prompt, system=ARCHITECT_SYSTEM)
    return {"structure": structure}


async def generate_code_node(state: AgentState) -> AgentState:
    code = await codegen_service.generate_app(
        prompt=state.get("prompt", ""),
        analysis=state.get("analysis"),
        structure=state.get("structure"),
    )
    return {"code": {"html": code.html, "css": code.css, "js": code.js}}


async def review_code_node(state: AgentState) -> AgentState:
    provider = get_llm_provider()
    code = state.get("code", {})
    snippet = f"HTML:\n{code.get('html', '')[:2000]}\n\nCSS:\n{code.get('css', '')[:1000]}"
    notes = await provider.complete(snippet, system=REVIEWER_SYSTEM)
    return {"review_notes": [line.strip() for line in notes.splitlines() if line.strip()]}


async def fix_optimize_node(state: AgentState) -> AgentState:
    """Ensure the generated code is non-empty; regenerate once if it is missing."""
    code = state.get("code") or {}
    if code.get("html"):
        return {"code": code}
    regenerated = await codegen_service.generate_app(prompt=state.get("prompt", ""))
    return {"code": {"html": regenerated.html, "css": regenerated.css, "js": regenerated.js}}
