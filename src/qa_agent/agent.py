import os
import google.generativeai as genai
from dotenv import load_dotenv
from src.models import Session

# Load environment variables from .env file
load_dotenv()

# Configure the generative AI client
api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GENAI_API_KEY")
if not api_key:
    raise ValueError("API key not found. Please set GOOGLE_API_KEY or GENAI_API_KEY in your .env file.")

genai.configure(api_key=api_key)

class QAAgent:
    """A simple Q&A agent that can use session state."""

    def __init__(self, model_name: str = "gemini-pro"):
        self._model = genai.GenerativeModel(model_name)

    def handle(self, message: str, session: Session) -> str:
        """
        Handles a user message, either by using session state or by delegating to an LLM.
        """
        preferences = session.state.get("preferences", {})
        favorite_tv_show = preferences.get("favorite_tv_show")

        if "favorite tv show" in message.lower() and favorite_tv_show:
            username = session.state.get("username", "Their")
            return f"{username}'s favorite TV show is {favorite_tv_show}."

        # Delegate to the LLM
        try:
            response = self._model.generate_content(message)
            return response.text
        except Exception as e:
            # Basic error handling
            return f"An error occurred while contacting the LLM: {e}"

# Create a root agent instance, as expected by ADK.
root_agent = QAAgent()