# Coding Conventions

**Analysis Date:** 2026-10-05

## Naming Patterns

**Files:**
- Snake case for all Python modules: `sipsup/loop/agent.py`, `sipsup/memory/retrieval_gate.py`.
- Test files prefixed with `test_`: `evals/deterministic/test_retrieval_gate.py`.
- Skill markdown contracts capitalized: `SKILL.md`.

**Functions:**
- Snake case: `run_loop()`, `gated_retrieve()`, `build_system()`.
- Private/internal helpers prefixed with leading underscore: `_load_env()`, `_migrate()`, `_capture()`.
- Factory functions named `make_<entity>` or `build_<entity>`: `make_sipsup()`, `build_registry()`.

**Variables:**
- Snake case: `user_message`, `session_id`, `stop_reason`.
- Constants and global registries in UPPER_CASE: `PROVIDERS`, `SCHEMA`, `GATE_PROMPT`, `DOTENV_PATH`.

**Types & Classes:**
- PascalCase for classes and dataclasses: `SipSup`, `Settings`, `Provider`, `LoopResult`, `ToolRegistry`.
- Type aliases in PascalCase: `LoopEvent`, `Observer`.

## Code Style

**Formatting:**
- Managed via `ruff` (`ruff==0.16.0` pinned strictly in `pyproject.toml`).
- Max line length: 100 characters (`line-length = 100`).
- Modern Python type hints enabled with `from __future__ import annotations` at the top of every module.

**Linting:**
- Linter: `ruff` 0.16.0.
- Deliberate Ignore Rules (configured in `[tool.ruff.lint]`):
  - `BLE001`: Blind `except Exception` is the documented pattern. Tools and observers catch exceptions and return readable text messages rather than crashing the loop.
  - `DTZ001`, `DTZ005`, `DTZ011`: Naive local datetimes are intentional. Daily trace files and workspace folders reflect user-local time, not UTC.
  - `S110`: Permitted `try/except/pass` around optional third-party integrations (OTel, audio libraries, optional extras).
  - `RUF100`: Unused `# noqa` warnings disabled so contributors writing `# noqa: BLE001` do not trigger CI failures.

## Import Organization

**Order:**
1. Future annotations: `from __future__ import annotations`
2. Standard library modules (`os`, `sys`, `json`, `sqlite3`, `pathlib`)
3. Third-party dependencies (`anthropic`, `openai`, `rich`, `dotenv`, `pytest`)
4. Internal `sipsup` package modules (`from sipsup.config import Settings`)

*Note: Ruff rule `I001` enforces strict alphabetical sorting within import groups (e.g. `from datetime import datetime, timezone` rather than `timezone, datetime`).*

**Path Aliases:**
- Absolute package imports used across codebase: `from sipsup.config import Settings`.
- No root relative hacks; root is added to `sys.path` in `evals/conftest.py` for test runners.

## Error Handling

**Patterns:**
- **Fail-Soft in Tools:** Tool functions catch internal errors and return actionable string diagnostics to the model instead of raising:
  ```python
  try:
      # perform external action
  except Exception as exc:
      return f"Error executing tool: {type(exc).__name__}: {exc}"
  ```
- **Fail-Open in Classifiers:** Fast-path decision gates (retrieval gate, triage classifier) always fail open upon error:
  ```python
  try:
      decision = json.loads(text)
      return bool(decision.get("retrieve")), decision.get("query", message), decision.get("reason", "")
  except Exception as exc:
      return True, message, f"gate failed open ({type(exc).__name__})"
  ```

## Logging & Observability

**Framework:**
- Custom non-intrusive `Tracer` (`sipsup/ops/tracing.py`) writing append-only JSONL files (`.sipsup/traces/trace-YYYY-MM-DD.jsonl`).
- Terminal progress and output rendered via `rich.console.Console`.
- Decoupled `Observer` callback pattern:
  ```python
  LoopEvent = dict[str, Any]
  Observer = Callable[[str, LoopEvent], None]
  ```

**Patterns:**
- Do not use verbose standard `logging.getLogger()` calls across business logic.
- Emit structured events through `notify(kind, event_dict)` for UI reactivity and tracing.

## Comments & Documentation

**When to Comment:**
- Explain **WHY** a design decision was made, especially around non-obvious edge cases (e.g. why `usecwd=True` in `_load_env()`, why `max_tokens=8192` for reasoning models).
- Module-level docstrings should provide an architectural summary and component relationships.

**Docstrings:**
- Standard triple-quote docstrings (`"""..."""`) on modules, major classes, and public APIs.
- Self-explanatory internal helpers can rely on concise type hints and descriptive names.

## Function Design

**Size:**
- Single responsibility; concise and focused functions (typically 15-40 lines). Complex orchestration extracted into smaller helpers.

**Parameters:**
- Use keyword arguments and default values in dataclasses for configuration.
- Dependency injection pattern for external dependencies (`client`, `conn`, `settings`) to support offline scripted evals.

**Return Values:**
- Structured results encapsulated in `@dataclass` containers (`LoopResult`, `IntegrationStatus`).

## Module Design

**Exports:**
- Controlled module facades using `__all__` or clean `__init__.py` exposures (e.g. `sipsup.memory.Memory`, `sipsup.tools.build_registry`).

**Barrel Files:**
- Sub-packages provide an `__init__.py` acting as a single entrypoint for that pillar (e.g. `sipsup/memory/__init__.py`, `sipsup/loop/__init__.py`).

---

*Convention analysis: 2026-10-05*
