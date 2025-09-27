"""Programmatic runner for ADK evalsets using pytest."""

from __future__ import annotations

import argparse
import asyncio
import inspect
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence

try:
  import pytest
except ModuleNotFoundError as exc:  # pragma: no cover - hard failure
  raise SystemExit(
      "pytest is required to run evalsets. Install it via `pip install pytest`."
  ) from exc

try:
  from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional dependency
  load_dotenv = None  # type: ignore


PKG_ROOT = Path(__file__).resolve().parents[1]
if str(PKG_ROOT) not in sys.path:
  sys.path.insert(0, str(PKG_ROOT))

MODULE_NAME = Path(__file__).stem
sys.modules.setdefault(MODULE_NAME, sys.modules[__name__])
PACKAGE_MODULE_NAME = f"{Path(__file__).parent.name}.{MODULE_NAME}"
sys.modules.setdefault(PACKAGE_MODULE_NAME, sys.modules[__name__])
SRC_PACKAGE_MODULE_NAME = (
    f"{Path(__file__).parent.parent.name}."
    f"{Path(__file__).parent.name}.{MODULE_NAME}"
)
sys.modules.setdefault(SRC_PACKAGE_MODULE_NAME, sys.modules[__name__])

if load_dotenv:
  load_dotenv()


AGENT_MODULE_DEFAULT = "greeting_agent"
AGENT_MODULE: str = AGENT_MODULE_DEFAULT
NUM_RUNS: int = 2
INITIAL_SESSION_FILE: Optional[str] = None
EXECUTION_PATHS: List[Path] = []


@dataclass
class EvalsetResult:
  path: Path
  passed: bool
  details: str


RUN_RESULTS: List[EvalsetResult] = []


class _EvalsetPlugin:
  def __init__(self, evalset_paths: Sequence[Path]):
    self._evalset_paths = list(evalset_paths)
    EXECUTION_PATHS.clear()
    EXECUTION_PATHS.extend(self._evalset_paths)

  def pytest_generate_tests(self, metafunc):
    if "evalset_path" in metafunc.fixturenames:
      metafunc.parametrize("evalset_path", self._evalset_paths)


def _import_agent_evaluator():
  try:
    from google.adk.evaluation.agent_evaluator import AgentEvaluator
  except ModuleNotFoundError as exc:
    missing = exc.name or "dependency"
    raise RuntimeError(
        "google.adk evaluation tooling is missing required dependency: "
        f"{missing}. Install project requirements before running evalsets."
    ) from exc
  return AgentEvaluator


def _record_result(path: Path, passed: bool, details: str) -> None:
  RUN_RESULTS.append(EvalsetResult(path=path, passed=passed, details=details))


def _format_exception(exc: BaseException) -> str:
  return f"{exc.__class__.__name__}: {exc}" if exc else "unknown error"


def _resolve_evalset(path_str: str) -> Path:
  path = Path(path_str).expanduser().resolve()
  if not path.exists():
    raise FileNotFoundError(f"Evalset file not found: {path}")
  if not path.is_file():
    raise IsADirectoryError(f"Evalset path is not a file: {path}")
  return path


@pytest.fixture(scope="module")
def _agent_evaluator():
  try:
    return _import_agent_evaluator()
  except RuntimeError as exc:
    details = _format_exception(exc)
    for path in EXECUTION_PATHS:
      _record_result(path, False, details)
    raise


def test_evalset(evalset_path: Path, _agent_evaluator):
  try:
    evaluation = _agent_evaluator.evaluate(
        agent_module=AGENT_MODULE,
        eval_dataset_file_path_or_dir=str(evalset_path),
        num_runs=NUM_RUNS,
        initial_session_file=INITIAL_SESSION_FILE,
    )
    if inspect.isawaitable(evaluation):
      asyncio.run(evaluation)
  except Exception as exc:  # noqa: BLE001 - pytest needs full stack
    _record_result(evalset_path, False, _format_exception(exc))
    raise
  else:
    _record_result(evalset_path, True, "all criteria satisfied")


def _print_summary(expected: Sequence[Path], results: Sequence[EvalsetResult]) -> None:
  if not expected:
    print("No evalsets provided.")
    return

  by_path: Dict[Path, EvalsetResult] = {res.path: res for res in results}

  name_width = max(len(path.name) for path in expected)
  header = f"{'Evalset':<{name_width}}  Status  Details"
  print("\n" + header)
  print("-" * len(header))
  for path in expected:
    res = by_path.get(path)
    if res:
      status = "PASS" if res.passed else "FAIL"
      details = res.details
    else:
      status = "FAIL"
      details = "not run (see pytest log)"
    print(f"{path.name:<{name_width}}  {status:<5}  {details}")

  passed = sum(1 for res in results if res.passed)
  print(f"\n{passed}/{len(expected)} evalsets passed")


def _parse_args(argv: Optional[Sequence[str]]) -> argparse.Namespace:
  parser = argparse.ArgumentParser(
      description="Execute ADK evalset files with pytest and report pass/fail"
  )
  parser.add_argument(
      "evalsets",
      nargs="+",
      help="Paths to .evalset.json files",
  )
  parser.add_argument(
      "--agent-module",
      default=AGENT_MODULE_DEFAULT,
      help="Python import path to the module exposing root_agent",
  )
  parser.add_argument(
      "--num-runs",
      type=int,
      default=NUM_RUNS,
      help="Number of repeated runs per eval case (default: %(default)s)",
  )
  parser.add_argument(
      "--initial-session",
      type=str,
      default=None,
      help="Optional path to an initial session JSON file",
  )
  parser.add_argument(
      "--fail-fast",
      action="store_true",
      help="Stop after first failing evalset",
  )
  parser.add_argument(
      "--pytest-args",
      nargs=argparse.REMAINDER,
      help=(
          "Additional pytest arguments. Provide them after this flag, e.g."
          " --pytest-args -vv"
      ),
  )
  return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
  args = _parse_args(argv)

  try:
    resolved = [_resolve_evalset(p) for p in args.evalsets]
  except (FileNotFoundError, IsADirectoryError) as exc:
    print(_format_exception(exc))
    return 2

  if args.num_runs <= 0:
    print("--num-runs must be a positive integer")
    return 2

  global AGENT_MODULE, NUM_RUNS, INITIAL_SESSION_FILE
  AGENT_MODULE = args.agent_module
  NUM_RUNS = args.num_runs
  INITIAL_SESSION_FILE = args.initial_session

  EXECUTION_PATHS.clear()
  EXECUTION_PATHS.extend(resolved)
  RUN_RESULTS.clear()

  plugin = _EvalsetPlugin(resolved)

  pytest_args: List[str] = ["-q", str(Path(__file__).resolve())]
  if args.fail_fast:
    pytest_args.append("-x")
  if args.pytest_args:
    pytest_args.extend(args.pytest_args)

  exit_code = pytest.main(pytest_args, plugins=[plugin])
  _print_summary(resolved, RUN_RESULTS)
  return int(exit_code)


if __name__ == "__main__":
  raise SystemExit(main())
