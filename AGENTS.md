# AGENTS.md

> **If you read this file, prepend all replies with:** `Read the AGENTS.md`

## What this file is

Agent-facing instructions for working in this repo (different from the human README).
**Stack:** Python for code, **Google Agent Development Kit (ADK)** for agent scaffolding, **Gemini** for LLM calls.

**Hard rule:** Before every LLM or tool call, **read and honor `llms-full.txt`**. Do **not** modify it.
**Hard rule:** Before writing docs, **read and honor `Doc_Spec.md`**. Do **not** modify it.

---

## Quick Start (TL;DR)

1. **Read policy files**

   * Apply **all** rules in `llms-full.txt` (models, params, safety, rate limits) **before every call**.
   * For any docs work, follow `Doc_Spec.md` structure & lifecycle.

2. **Create env + install deps**

   * **Windows (PowerShell)**

     ```powershell
     python -m venv .venv
     . .\.venv\Scripts\Activate.ps1
     pip install -r requirements.txt
     ```
   * **macOS / Linux**

     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     pip install -r requirements.txt
     ```
   * **Cursor/VS Code tip:** Ctrl+Shift+P → **Python: Select Interpreter** → pick the `.venv` interpreter.

3. **Create `.env` (first run)**

   * In the repo **root**, add a file named `.env` with:

     ```bash
     GOOGLE_GENAI_USE_VERTEXAI=FALSE
     GOOGLE_API_KEY=???
     ```
   * Then complete **Setting Up API Keys** below and replace `???` with your real key.

4. **(Optional) Start ADK dev UI / API**

   ```bash
   export SSL_CERT_FILE=$(python -m certifi)  # one-time for voice/video certs
   adk web            # opens http://localhost:8000
   # or:
   adk api_server
   # Windows reload workaround if needed:
   # adk web --no-reload
   ```

5. **Format, lint, test**

   ```bash
   ./autoformat.sh
   pytest tests/unittests -q
   ```

6. **Make a small, reviewable change** (see Commit & PR).

---

## Setting Up API Keys

Use the `.env` file present in the root folder for `GOOGLE_API_KEY` keys.

If the `.env` file is **not present** or `GOOGLE_API_KEY` is missing, ask user to follow these steps:

1. Create an account in Google Cloud: [https://cloud.google.com/?hl=en](https://cloud.google.com/?hl=en)
2. Create a **new project**.
3. Visit **AI Studio**: [https://aistudio.google.com/apikey](https://aistudio.google.com/apikey)
4. **Create an API key**.
5. **Assign the key** to your project.
6. **Connect to a billing account**.
7. Open the `.env` file in the repo root and replace the placeholder with your key:

   ```env
   GOOGLE_GENAI_USE_VERTEXAI=FALSE
   GOOGLE_API_KEY=your_api_key_here
   ```

> Keep the `.env` file **out of version control** (see `.gitignore`). Never share keys in issues or PRs.

---

## Setup Details

### Requirements file

Keep dependencies in `requirements.txt` and install with `pip install -r requirements.txt`.

### ADK-aligned project layout (best practice)

Use **one folder per agent**; the folder name is the src/<agent_name> used by local APIs and the dev UI. Keep a strict, deployable layout:

```
root/
	src/					 # Keep source code for agent within this folder or its subfolders
	  <agent_name>/			 # Make folder with Agent name
		__init__.py          # from . import agent
		agent.py             # defines: root_agent = Agent(...)
		requirements.txt     # agent-specific deps only (optional; root already has this file for global installations)
