# Codebase Structure

**Analysis Date:** 2026-10-05

## Directory Layout

```text
sipSup/
├── sipsup/                 # Primary Python package implementing the 4 pillars
│   ├── gateway/            # Pillar 1 (Harness): CLI, voice, Telegram, Discord, WhatsApp
│   ├── loop/               # Pillar 2 (Loop): ReAct agent while-loop and model wire adapters
│   ├── graph/              # Pillar 2 (Loop extension): Graph DAG engine and workflow nodes
│   ├── memory/             # Pillar 3 (Memory): Semantic, episodic, procedural, retrieval gate
│   │   ├── semantic/       # Fact stores (SQLite FTS5, Supabase, Mem0, Zep, LangMem)
│   │   ├── episodic/       # Episode stores (SQLite FTS5, Notion)
│   │   └── procedural/     # Skill file loader and markdown installer
│   ├── tools/              # Tool implementations and ToolRegistry
│   ├── ops/                # Pillar 4 (Ops): Tracing, dashboard, pricing, release gate
│   │   ├── runtime/        # Session and working memory management
│   │   ├── static/         # Frontend dashboard assets (HTML, JS, CSS)
│   │   └── whiteboard/     # Architectural diagram generators
│   ├── app.py              # Central assembly diagram: builds SipSup instance
│   ├── config.py           # Dataclass settings and robust .env loader
│   ├── db.py               # SQLite schema, FTS5 virtual tables, and migrations
│   ├── integrations.py     # Unified integration registry and connection health
│   └── __main__.py         # CLI executable entrypoint
├── evals/                  # Pillar 4 (Evals): Deterministic tests and LLM-as-judge
│   ├── deterministic/      # Offline regression tests (pytest)
│   ├── judge/              # Scored LLM-as-judge eval benchmarks
│   ├── helpers.py          # Scripted mock LLM clients and test factory
│   └── conftest.py         # Test discovery paths
├── skills/                 # Bundled procedural skills shipped with the package
│   ├── schedule-meeting/   # Calendar scheduling skill contract
│   ├── weekly-brief/       # Morning/weekly briefing skill contract
│   └── community/          # Community contributed skill definitions
├── docs/                   # Architecture documentation, design docs, and playbooks
├── scripts/                # Utility scripts (skills validation, shootouts, env generators)
├── sql/                    # SQL migration scripts (Supabase pgvector init)
├── examples/               # Standalone MCP demo servers and memory agent examples
├── Makefile                # Unified CLI task runner (run, voice, dashboard, gate)
├── pyproject.toml          # Package metadata, optional extras, ruff configuration
└── uv.lock                 # Pinned dependency lockfile
```

## Directory Purposes

**`sipsup/gateway/`:**
- Purpose: Ingress channel adapters interfacing user input with the core agent.
- Contains: Protocol handlers, asyncio runners, webhook listeners.
- Key files: `cli.py`, `voice.py`, `telegram.py`, `discord.py`, `whatsapp.py`, `runner.py`, `supervisor.py`.

**`sipsup/loop/`:**
- Purpose: Core reasoning loop and model API client abstraction.
- Contains: ReAct while-loop implementation, multi-provider model registry, wire format normalizers.
- Key files: `agent.py` (ReAct loop), `models.py` (8 LLM providers, model catalogs, endpoint pairs).

**`sipsup/graph/`:**
- Purpose: Directed graph workflow engine for multi-step or parallelized tasks.
- Contains: Node execution primitives, DAG engine, workflow definitions.
- Key files: `engine.py`, `nodes.py`, `workflows/triage.py`, `workflows/gather.py`.

**`sipsup/memory/`:**
- Purpose: Three-pillar long-term memory architecture and lifecycle management.
- Contains: FTS5 SQLite tables, pluggable cloud stores, retrieval gate classification, memory consolidation.
- Key files: `__init__.py` (facade), `retrieval_gate.py` (gate classifier), `consolidation.py` (distillation worker).

**`sipsup/tools/`:**
- Purpose: Executable capabilities available to the model.
- Contains: Tool definition dataclass, schema generator, execution dispatcher, built-in tools.
- Key files: `registry.py`, `calendar.py`, `google_calendar.py`, `apple.py`, `github.py`, `search.py`, `mcp_client.py`, `experimental.py`.

