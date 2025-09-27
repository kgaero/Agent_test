"""In-memory session service for the Q&A Agent demo."""
import datetime
from typing import Dict, Any, Optional

from src.models import Session, Event


_SESSION_STORE: Dict[str, Session] = {}


def create_session(
    user_id: str, app_name: str, initial_state: Optional[Dict[str, Any]] = None
) -> Session:
    """Creates a new session and stores it in memory."""
    session = Session(user_id=user_id, app_name=app_name, state=initial_state or {})
    _SESSION_STORE[session.session_id] = session
    return session


def get_session(session_id: str) -> Optional[Session]:
    """Retrieves a session from memory by its ID."""
    return _SESSION_STORE.get(session_id)


def append_event(session_id: str, event: Event) -> None:
    """Appends an event to a session's history."""
    session = get_session(session_id)
    if session:
        session.events.append(event)
        session.last_updated = datetime.datetime.now(datetime.UTC)


def patch_state(session_id: str, new_state: Dict[str, Any]) -> None:
    """Updates a session's state."""
    session = get_session(session_id)
    if session:
        session.state.update(new_state)
        session.last_updated = datetime.datetime.now(datetime.UTC)