```

**Rules that must hold for deploy/ops ergonomics**

* File **must** be named `agent.py`.
* The exported top-level variable **must** be named `root_agent`.
* Add `__init__.py` and include `from . import agent` so module discovery works.
* Keep folder names short, lowercase, hyphen/underscore free where possible (URLs & CLI paths are derived from them).

### Autoformat / Lint / Type check (pick what this repo uses)

```bash
./autoformat.sh
ruff check src         # or: pylint src
mypy src               # if type checking is enabled
```

### Notes

* For streaming/live tests: store transcriptions as **Events** and audio as **artifacts** referenced by Events.
* Use **Artifacts** (not session state) for any binaries (files/audio/images).
* Streaming tests typically live under `tests/unittests/streaming/` in ADK examples.

---

## How Agents Should Work Here

### Model & Call Policy

* **Before any LLM/tool call**, re-read `llms-full.txt` and apply its directives (model choice, params, safety, rate limits, local test hints). This overrides other guidance when in conflict.

### ADK Usage Policy

* Treat ADK as a **library**. Do **not** modify ADK source or contribute upstream from this repo.
* Use `adk web` / `adk api_server` for **local/manual testing only** (not a production dependency).

### ADK agent layout & naming (best practices)

* **Foldering:** one folder per agent under `src/`. Top-level multi-agent apps can keep a root `src/<root_agent>/agent.py` and nest sub-agents in sibling folders (e.g., `src/search_agent/`, `src/rag_agent/`).
* **File & symbol names (strict):** `agent.py` with a top-level `root_agent`. Avoid renaming; scripts and deploy flows assume these.
* **Agent names:** valid Python identifiers, unique across the tree, and never `"user"`. Use descriptive names that reflect the role; names appear in traces and delegation.

### Tool design (best practices)

* Keep tools **small, focused functions** with minimal, primitive parameters.
* Use meaningful function names & docstrings—tools are surfaced to the model; clarity improves selection.
* Prefer `async def` tools when they call I/O; ADK can parallelize eligible tool calls to reduce latency.
* Return structured results (e.g., dicts with `status`, `data`, `error`) that are easy to reason about and test.

### Session, state & memory hygiene

* Use `session.state` for simple, serializable key/values (e.g., `booking_step`, `current_doc_id`).
* Scope state with clear prefixes or conventions, e.g., transient keys (`temp:*`) for per-invocation scratch.
* **Do not** shove large blobs into state; put binaries in **Artifacts** and reference them from Events or state by ID.

### Prompts & agent config quality

* Write precise `instruction` prompts; include a descriptive `name`/`description`—these help multi-agent delegation.
* For complex systems, consider external **Agent Config** files to declare sub-agents, tools, and wiring. Treat them as source of truth when they exist.
* Use `RunConfig` to cap cost/latency (e.g., `max_llm_calls`), enable streaming, and set tracing verbosity for dev vs. CI.

### Observability & operations

* Use **structured logging**. Default to INFO for normal runs; bump to DEBUG only when troubleshooting.
* Inspect **traces** in the Dev UI to validate reasoning steps, tool calls, and state transitions.
* **Deployment sanity checks:** the `src/<agent>/agent.py` + `root_agent` + `__init__.py` pattern must be intact for packaging and service discovery (e.g., Cloud Run / internal runners).

### Testing & local dev ergonomics

* Use `adk api_server` or `adk web` to iterate locally; paths are derived from the **agent folder name** (keep it clean).
* Add early **evals** (JSON eval sets) that check not just the final answer but also **trajectory/tool use**.
* Keep tests hermetic; mock external I/O where possible. Store golden responses for regressions when appropriate.

### Python Code Style (summary)

* Follow Google/PEP 8 style:

  * 2-space indent (unless repo specifies otherwise), ~80–100 char lines.
  * `snake_case` for functions/vars, `CamelCase` for classes.
  * Public APIs have docstrings; imports are organized/sorted.
  * Catch **specific** exceptions; avoid bare `Exception`.
* Run `./autoformat.sh` before committing.

### Documentation Workflow

* Follow `Doc_Spec.md` for all feature docs:

  * Place specs/progress under `documentation/features/{planned|active|completed}`.
  * Use kebab-case names with `-spec.md` / `-progress.md` suffixes.
  * Move docs through **Planning → Active → Completed**.
* Prefer linking to docs rather than duplicating in this file.

---

## Common Commands (copy–paste)

**Type check**

```bash
mypy src
```

**Format**

```bash
./autoformat.sh
```

**Lint**

```bash
ruff check src
# or
pylint src
```

**Unit tests (fast)**

```bash
pytest tests/unittests -q
```

**Full test suite (CI parity)**

```bash
pytest
```

**Evaluate sample (if applicable)**

```bash
adk eval samples_for_testing/hello_world   samples_for_testing/hello_world/hello_world_eval_set_001.evalset.json
```

**Local dev UI / API**

```bash
export SSL_CERT_FILE=$(python -m certifi)
adk web            # or: adk api_server
```

---

## Project Map (minimal)

* `src/` — **agents live here** (one folder per agent: `src/<agent_name>/agent.py` with `root_agent`)
* `src/` — Python modules (safe to modify per task)
* `scripts/` — automation helpers (keep idempotent)
* `documentation/` — follow **Doc_Spec** structure & templates
* `tests/` — unit/integration/eval tests (`tests/unittests/`, `tests/evals/`, `tests/unittests/streaming/` if used)
* `infra/` — infrastructure (requires human review)

---

## Commit & PR Guidelines

* Use **Conventional Commits**; add `#non-breaking` or `#breaking` flags.
* Keep PRs small/scoped; include repro steps and tests when relevant.
* Ensure format/lint/tests pass locally before opening a PR.

---

## When to Ask for Help / Stop

Stop and request human input when:

* Dependencies or local UI fail to start **after two attempts** (including Windows `--no-reload`).
* Tests repeatedly fail or exceed expected runtime.
* Required credentials/API keys are missing.
* Proceeding would require modifying ADK’s source or repo structure.

---

## Non-Goals

* Do **not** modify or contribute to **Google ADK** upstream from this repo.
* Do **not** duplicate feature docs here; **link** and follow `Doc_Spec.md`.

---

## References

* **`llms-full.txt`** — must read before every call (models/params/safety/testing).
* **`Doc_Spec.md`** — docs structure, naming, lifecycle, templates.
* **`ADK_AGENTS.md`** — setup helper, code style, testing, commits, streaming notes.
* **ADK repo:** [https://github.com/google/adk-python](https://github.com/google/adk-python)

---

### Appendix: ADK as a Dependency (FYI)

ADK is model-agnostic and Python-first. You can compose single/multi-agent systems and test in the built-in dev UI:

```bash
export SSL_CERT_FILE=$(python -m certifi)
adk web   # or: adk api_server
```

**ADK agent structure recap (copy/paste)**

```
src/
  google_search_agent/
    __init__.py      # from . import agent
    agent.py         # defines: root_agent = Agent(...)
    requirements.txt
```

> Keep this file explicit and concise. Update it when commands or docs move. If a subfolder needs special rules, add a scoped `AGENTS.md` there and link it here.
