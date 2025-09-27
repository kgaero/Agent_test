"""Data models for the Q&A Agent demo."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Union
import datetime
import uuid


@dataclass
class UserMessage:
    """A message from the user."""

    content: str
    role: Literal["user"] = "user"


@dataclass
class AgentMessage:
    """A message from the agent."""

    content: str
    role: Literal["agent"] = "agent"


@dataclass
class ToolCall:
    """A tool call from the agent."""

    name: str
    args: Dict[str, Any]
    role: Literal["tool_call"] = "tool_call"


@dataclass
class ToolResult:
    """The result of a tool call."""

    tool_name: str
    result: Any
    role: Literal["tool_result"] = "tool_result"


Event = Union[UserMessage, AgentMessage, ToolCall, ToolResult]


@dataclass
class Session:
    """Represents a session with a user."""

    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    app_name: str = "qna-demo"
    user_id: str = "anonymous"
    state: Dict[str, Any] = field(default_factory=dict)
    events: List[Event] = field(default_factory=list)
    last_updated: datetime.datetime = field(
        default_factory=lambda: datetime.datetime.now(datetime.UTC)
    )