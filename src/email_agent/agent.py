"""Factory for the email generation LLM agent."""

from __future__ import annotations

from typing import Optional

from google.adk.agents import LlmAgent
from pydantic import BaseModel


class Email(BaseModel):
  """A professional email."""
  subject: str
  body: str

DEFAULT_EMAIL_MODEL = "gemini-2.0-flash"


def create_email_agent(
    *,
    model: str = DEFAULT_EMAIL_MODEL,
    agent_name: str = "email_agent",
    instruction_override: Optional[str] = None,
) -> LlmAgent:
  """Builds the email agent configured for Gemini.

  Args:
    model: The Gemini model identifier to invoke via ADK.
    agent_name: Logical name of the agent instance.
    instruction_override: Optional custom instruction to replace the default.

  Returns:
    Configured ``LlmAgent`` that generates an email based on user's request.
  """
  instruction = instruction_override or (
      "You are an Email Generation Assistant.\n"
      "Your task is to generate a professional email based on the user's request.\n\n"
      "GUIDELINES:\n"
      "- Create an appropriate subject line (concise and relevant)\n"
      "- Write a well-structured email body with:\n"
      "    * Professional greeting\n"
      "    * Clear and concise main content\n"
      "    * Appropriate closing\n"
      "    * Your name as signature\n"
      "- Suggest relevant attachments if applicable (empty list if none needed)\n"
      "- Email tone should match the purpose (formal for business, friendly for colleagues)\n"
      "- Keep emails concise but complete\n\n"
      "IMPORTANT: Your response MUST be valid JSON matching this structure:\n"
      "{\n"
      '    "subject": "Subject line here",\n'
      '    "body": "Email body here with proper paragraphs and formatting"\n'
      "}\n\n"
      "DO NOT include any explanations or additional text outside the JSON response."
  )

  return LlmAgent(
      name=agent_name,
      model=model,
      description=(
          "Generates a professional email based on the user's request."
      ),
      instruction=instruction,
      output_key="email",
  )


root_agent = create_email_agent()

__all__ = ["create_email_agent", "root_agent", "Email"]