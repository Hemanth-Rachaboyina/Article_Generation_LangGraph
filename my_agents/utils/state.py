from typing_extensions import TypedDict
from typing import Annotated, List
from langgraph.graph import add_messages


class State(TypedDict):
    user_query: str
    article: str
    grade: int
    best_score: float
    best_article: str
    justification: str
    suggested_edits: str
    iterations: int
    messages: Annotated[List, add_messages]
    essay: Annotated[List, add_messages]
    # Configurable parameters
    max_iterations: int
    target_score: float
    max_tokens: int