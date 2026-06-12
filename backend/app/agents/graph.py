from app.agents.nodes import analyze_requirement, generate_code_node, review_code_node
from app.agents.state import AgentState


async def run_mock_agent_graph(prompt: str) -> AgentState:
    state: AgentState = {"prompt": prompt}
    state = await analyze_requirement(state)
    state = await generate_code_node(state)
    return await review_code_node(state)
