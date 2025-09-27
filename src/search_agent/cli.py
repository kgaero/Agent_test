"""Console runner for the search agent."""

from __future__ import annotations

import asyncio
import os
from typing import AsyncGenerator, AsyncIterable

from dotenv import load_dotenv
from google.adk.events import Event
from google.adk.runners import InMemoryRunner
from google.genai import types

from .agent import create_search_agent

_EXIT_COMMANDS = {"exit", "quit"}
_DEFAULT_APP_NAME = "search_agent_app"


def _ensure_api_key() -> str:
  """Fetches the Gemini API key and raises if it is missing."""
  api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GENAI_API_KEY")
  if not api_key:
    raise RuntimeError(
        "Set GOOGLE_API_KEY or GENAI_API_KEY before running the search agent."
    )
  return api_key


def _content_to_text(content: types.Content | None) -> str:
  if not content or not content.parts:
    return ""
  texts = [part.text for part in content.parts if getattr(part, "text", None)]
  return " ".join(filter(None, texts))


async def _stream_agent_responses(
    events: AsyncIterable[Event],
) -> AsyncGenerator[str, None]:
  buffer: list[str] = []
  async for event in events:
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


async def run_cli() -> None:
  """Starts the search agent in an interactive console loop."""
  load_dotenv()
  _ensure_api_key()

  agent = create_search_agent()
  runner = InMemoryRunner(
      app_name=_DEFAULT_APP_NAME,
      agent=agent,
  )

  user_id = "local-user"
  session_id = "local-session"

  await runner.session_service.create_session(
      app_name=_DEFAULT_APP_NAME, user_id=user_id, session_id=session_id
  )

  print("Search agent ready. Ask me to search for something! Type 'exit' to quit.")
  try:
    while True:
      try:
        user_input = await asyncio.to_thread(input, "You: ")
        user_input = user_input.strip()
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
        events = runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=message,
        )
        async for response in _stream_agent_responses(events):
          print(f"Agent: {response}")

      except Exception as exc:  # pragma: no cover - linting requires explicit logging.
        print(f"Agent error: {exc}")
        break

  except KeyboardInterrupt:
    print()  # Keeps console output tidy on Ctrl+C.
  finally:
    await runner.session_service.delete_session(
        app_name=_DEFAULT_APP_NAME, user_id=user_id, session_id=session_id
    )


if __name__ == "__main__":
  asyncio.run(run_cli())