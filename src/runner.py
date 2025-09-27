"""The runner for the Q&A Agent demo."""

from typing import List, Optional

from src.models import Session, UserMessage, AgentMessage
from src.qna_agent import QnAAgent
import src.session_service as session_service


class Runner:
    """Orchestrates the agent and session service."""

    def __init__(self, agents: List[QnAAgent]):
        self._agents = agents

    def run(
        self, user_id: str, session_id: Optional[str], user_text: str
    ) -> (str, Session):
        """Runs the agent and returns the reply and the session."""
        if session_id:
            session = session_service.get_session(session_id)
            if not session:
                raise ValueError(f"Session with ID {session_id} not found.")
        else:
            session = session_service.create_session(
                user_id=user_id, app_name="qna-demo"
            )

        session_service.append_event(
            session.session_id, UserMessage(content=user_text)
        )

        # For this demo, we'll just use the first agent.
        agent = self._agents[0]
        reply = agent.handle(user_text, session)

        session_service.append_event(
            session.session_id, AgentMessage(content=reply)
        )

        return reply, session