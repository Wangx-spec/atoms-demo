"""LangGraph workflow assembling the agent nodes.

If LangGraph is unavailable, fall back to a sequential async pipeline that runs
the same node functions, so the system degrades gracefully.
"""
from __future__ import annotations

from app.agents.nodes import (
    analyze_requirement,
    fix_optimize_node,
    generate_code_node,
    plan_structure,
    review_code_node,
)
from app.agents.state import AgentState

# Ordered pipeline shared by both the LangGraph build and the fallback runner.
PIPELINE = [
    ("analyze", analyze_requirement),
    ("plan", plan_structure),
    ("generate", generate_code_node),
    ("review", review_code_node),
    ("fix", fix_optimize_node),
]


def build_graph():
    """Build a compiled LangGraph StateGraph for the generation workflow."""
    from langgraph.graph import END, START, StateGraph

    builder = StateGraph(AgentState)
    for name, fn in PIPELINE:
        builder.add_node(name, fn)

    builder.add_edge(START, "analyze")
    builder.add_edge("analyze", "plan")
    builder.add_edge("plan", "generate")
    builder.add_edge("generate", "review")
    builder.add_edge("review", "fix")
    builder.add_edge("fix", END)
    return builder.compile()


async def run_agent_graph(prompt: str) -> AgentState:
    state: AgentState = {"prompt": prompt}
    try:
        graph = build_graph()
        return await graph.ainvoke(state)
    except Exception:
        # Fallback: run the same nodes sequentially.
        for _, fn in PIPELINE:
            state.update(await fn(state))
        return state
