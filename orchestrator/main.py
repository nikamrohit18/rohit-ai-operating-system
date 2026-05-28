from langgraph.graph import StateGraph, START, END
from orchestrator.state import OrchestratorState
from orchestrator.router import route_task
from agents.research.agent import run as research_run
from agents.content.agent import run as content_run
from agents.seo.agent import run as seo_run
from agents.digital_twin.agent import run as digital_twin_run
from agents.social.agent import run as social_run
from agents.youtube.agent import run as youtube_run

_ALL_NODES = ("research", "content", "seo", "digital_twin", "social", "youtube")


def build_graph():
    graph = StateGraph(OrchestratorState)

    graph.add_node("research", research_run)
    graph.add_node("content", content_run)
    graph.add_node("seo", seo_run)
    graph.add_node("digital_twin", digital_twin_run)
    graph.add_node("social", social_run)
    graph.add_node("youtube", youtube_run)

    graph.add_conditional_edges(
        START,
        route_task,
        {node: node for node in _ALL_NODES},
    )

    for node in _ALL_NODES:
        graph.add_edge(node, END)

    return graph.compile()


orchestrator = build_graph()
