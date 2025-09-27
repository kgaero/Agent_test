"""Factory for the search agent."""

from google.adk.agents import LlmAgent
from google.adk.tools.google_search_tool import google_search

DEFAULT_SEARCH_MODEL = "gemini-2.0-flash"


def create_search_agent(
    *,
    model: str = DEFAULT_SEARCH_MODEL,
    agent_name: str = "search_agent",
) -> LlmAgent:
  """Builds the search agent configured for Gemini.

  Args:
    model: The Gemini model identifier to invoke via ADK.
    agent_name: Logical name of the agent instance.

  Returns:
    Configured ``LlmAgent`` that uses the search tool to answer questions.
  """
  instruction = (
      "You are a helpful assistant that uses Google Search to answer user "
      "questions. When the user asks a question, use the `google_search` tool "
      "to find an answer and then respond to the user."
  )

  return LlmAgent(
      name=agent_name,
      model=model,
      description="Uses Google Search to answer user questions.",
      instruction=instruction,
      tools=[google_search],
  )


root_agent = create_search_agent()

__all__ = ["create_search_agent", "root_agent"]