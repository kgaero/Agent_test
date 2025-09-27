import uuid
from typing import Dict, Optional
from src.models import Session, Event

# In-memory store (for demo purposes)
_sessions: Dict[str, Session] = {}

def create_session(app_name: str, user_id: str, initial_state: Optional[Dict] = None) -> Session:
    """Creates a new session and stores it."""
    session_id = str(uuid.uuid4())
    session = Session(
        id=session_id,
        app_name=app_name,
        user_id=user_id,
        state=initial_state or {},
    )
    _sessions[session_id] = session
    return session

def get_session(session_id: str) -> Optional[Session]:
    """Retrieves a session by its ID."""
    return _sessions.get(session_id)

def append_event(session_id: str, event: Event) -> None:
    """Appends an event to a session's history."""
    session = get_session(session_id)
    if session:
        session.events.append(event)

def patch_state(session_id: str, state_patch: Dict) -> None:
    """Updates the state of a session."""
    session = get_session(session_id)
    if session:
        session.state.update(state_patch)