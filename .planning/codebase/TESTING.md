# Testing Patterns

**Analysis Date:** 2026-10-05

## Test Framework

**Runner:**
- `pytest` (>=8.0, runner via `uv run --extra dev pytest` or Makefile)
- Config: Configured via `pyproject.toml`
- Runner Helper: `sipsup/ops/release_gate.py` (`make gate`)

**Assertion Library:**
- Standard Python `assert` statements with expressive failure messages.

**Run Commands:**
```bash
uv run --extra dev pytest evals/deterministic           # Run all deterministic tests
make eval                                              # Run deterministic suite via Makefile
make eval-judge                                        # Run LLM-as-judge benchmarks (requires API key)
make gate                                              # Execute full release gate (deterministic + judge)
uv run --extra dev pytest evals/deterministic/test_scoring.py  # Run a single test file
```

## Test File Organization

**Location:**
- Separate test directory: `evals/` sits at the repo root parallel to `sipsup/`.
- Root path discovery configured in `evals/conftest.py`.

**Naming:**
- Files: `evals/deterministic/test_*.py` and `evals/judge/test_*.py`.
- Functions: `test_*`.

**Structure:**
```text
evals/
├── conftest.py             # Global test path configuration
├── helpers.py              # Mocking primitives (ScriptedClient) and make_sipsup() factory
├── dataset.jsonl           # Benchmark interaction scenarios
├── coding.jsonl            # Coding evaluation prompts
├── memory_arena.json       # Memory accuracy test corpus
├── deterministic/          # 680+ offline deterministic regression tests
└── judge/                  # Live LLM evaluation suites
```

## Test Structure

**Suite Organization:**
```python
from pathlib import Path
from evals.helpers import ScriptedClient, make_sipsup, response, text_block, tool_block


def test_turn_executes_tool_and_returns_reply(tmp_path: Path):
    # 1. Arrange: Prepare mock client responses and isolated agent instance
    script = [
        response([tool_block("list_events", {"date": "2026-10-05"})]),
        response([text_block("You have no events scheduled for today.")]),
    ]
    agent = make_sipsup(tmp_path, client=ScriptedClient(script))

    # 2. Act: Send message to the agent
    result = agent.respond("What is on my calendar today?")

    # 3. Assert: Validate return value, tool executions, and iterations
    assert "no events" in result.reply.lower()
    assert len(result.tool_calls) == 1
    assert result.tool_calls[0]["tool"] == "list_events"
    assert result.iterations == 2
```

**Patterns:**
- **Setup Pattern:** Use pytest's built-in `tmp_path` fixture to provide an isolated `.sipsup` home directory for each test run.
- **Teardown Pattern:** Automatic directory cleanup by pytest fixtures; SQLite connections closed naturally on garbage collection.
- **Assertion Pattern:** Assert on `LoopResult` properties (`reply`, `tool_calls`, `iterations`) and direct database records in `state.db`.

## Mocking

**Framework:**
- In-house zero-dependency mock framework in `evals/helpers.py`.

**Mocking Patterns:**
```python
# Helper structures in evals/helpers.py:
def text_block(text: str):
    return SimpleNamespace(type="text", text=text)

def tool_block(name: str, args: dict, call_id: str = "tu_1"):
    return SimpleNamespace(type="tool_use", id=call_id, name=name, input=args)

class ScriptedClient:
    """Plays back a fixed list of responses — the 'model' for offline tests."""
    def __init__(self, script: list):
        self._script = list(script)
        self.messages = SimpleNamespace(create=self._create)

    def _create(self, **kwargs):
        return self._script.pop(0)
```

**What to Mock:**
- External LLM provider API responses (`ScriptedClient`).
- External network requests (Tavily search, Google Calendar APIs, Notion).
- Host platform commands (AppleScript `/usr/bin/osascript`, `gh` CLI subprocesses).

**What NOT to Mock:**
- Local SQLite database and FTS5 search (real database is created and verified in `tmp_path`).
- ReAct loop state transitions and token window calculations.
- Tool schemas and JSON parsing logic.

## Fixtures and Factories

**Agent Factory (`evals/helpers.py`):**
```python
def make_sipsup(home: Path, client=None, **settings_overrides):
    """Build a SipSup with an isolated home dir; optionally swap in a fake client."""
    from sipsup.app import SipSup
    from sipsup.config import Settings

    # Pins external side-effects off by default for determinism
    for switch in ("apple_calendar", "google_calendar", "apple_tools", "graph_workflows"):
        settings_overrides.setdefault(switch, False)
    settings = Settings(home=home, **settings_overrides)
    if client is not None and not settings.api_key:
        settings.api_key = "offline"
    return SipSup(settings=settings, client=client)
```

**Location:**
- Shared fixtures and mock helpers: `evals/helpers.py`.
- Benchmark datasets: `evals/dataset.jsonl`, `evals/memory_arena.json`.

## Coverage

**Requirements:**
- High test coverage across deterministic logic (over 680 tests passing in `evals/deterministic/`).
- 100% pass rate required for deterministic tests to clear the pre-release gate (`make gate`).
- Judge evaluations require passing threshold scores when API keys are available.

## Test Types

**Deterministic Unit & Integration Tests (`evals/deterministic/`):**
- Fast, fully offline tests executing the real agent against `ScriptedClient` and real SQLite.
- Tests tool triggers, memory persistence, FTS search, history window slicing, and gateway supervisors.

**LLM-as-Judge Evaluations (`evals/judge/`):**
- Scored end-to-end evaluations testing qualitative outputs against real LLM APIs.
- Evaluates retrieval gate accuracy (`test_retrieval_gate_accuracy.py`) and response helpfulness.

**Benchmark Shootouts (`scripts/shootout.py`):**
- Competitive multi-model performance arena comparing speed, tool calling accuracy, and cost.

## Platform Compatibility Warning

- **Python 3.10 vs 3.11+ Notice:** Tests importing standard library `tomllib` (`evals/deterministic/test_version.py` and `evals/deterministic/test_packaging.py`) require Python 3.11+ or `tomli` fallback. On Python 3.10 runtimes, these two tests throw collection errors unless executed on Python 3.11+.

---

*Testing analysis: 2026-10-05*
