"""Factory for the hobby poem LLM agent."""

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
  """Builds the hobby poem agent configured for Gemini.

  Args:
    model: The Gemini model identifier to invoke via ADK.
    agent_name: Logical name of the agent instance.
    instruction_override: Optional custom instruction to replace the default.

  Returns:
    Configured ``LlmAgent`` that asks for the user's hobby and writes a poem.
  """
  instruction = instruction_override or (
      "You are a playful poet who creates short, funny poems about hobbies. "
      "If you do not yet know the user's hobby, ask for it. When a hobby is "
      "provided, gather one or two fun and factual tidbits about that hobby—"
      "you may ask brief follow-up questions if needed. Combine those facts "
      "into a lighthearted poem of 4 to 6 lines that celebrates the hobby, "
      "keeps a cheerful tone, and includes the fun facts explicitly. End the "
      "conversation after sharing the poem."
  )

  return LlmAgent(
      name=agent_name,
      model=model,
      description=(
          "Collects the user's hobby, finds fun facts, and replies with a funny "
          "poem that mentions them."
      ),
      instruction=instruction,
  )


root_agent = create_greeting_agent()

__all__ = ["create_greeting_agent", "root_agent"]
