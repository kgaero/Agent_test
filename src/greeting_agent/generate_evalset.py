# generate_evalset.py
# Simple, local generator: runs eval_scripts.json turns through your agent and writes <evalset_id>.evalset.json

from __future__ import annotations

import asyncio
import json
import sys
import uuid
from dotenv import load_dotenv
from importlib import import_module
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# --- make "src" imports work when run as a script ---
PKG_ROOT = Path(__file__).resolve().parents[1]  # .../<repo>/src
if str(PKG_ROOT) not in sys.path:
    sys.path.insert(0, str(PKG_ROOT))

load_dotenv()
# --- your agent (expects root_agent exported in agent.py) ---
from greeting_agent.agent import root_agent as agent  # noqa: E402

# --- ADK runtime ---
from google.adk.runners import Runner  # noqa: E402
from google.adk.sessions import InMemorySessionService  # noqa: E402
from google.genai import types as genai_types  # noqa: E402

# ---------------------------------------------------------------------------
# ADK Eval models: try multiple locations; else fall back to dict builders
# ---------------------------------------------------------------------------

EvalSet = EvalCase = ConversationTurn = Content = Part = None  # type: ignore

def _try_import_models() -> Tuple[Optional[type], Optional[type], Optional[type], Optional[type], Optional[type]]:
    paths = [
        "google.adk.evaluation.eval_models",      # some 1.14.x wheels
        "google.adk.evaluation.models",           # alt
        "google.adk.evaluation.eval_data_models", # older prerelease
        "google.adk.evaluation.data_models",      # another layout seen in the wild
    ]
    for p in paths:
        try:
            m = import_module(p)
            es  = getattr(m, "EvalSet", None)
            ec  = getattr(m, "EvalCase", None)
            ct  = getattr(m, "ConversationTurn", None)
            c   = getattr(m, "Content", None)
            prt = getattr(m, "Part", None)
            if all([es, ec, ct, c, prt]):
                return es, ec, ct, c, prt
        except Exception:
            pass
    return None, None, None, None, None

EvalSet, EvalCase, ConversationTurn, Content, Part = _try_import_models()

USE_MODELS = all([EvalSet, EvalCase, ConversationTurn, Content, Part])

# ---------------------------------------------------------------------------
# IO layout (keep next to this file)
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).parent
TESTS_PATH = SCRIPT_DIR / "eval_scripts.json"
OUTPUT_DIR = SCRIPT_DIR
APP_NAME   = "greeting_agent"


def _new_id(prefix: str, n: int = 6) -> str:
    return f"{prefix}{uuid.uuid4().hex[:n]}"


def _model_dump(obj: Any) -> Dict[str, Any]:
    if hasattr(obj, "model_dump"):
        return obj.model_dump(by_alias=True)
    if hasattr(obj, "dict"):
        return obj.dict(by_alias=True)
    return obj  # already a dict


# -----------------------------
# Builders (models or dicts)
# -----------------------------
def _part_text(text: str):
    if USE_MODELS:
        return Part(text=text)  # type: ignore
    return {"text": text, "inline_data": None, "file_data": None, "function_call": None,
            "function_response": None, "code_execution_result": None, "executable_code": None,
            "video_metadata": None, "thought": None, "thought_signature": None}

def _content_from_text(text: str):
    if USE_MODELS:
        return Content(parts=[_part_text(text)])  # type: ignore
    return {"parts": [_part_text(text)]}

def _turn(user_text: str, assistant_text: str):
    if USE_MODELS:
        return ConversationTurn(  # type: ignore
            user_content=_content_from_text(user_text),
            final_response=_content_from_text(assistant_text),
            role="user",
        )
    return {
        "user_content": _content_from_text(user_text),
        "final_response": _content_from_text(assistant_text),
        "role": "user",
    }

def _case(case_id: str, turns: List[Dict[str, str]]):
    if USE_MODELS:
        return EvalCase(  # type: ignore
            eval_id=case_id,
            conversation=[_turn(t["user_text"], t["assistant_text"]) for t in turns],
        )
    return {
        "eval_id": case_id,
        "conversation": [_turn(t["user_text"], t["assistant_text"]) for t in turns],
    }

