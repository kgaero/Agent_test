import os
from pprint import pprint
from dotenv import load_dotenv

# Set the python path to include the src directory
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from src.models import Session, UserMessage, AgentMessage
from src.session_service import create_session, get_session
from src.qa_agent.agent import QAAgent
from src.runner import Runner
import src.session_service as session_service

def main():
    """
    A simple demo to showcase the Q&A agent and session management.
    """
    # Load environment variables
    load_dotenv()

    # 1. Initialize services and agents
    qa_agent = QAAgent()
    runner = Runner(agents=[qa_agent], session_service=session_service)

    # 2. Create a session with initial state
    initial_state = {
        "username": "Brandon",
        "preferences": {"favorite_tv_show": "Game of Thrones"}
    }
    session = create_session(app_name="qa_demo", user_id="user123", initial_state=initial_state)
    print(f"Session created with ID: {session.id}\n")

    # 3. Send a sample prompt
    prompt = "What is Brandon's favorite TV show?"
    print(f"User Prompt: {prompt}\n")

    # 4. Run the agent
    final_reply = runner.run(user_id="user123", session_id=session.id, user_text=prompt)

    # 5. Print the results
    print(f"Agent Reply: {final_reply}\n")

    # 6. Print the session snapshot
    updated_session = get_session(session.id)
    print("--- Session Snapshot ---")
    print("State:")
    pprint(updated_session.state)
    print("\nLast Event:")
    pprint(updated_session.events[-1])
    print("------------------------")

if __name__ == "__main__":
    main()