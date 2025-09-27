"""Console runner for the email agent."""

from __future__ import annotations

import os
import asyncio
import json

from dotenv import load_dotenv
from google.adk.events import Event
from google.adk.runners import InMemoryArtifactService
from google.adk.runners import InMemoryMemoryService
from google.adk.runners import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types
from pydantic import ValidationError

from .agent import create_email_agent, Email


def _ensure_api_key() -> str:
  """Fetches the Gemini API key and raises if it is missing."""
  api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GENAI_API_KEY")
  if not api_key:
    raise RuntimeError(
        "Set GOOGLE_API_KEY or GENAI_API_KEY before running the email agent."
    )
  return api_key


def run_cli() -> None:
  """Starts the email agent in an interactive console loop."""
  load_dotenv()
  _ensure_api_key()

  agent = create_email_agent()
  session_service = InMemorySessionService()
  runner = Runner(
      app_name="email_agent_app",
      agent=agent,
      session_service=session_service,
      artifact_service=InMemoryArtifactService(),
      memory_service=InMemoryMemoryService(),
  )

  user_id = "local-user"
  session_id = "local-session"

  # Explicitly create the session
  asyncio.run(session_service.create_session(
      app_name="email_agent_app",
      user_id=user_id,
      session_id=session_id
  ))

  print("Email agent ready. Tell me what email to write! Type 'exit' to quit.")
  try:
    while True:
      try:
        user_input = input("You: ").strip()
      except EOFError:
        print()
        break

      if not user_input:
        continue

      if user_input.lower() in {"exit", "quit"}:
        print("Agent: Goodbye!")
        break

      message = types.Content(
          role="user",
          parts=[types.Part.from_text(text=user_input)],
      )

      try:
        events = runner.run(
            user_id=user_id,
            session_id=session_id,
            new_message=message,
        )
        for event in events:
          if event.author == "agent" and event.content and event.content.parts:
              try:
                  text_content = event.content.parts[0].text.strip()
                  if text_content.startswith("```json"):
                      text_content = text_content[7:-3].strip()

                  email_dict = json.loads(text_content)
                  email = Email(**email_dict)
                  print("\n--- Generated Email (Validated) ---")
                  print(f"Subject: {email.subject}")
                  print("\nBody:")
                  print(email.body)
                  print("-------------------------------------\n")
              except (json.JSONDecodeError, ValidationError, IndexError) as e:
                  print(f"\n--- Error parsing agent response: {e} ---")
                  if event.content and event.content.parts:
                      print("--- Agent Raw Response ---")
                      print(event.content.parts[0].text)
                      print("--------------------------\n")

      except Exception as exc:
        print(f"Agent error: {exc}")
        break
  except KeyboardInterrupt:
    print()
  finally:
    pass


if __name__ == "__main__":
  run_cli()