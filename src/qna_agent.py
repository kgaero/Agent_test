"""A simple Q&A agent that can access session state."""

from src.models import Session
from google.adk.agents import LlmAgent
import os


class QnAAgent:
    """A Q&A agent that can access session state."""

    def __init__(self, llm: LlmAgent):
        self._llm = llm

    def handle(self, message: str, session: Session) -> str:
        """Handles a user message, potentially using session state."""
        if "favorite tv show" in message.lower():
            username = session.state.get("username", "user")
            favorite_show = session.state.get("preferences", {}).get(
                "favorite_tv_show"
            )
            if favorite_show:
                return (
                    f"I remember! {username}'s favorite TV show is {favorite_show}."
                )

        # If the information is not in the session, delegate to the LLM.
        return self._llm.generate(prompt=message).content


def create_qna_agent() -> QnAAgent:
    """Creates a Q&A agent with a default LLM."""
    llm = LlmAgent(
        name="qna_llm",
        model="gemini-1.5-flash",
    )
    return QnAAgent(llm=llm)