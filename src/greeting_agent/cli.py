"""Console runner for the hobby poem agent."""

from __future__ import annotations

import os
from typing import Generator, Iterable

from dotenv import load_dotenv
from google.adk.events import Event
from google.adk.runners import InMemoryArtifactService
from google.adk.runners import InMemoryMemoryService
from google.adk.runners import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types

from .agent import create_greeting_agent

_EXIT_COMMANDS = {"exit", "quit"}
_DEFAULT_APP_NAME = "greeting_agent_app"


def _ensure_api_key() -> str:
  """Fetches the Gemini API key and raises if it is missing."""
  api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GENAI_API_KEY")
  if not api_key:
    raise RuntimeError(
        "Set GOOGLE_API_KEY or GENAI_API_KEY before running the hobby poem agent."
    )
  return api_key


def _content_to_text(content: types.Content | None) -> str:
  if not content or not content.parts:
    return ""
  texts = [part.text for part in content.parts if getattr(part, "text", None)]
  return " ".join(filter(None, texts))


def _stream_agent_responses(events: Iterable[Event]) -> Generator[str, None, None]:
  buffer: list[str] = []
  for event in events:
    if event.author == "user":
      continue
    text = _content_to_text(event.content)
    if not text:
      continue
    buffer.append(text)
    if event.partial:
      continue
    yield " ".join(buffer)
    buffer.clear()


def run_cli() -> None:
  """Starts the hobby poem agent in an interactive console loop."""
  load_dotenv()
  _ensure_api_key()

  agent = create_greeting_agent()
  runner = Runner(
      app_name=_DEFAULT_APP_NAME,
      agent=agent,
      session_service=InMemorySessionService(),
      artifact_service=InMemoryArtifactService(),
      memory_service=InMemoryMemoryService(),
  )

  user_id = "local-user"
  session_id = "local-session"

  print("Hobby poem agent ready. Tell me your hobby! Type 'exit' to quit.")
  try:
    while True:
      try:
        user_input = input("You: ").strip()
      except EOFError:
        print()
        break

      if not user_input:
        continue

      if user_input.lower() in _EXIT_COMMANDS:
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
      except Exception as exc:  # pragma: no cover - linting requires explicit logging.
        print(f"Agent error: {exc}")
        break

      for response in _stream_agent_responses(events):
        print(f"Agent: {response}")
  except KeyboardInterrupt:
    print()  # Keeps console output tidy on Ctrl+C.
  finally:
    runner.close_session(user_id=user_id, session_id=session_id)


if __name__ == "__main__":
  run_cli()
