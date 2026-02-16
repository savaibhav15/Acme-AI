"""State definition for the Acme Dental Agent."""

from typing import TypedDict, Annotated, Sequence, Optional
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """State of the agent conversation."""
    messages: Annotated[Sequence[BaseMessage], add_messages]
    user_name: Optional[str]
    user_email: Optional[str]
    appointment_date: Optional[str]
    appointment_time: Optional[str]
    booking_url: Optional[str]
