"""Factory for the email generation LLM agent."""

from __future__ import annotations

from typing import Optional

from google.adk.agents import LlmAgent
from pydantic import BaseModel, Field

DEFAULT_EMAIL_MODEL = "gemini-2.0-flash"


class EmailOutput(BaseModel):
  """Structured schema for generated email content."""

  subject: str = Field(
      ..., description="Concise subject line summarizing the email's purpose."
  )
  body: str = Field(
      ..., description="Formatted email body containing greeting, message, closing, and signature."
  )


def create_email_generation_agent(
    *,
    model: str = DEFAULT_EMAIL_MODEL,
    agent_name: str = "email_generation_agent",
    instruction_override: Optional[str] = None,
) -> LlmAgent:
  """Builds the email generation agent configured for Gemini models.

  Args:
    model: The Gemini model identifier to invoke via ADK.
    agent_name: Logical name of the agent instance.
    instruction_override: Optional custom instruction to replace the default.

  Returns:
    Configured ``LlmAgent`` that writes professional emails as JSON.
  """
  instruction = instruction_override or (
      "You are an Email Generation Assistant. Follow every user request to craft a "
      "complete, professional email. Reply in valid JSON using this structure: "
      '{"subject": "Subject line here", "body": "Email body here with proper paragraphs and formatting"}. '
      "Observe these requirements for the email body: start with a professional greeting "
      "that fits the context, deliver clear and concise paragraphs for the main message, "
      "close with an appropriate sign-off, and sign as 'Email Generation Assistant'. "
      "Keep the tone aligned with the user's purpose (formal for business, friendly for "
      "colleagues) and keep the message concise yet complete. Include a final paragraph "
      "that begins with 'Suggested attachments:' followed by a JSON-style list (e.g., [] "
      "when no attachments are needed). Do not include any extra commentary or text "
      "outside the JSON object."
  )

  return LlmAgent(
      name=agent_name,
      model=model,
      description=(
          "Generates professional, well-structured emails and returns them as JSON."
      ),
      instruction=instruction,
      output_schema=EmailOutput,
      output_key="email",
  )


root_agent = create_email_generation_agent()

__all__ = ["EmailOutput", "create_email_generation_agent", "root_agent"]
