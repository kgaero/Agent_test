import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.models import Session
from src.qa_agent.agent import QAAgent

class TestQAAgent(unittest.TestCase):
    """
    Unit tests for the QAAgent.
    """

    @patch('src.qa_agent.agent.genai.GenerativeModel')
    def test_agent_reads_from_session_state(self, mock_generative_model):
        """
        Verifies that the agent can read from the session state
        without making a network call.
        """
        # Arrange
        # Mock the LLM to ensure it's not called
        mock_model_instance = MagicMock()
        mock_generative_model.return_value = mock_model_instance

        # Create a session with a specific state
        session = Session(
            id="test-session-123",
            app_name="test_app",
            user_id="test-user",
            state={
                "username": "Alex",
                "preferences": {"favorite_tv_show": "The Office"}
            }
        )

        agent = QAAgent()
        prompt = "What is my favorite tv show?"

        # Act
        reply = agent.handle(prompt, session)

        # Assert
        self.assertEqual(reply, "Alex's favorite TV show is The Office.")

        # Verify that the LLM was not called
        mock_model_instance.generate_content.assert_not_called()

if __name__ == '__main__':
    unittest.main()