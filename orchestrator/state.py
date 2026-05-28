from typing import TypedDict, Optional, List, Any, Annotated
from langgraph.graph.message import add_messages


class OrchestratorState(TypedDict):
    task_id: str
    task_type: str
    input: str
    context: Optional[dict]
    output: Optional[str]
    status: str
    error: Optional[str]
    sources: Optional[List[str]]
    messages: Annotated[List[Any], add_messages]
