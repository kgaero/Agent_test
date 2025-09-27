import datetime
from typing import List
from src.models import Session, UserMessage, AgentMessage
from src.session_service import get_session, append_event
from src.qa_agent.agent import QAAgent

class Runner:
    def __init__(self, agents: List[QAAgent], session_service):
        self._agents = agents
        self._session_service = session_service

    def run(self, user_id: str, session_id: str, user_text: str) -> str:
        """
        Runs the agent for a user and session.
        """
        # Fetch the session
        session = self._session_service.get_session(session_id)
        if not session:
            raise ValueError(f"Session with ID '{session_id}' not found.")

        # Append the user message to the session
        self._session_service.append_event(session_id, UserMessage(content=user_text))

        # Choose an agent (simple routing for now)
        agent = self._agents[0]

        # Invoke the agent
        reply_text = agent.handle(user_text, session)

        # Append the agent message to the session
        self._session_service.append_event(session_id, AgentMessage(content=reply_text))

        # Update the session's timestamp
        session.last_updated = datetime.datetime.utcnow()

        return reply_text