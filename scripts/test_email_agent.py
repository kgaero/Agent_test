"""Test script for the email agent."""

import os
from dotenv import load_dotenv
from google.adk.runners import Runner, InMemorySessionService, InMemoryArtifactService, InMemoryMemoryService
from google.genai import types
from src.email_agent import create_email_agent

def run_test():
    """Runs a single-turn test of the email agent."""
    load_dotenv()
    api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GENAI_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY or GENAI_API_KEY not found.")
        return

    agent = create_email_agent()
    runner = Runner(
        app_name="email_agent_test_app",
        agent=agent,
        session_service=InMemorySessionService(),
        artifact_service=InMemoryArtifactService(),
        memory_service=InMemoryMemoryService(),
    )

    user_id = "test-user"
    session_id = "test-session"
    prompt = "Write a short, friendly email to my colleague, Jane, asking for the quarterly report."

    print(f"Testing email_agent with prompt: '{prompt}'")

    message = types.Content(
        role="user",
        parts=[types.Part.from_text(text=prompt)],
    )

    try:
        events = runner.run(
            user_id=user_id,
            session_id=session_id,
            new_message=message,
        )

        response_found = False
        for event in events:
            if event.author == "agent":
                for part in event.content.parts:
                    if part.text:
                        print("\nAgent Response:")
                        print(part.text)
                        response_found = True

        if not response_found:
            print("\nNo response from agent.")

    except Exception as e:
        print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    run_test()