def _evalset(cases: List[Any], name: Optional[str] = None):
    eid = _new_id("evalset")
    if USE_MODELS:
        return EvalSet(  # type: ignore
            eval_set_id=eid,
            name=name or "generated",
            description=None,
            eval_cases=cases,
        )
    return {
        "eval_set_id": eid,
        "name": name or "generated",
        "description": None,
        "eval_cases": cases,
    }


# --------------------------------
# Helpers to talk to the runner
# --------------------------------
def _content_first_text(content: Any) -> Optional[str]:
    if content is None:
        return None
    parts = getattr(content, "parts", None)
    if parts is None and isinstance(content, dict):
        parts = content.get("parts")
    if not parts:
        return None
    for part in parts:
        text = getattr(part, "text", None)
        if text is None and isinstance(part, dict):
            text = part.get("text")
        if isinstance(text, str) and text.strip():
            return text
    return None


def _extract_assistant_text(event: Any) -> Optional[str]:
    if event is None:
        return None

    maybe = _content_first_text(event)
    if maybe:
        return maybe

    if hasattr(event, "content"):
        maybe = _content_first_text(getattr(event, "content"))
        if maybe:
            return maybe

    if hasattr(event, "model_dump"):
        try:
            dumped = event.model_dump()
        except Exception:
            dumped = None
        else:
            maybe = _extract_assistant_text(dumped)
            if maybe:
                return maybe

    if isinstance(event, dict):
        maybe = _content_first_text(event.get("content"))
        if maybe:
            return maybe

        paths = [
            ("final_response", "parts", 0, "text"),
            ("response", "text"),
            ("assistant", "text"),
            ("message", "content", 0, "text"),
        ]
        for path in paths:
            cur: Any = event
            try:
                for p in path:
                    cur = cur[p]
                if isinstance(cur, str) and cur.strip():
                    return cur
            except Exception:
                continue
        for value in event.values():
            if isinstance(value, dict):
                text = value.get("text")
                if isinstance(text, str) and text.strip():
                    return text
    return None


def _user_message(text: str) -> genai_types.Content:
    return genai_types.Content(
        role="user",
        parts=[genai_types.Part(text=text)],
    )


async def _run_turns(runner: Runner, user_id: str, session_id: str, turns: List[str]) -> List[Dict[str, str]]:
    out: List[Dict[str, str]] = []
    for text in turns:
        assistant_text: Optional[str] = None
        message = _user_message(text)
        async for ev in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=message,
        ):
            maybe = _extract_assistant_text(ev)
            if maybe:
                assistant_text = maybe
        out.append({"user_text": text, "assistant_text": assistant_text or ""})
    return out


def _load_tests(path: Path) -> List[Dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("eval_scripts.json must be a JSON array of objects with {id, turns[]}.")
    results: List[Dict[str, Any]] = []
    for item in data:
        cid = item.get("id") or _new_id("case")
        turns = item.get("turns") or []
        results.append({"id": str(cid), "turns": [str(t) for t in turns]})
    return results


async def _main() -> Path:
    # Services
    session_service = InMemorySessionService()
    runner = Runner(
        app_name=APP_NAME,
        agent=agent,
        session_service=session_service,
    )

    # Load test scripts
    tests = _load_tests(TESTS_PATH)

    cases: List[Any] = []
    for t in tests:
        user_id = f"user_{uuid.uuid4().hex[:8]}"
        session_id = f"sess_{uuid.uuid4().hex[:8]}"

        # Register session (different ADK versions have different arg names)
        try:
            session_service.create_session(
                app_name=APP_NAME,
                user_id=user_id,
                session_id=session_id,
            )
        except TypeError:
            try:
                session_service.create_session(
                    session_id=session_id,
                    root_agent=agent,
                    app_name=APP_NAME,
                )
            except TypeError:
                try:
                    session_service.create_session(
                        session_id=session_id,
                        agent=agent,
                        app_name=APP_NAME,
                    )
                except TypeError:
                    session_service.create_session(session_id, agent)  # very old signature

        events = await _run_turns(runner, user_id, session_id, t["turns"])
        cases.append(_case(t["id"], events))

    es = _evalset(cases, name=f"{APP_NAME}-generated")
    payload = _model_dump(es)

    out_path = OUTPUT_DIR / f'{payload.get("eval_set_id", _new_id("evalset"))}.evalset.json'
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        "Wrote:", out_path,
        "(models:", "ok" if USE_MODELS else "fallback-dict", ")"
    )
    return out_path


if __name__ == "__main__":
    asyncio.run(_main())

