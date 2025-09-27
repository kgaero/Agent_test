"""Unit tests for the Q&A agent."""

import unittest.mock as mock

from src.qna_agent import QnAAgent
from src.models import Session


def test_qna_agent_uses_session_state():
    """Verifies the agent reads from session state without calling the LLM."""
    # 1. Arrange
    mock_llm = mock.Mock()
    agent = QnAAgent(llm=mock_llm)
    session = Session(
        state={
            "username": "TestUser",
            "preferences": {"favorite_tv_show": "The Office"},
        }
    )
    message = "What is my favorite tv show?"

    # 2. Act
    response = agent.handle(message, session)

    # 3. Assert
    assert response == "I remember! TestUser's favorite TV show is The Office."
    mock_llm.generate.assert_not_called()


def test_qna_agent_delegates_to_llm():
    """Verifies the agent delegates to the LLM when session state is not relevant."""
    # 1. Arrange
    mock_llm = mock.Mock()
    mock_llm.generate.return_value.content = "I am a mock LLM."
    agent = QnAAgent(llm=mock_llm)
    session = Session()
    message = "What is the capital of France?"

    # 2. Act
    response = agent.handle(message, session)

    # 3. Assert
    assert response == "I am a mock LLM."
    mock_llm.generate.assert_called_once_with(prompt=message)