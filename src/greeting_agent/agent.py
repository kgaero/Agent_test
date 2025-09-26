"""Factory for the greeting LLM agent."""

from __future__ import annotations

from typing import Optional

from google.adk.agents import LlmAgent

DEFAULT_GREETING_MODEL = "gemini-2.0-flash"


def create_greeting_agent(
    *,
    model: str = DEFAULT_GREETING_MODEL,
    agent_name: str = "greeting_agent",
    instruction_override: Optional[str] = None,
) -> LlmAgent:
  """Builds the greeting agent configured for Gemini.

  Args:
    model: The Gemini model identifier to invoke via ADK.
    agent_name: Logical name of the agent instance.
    instruction_override: Optional custom instruction to replace the default.

  Returns:
    Configured ``LlmAgent`` that asks for the user's name and greets them.
  """
  instruction = instruction_override or (
      "You are a friendly assistant. If you do not yet know the user's name, "
      "ask for it politely. Once you learn the name, greet the user by name and "
      "end the conversation after the greeting."
  )

  return LlmAgent(
      name=agent_name,
      model=model,
      description="Collects the user's name and replies with a personalized greeting.",
      instruction=instruction,
  )
root_agent = create_greeting_agent()

__all__ = ["create_greeting_agent", "root_agent"]
