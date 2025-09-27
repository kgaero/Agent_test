"""Main demo script for the Q&A Agent."""

import os
from dotenv import load_dotenv
from pprint import pprint

from src.qna_agent import create_qna_agent
from src.runner import Runner
import src.session_service as session_service


def main():
    """Runs the main demo flow."""
    load_dotenv()

    # 1. Initialize the agent and runner
    qna_agent = create_qna_agent()
    runner = Runner(agents=[qna_agent])

    # 2. Create a session with initial state
    initial_state = {
        "username": "Brandon",
        "preferences": {"favorite_tv_show": "Game of Thrones"},
    }
    session = session_service.create_session(
        user_id="brandon123", app_name="qna-demo", initial_state=initial_state
    )

    # 3. Send a sample prompt
    prompt = "What is Brandon's favorite TV show?"
    print(f"-> User Prompt: {prompt}\n")

    reply, final_session = runner.run(
        user_id=session.user_id, session_id=session.session_id, user_text=prompt
    )

    # 4. Print the results
    print(f"<- Agent Reply: {reply}\n")
    print("-> Final Session State:")
    pprint(final_session)


if __name__ == "__main__":
    main()