**`sipsup/ops/`:**
- Purpose: Observability, developer tooling, web dashboard, and release verification.
- Contains: JSONL turn tracing, HTTP dashboard server, token pricing counters, eval gate script.
- Key files: `dashboard.py`, `tracing.py`, `release_gate.py`, `pricing.py`, `catalog.py`.

**`evals/`:**
- Purpose: Automated quality assurance, unit tests, and judge benchmarks.
- Contains: Deterministic pytest suites, offline LLM playback scripts, evaluation datasets.
- Key files: `deterministic/` (~60 test files), `judge/test_retrieval_gate_accuracy.py`, `helpers.py`.

## Key File Locations

**Entry Points:**
- `sipsup/__main__.py`: CLI entry point (`sipsup` executable).
- `sipsup/ops/dashboard.py`: Web dashboard runner (`python -m sipsup.ops.dashboard`).
- `sipsup/ops/release_gate.py`: Pre-release quality gate (`make gate`).

**Configuration:**
- `sipsup/config.py`: Single source of truth for runtime settings dataclass.
- `.env.example`: Complete documentation of all supported environment variables.
- `pyproject.toml`: Build setup, dependency extras, ruff lint rules.

**Core Logic:**
- `sipsup/app.py`: Central `SipSup` coordinator class connecting all components.
- `sipsup/loop/agent.py`: `run_loop()` implementation.
- `sipsup/db.py`: Database schema and SQLite connection factory.
- `sipsup/integrations.py`: Central catalog of external integrations and health checks.

**Testing:**
- `evals/helpers.py`: `ScriptedClient` and `make_sipsup()` test harness.
- `evals/conftest.py`: Root sys.path insertion for test runs.

## Naming Conventions

**Files:**
- Snake case for all Python modules: `retrieval_gate.py`, `google_calendar.py`.
- Test files prefixed with `test_`: `evals/deterministic/test_scoring.py`.
- Procedural skill documents uppercase: `skills/<name>/SKILL.md`.

**Directories:**
- Snake case or lowercase single word: `gateway`, `ops`, `whiteboard`.
- Skill directories hyphenated lowercase: `skills/schedule-meeting/`.

**Classes and Functions:**
- Classes: PascalCase (`SipSup`, `ToolRegistry`, `ScriptedClient`, `SqliteFactStore`).
- Functions & methods: snake_case (`run_loop`, `gated_retrieve`, `build_system`).
- Constants & Registries: UPPER_CASE (`PROVIDERS`, `SCHEMA`, `INTEGRATIONS`).

## Where to Add New Code

**New Tool:**
1. Implement the tool functions or class in `sipsup/tools/<tool_name>.py`.
2. Register the tool schema and handler in `build_registry()` inside `sipsup/tools/registry.py`.
3. Add deterministic tests in `evals/deterministic/test_<tool_name>.py` mocking external I/O.

**New LLM Provider:**
1. Add a new `Provider` entry to `PROVIDERS` in `sipsup/loop/models.py`.
2. Declare required environment variables and base URLs.
3. Add provider integration metadata in `sipsup/integrations.py`.
4. Add provider verification tests in `evals/deterministic/test_providers.py`.

**New Memory Store Backend:**
1. Implement the `FactStore` or `EpisodeStore` interface in `sipsup/memory/semantic/` or `sipsup/memory/episodic/`.
2. Ensure the store adheres to the conformance suite in `evals/deterministic/test_fact_store_conformance.py`.
3. Wire the backend into `Memory._make_fact_store()` in `sipsup/memory/__init__.py`.

**New Procedural Skill:**
1. Create a new directory under `skills/<skill-name>/`.
2. Add a `SKILL.md` file formatted with YAML frontmatter specifying `name`, `triggers`, and description.
3. Run `python scripts/validate_skills.py` to confirm syntax and trigger validity.

## Special Directories

**`.sipsup/` (Local State Directory):**
- Purpose: Stores local runtime database (`state.db`), markdown export (`MEMORY.md`), session caches, and trace logs (`traces/*.jsonl`).
- Generated: Yes (automatically created on first agent startup via `Settings.ensure_home()`).
- Committed: No (strictly excluded in `.gitignore` to preserve privacy and prevent secret leakage).

**`.planning/` (GSD Planning Directory):**
- Purpose: Contains GSD project roadmap, architectural maps, phase plans, and state artifacts.
- Generated: Yes (generated and updated by GSD workflows).
- Committed: Yes (project knowledge base tracked in Git).

---

*Structure analysis: 2026-10-05*
