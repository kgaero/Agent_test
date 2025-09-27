from dataclasses import dataclass, field
from typing import Dict, List, Union
import datetime

@dataclass
class UserMessage:
    role: str = "user"
    content: str = ""

@dataclass
class AgentMessage:
    role: str = "agent"
    content: str = ""

@dataclass
class ToolCall:
    # Stub for future use
    pass

@dataclass
class ToolResult:
    # Stub for future use
    pass

Event = Union[UserMessage, AgentMessage, ToolCall, ToolResult]

@dataclass
class Session:
    id: str
    app_name: str
    user_id: str
    state: Dict = field(default_factory=dict)
    events: List[Event] = field(default_factory=list)
    last_updated: datetime.datetime = field(default_factory=datetime.datetime.utcnow)