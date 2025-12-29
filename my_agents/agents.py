from langgraph.graph import StateGraph
from backend.my_agents.utils.state import State
from backend.my_agents.utils.nodes import (
    writer,
    grader,
    suggestion_provider,
    changer,
    routerfunction,
)

from langgraph.graph import StateGraph, START, END, add_messages

graph = StateGraph(State)

graph.add_node(writer, "writer")
graph.add_node(grader, "grader")
graph.add_node(suggestion_provider, "suggestion_provider")
graph.add_node(changer, "changer")


graph.add_edge(START, "writer")
graph.add_edge("writer", "grader")
graph.add_conditional_edges(
    "grader", routerfunction, {"suggestion_provider": "suggestion_provider", "end": END}
)
graph.add_edge("suggestion_provider", "changer")
graph.add_edge("changer", "grader")

workflow = graph.compile()
