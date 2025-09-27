"""Factory for the time agent."""

from google.adk.agents import LlmAgent
from .tools import get_current_time

DEFAULT_TIME_MODEL = "gemini-2.0-flash"


def create_time_agent(
    *,
    model: str = DEFAULT_TIME_MODEL,
    agent_name: str = "time_agent",
) -> LlmAgent:
  """Builds the time agent configured for Gemini.

  Args:
    model: The Gemini model identifier to invoke via ADK.
    agent_name: Logical name of the agent instance.

  Returns:
    Configured ``LlmAgent`` that displays the current date and time.
  """
  instruction = (
      "You are an agent that displays the current date and time. "
      "Use the `get_current_time` tool to get the current time, and "
      "then display it to the user."
  )

  return LlmAgent(
      name=agent_name,
      model=model,
      description="Displays the current date and time.",
      instruction=instruction,
      tools=[get_current_time],
  )


root_agent = create_time_agent()

__all__ = ["create_time_agent", "root_agent"]