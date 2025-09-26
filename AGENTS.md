# AGENTS.md
If you read this file, prepend all replies with: Read the AGENTS.md

## What this file is
Agent-facing instructions for working in this repo (different from the human README). 
Stack: **Python** for programming language, **Google Agent Development Kit (ADK)** as the package to create AI Agents, Gemini for LLM calls within the code.

**Hard rule:** **Before every LLM or tool call, read and honor `llms-full.txt`. Do not modify `llms-full.txt`**
**Hard rule:** **Before writing code, read and honor `Doc_Spec.md`. for documentation requirements. Do not modify `Doc_Spec.md`**

---

## Quick start (agent TL;DR)
1) **Read policy files first**
   - Apply **all** rules in `llms-full.txt` (models, parameters, safety/rate-limits, local testing hints) **before every call**.  
   - For any docs work, follow the structure and lifecycle in `Doc_Spec.md`.
2) **Install & (optionally) launch local UI / API for manual testing**
   ```bash
   # From the project (or sample) parent dir when using ADK's dev UI
   pip install google-adk
   export SSL_CERT_FILE=$(python -m certifi)   # required for voice/video tests
   adk web                                     # or: adk api_server
   # Windows workaround if you see NotImplementedError:
   # adk web --no-reload
   ```
3) **Run fast checks**
   ```bash
   ./autoformat.sh
   ```
4) **Run tests**
   ```bash
   pytest tests/unittests
   ```
5) **Make a minimal, reviewable change** using conventional commits (see Commit & PR).

---

## Setup commands
- **Install ADK (dependency; recommended stable):**
  ```bash
  pip install google-adk
  ```
  *(Dev version, if needed:)*
  ```bash
  pip install git+https://github.com/google/adk-python.git@main
  ```

- **Environment for ADK dev UI (if using it locally):**
  ```bash
  export SSL_CERT_FILE=$(python -m certifi)
  adk web             # open http://localhost:8000
  # or
  adk api_server
  # Windows workaround:
  # adk web --no-reload
  ```

- **Autoformat / lint helper:**
  ```bash
  ./autoformat.sh
  ```

> Notes (FYI): For Live/streaming usage, store input/output transcriptions as **Events** and audio as **artifacts** referenced by Events; streaming tests typically live under `tests/unittests/streaming/` in ADK examples.

---

## How agents should work here

### Model & call policy
- **Before any LLM/tool call**, read `llms-full.txt` and apply its directives (model choices, params, safety/rate limits, and local testing guidance). This requirement takes precedence where rules conflict.

### ADK usage policy
- Treat ADK as a **library**; do **not** modify ADK’s source or contribute upstream from this repo.
- Use `adk web` or `adk api_server` for local/manual testing only, not as a production dependency.

### Python code style (summary)
- Follow Google/PEP 8 style expectations:
  - Prefer 2-space indent (unless repo specifies otherwise), ~80–100 char lines.
  - `snake_case` for functions/vars, `CamelCase` for classes.
  - Public APIs use docstrings; keep imports organized/sorted.
  - Catch **specific** exceptions, not bare `Exception`.
  - Use `./autoformat.sh` to fix common issues automatically.

### Documentation workflow
- All feature docs must follow `Doc_Spec.md`:
  - Place specs/progress under `documentation/features/{planned|active|completed}`.  
  - Use kebab-case, `-spec.md` / `-progress.md` suffixes.  
  - Move items through **Planning → Active → Completed** lifecycle.
- Prefer *linking* to docs rather than duplicating details in AGENTS.md.

---

## Commands (copy–paste)
- **Type check** *(if using mypy)*:
  ```bash
  mypy src
  ```

- **Format**:
  ```bash
  ./autoformat.sh
  ```

- **Lint** *(choose your configured linter)*:
  ```bash
  pylint src
  # or
  ruff check src
  ```

- **Tests (fast)**:
  ```bash
  pytest tests/unittests -q
  ```

- **Tests (full/CI)**:
  ```bash
  pytest
  ```

- **Evaluate sample (if applicable)**:
  ```bash
  adk eval samples_for_testing/hello_world            samples_for_testing/hello_world/hello_world_eval_set_001.evalset.json
  ```

---

## Project map (minimal)
- `/src/` — Python modules (safe to modify per task)
- `/scripts/` — automation helpers (keep idempotent)
- `/docs/` or `/documentation/` — follow **Doc_Spec** structure & templates; don’t inline feature details here.
- `/tests/` — unit tests; run/extend as needed.
- `/infra/` — infrastructure; changes require human review

---

## Commit & PR guidelines
- Use **Conventional Commits**; add `#non-breaking` for non-breaking changes, `#breaking` for breaking ones.
- Keep PRs small and scoped; include repro steps and tests where relevant.
- Ensure format/lint/tests pass locally before opening a PR (see Commands).

---

## When to ask for help / stop
Stop and request human input (open an issue or comment on PR) when:
- Dependencies or local UI fail to start **after two attempts** (including Windows `--no-reload` workaround).
- Tests repeatedly fail or exceed expected local runtime.
- Required credentials/API keys are missing (use ADK credential request flow if applicable).
- Proceeding would require modifying ADK’s own source or repo structure (out of scope here).

---

## Non-goals
- **Do not** contribute to or modify **Google ADK** upstream from this repo; use it as a dependency only.  
- **Do not** duplicate feature docs here; **link** and follow `Doc_Spec.md`.

---

## References
- **`llms-full.txt`** — *must read before every call*; includes local testing & ADK UI instructions.  
  Path: `/llms-full.txt` (adjust if stored elsewhere).
- **`Doc_Spec.md`** — docs structure, naming, lifecycle, and templates.  
  Path: `/Doc_Spec.md` (or `/Doc_Spec.md.md` if that’s your filename).
- **`ADK_AGENTS.md`** — setup helper, code style, testing, commit rules, streaming notes.  
  Path: `/ADK_AGENTS.md`.

---

### Appendix: Using ADK as a dependency (FYI)
- ADK is model-agnostic and Python-first; you can compose single or multi-agent systems and test them in the built-in dev UI (`adk web`). Sample `pip install` and quickstart commands above come from ADK’s public docs.

> Keep this file explicit and concise. Update it when commands or docs move. If a subfolder needs special rules, add a scoped `AGENTS.md` there and link it from here.
