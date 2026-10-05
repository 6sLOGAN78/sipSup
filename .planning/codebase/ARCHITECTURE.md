<!-- refreshed: 2026-10-05 -->
# Architecture

**Analysis Date:** 2026-10-05

## System Overview

```text
┌───────────────────────────────────────────────────────────────────────────┐
│                           PILLAR 1: HARNESS                               │
│  CLI (`sipsup/gateway/cli.py`)          │ Voice (`sipsup/gateway/voice.py`)│
│  Telegram (`sipsup/gateway/telegram.py`) │ Discord / WhatsApp / Dashboard   │
└─────────────────────────────────────┬─────────────────────────────────────┘
                                      │ user_message / stream
                                      ▼
┌───────────────────────────────────────────────────────────────────────────┐
│                      PILLAR 2: LOOP & GRAPH RUNTIME                       │
│  `sipsup/app.py` (Coordinator)                                            │
│   ├── Graph Router: `sipsup/graph/engine.py` (Optional triage workflow)   │
│   └── ReAct Loop: `sipsup/loop/agent.py` (Observe → Reason → Act)         │
│        ├── LLM Clients: `sipsup/loop/models.py` (Anthropic / OpenAI wire) │
│        └── Tool Registry: `sipsup/tools/registry.py`                      │
└──────────────┬─────────────────────────────────────────────┬──────────────┘
               │                                             │
               ▼                                             ▼
┌─────────────────────────────────────────┐  ┌──────────────────────────────┐
│            PILLAR 3: MEMORY             │  │        PILLAR 4: OPS         │
│  `sipsup/memory/__init__.py`            │  │  `sipsup/ops/tracing.py`     │
│  ├── Retrieval Gate: `retrieval_gate.py`│  │  `sipsup/ops/dashboard.py`   │
│  ├── Procedural: `SKILL.md` via Loader  │  │  `sipsup/ops/release_gate.py`│
│  ├── Semantic: SQLite FTS5 / Supabase   │  │  `evals/` (deterministic &   │
│  ├── Episodic: Episodes FTS5 / Notion   │  │           judge test suites) │
│  └── Consolidation: `consolidation.py`  │  │  `sipsup/ops/pricing.py`     │
└──────────────────┬──────────────────────┘  └──────────────┬───────────────┘
                   │                                        │
                   ▼                                        ▼
┌───────────────────────────────────────────────────────────────────────────┐
│                              LOCAL STORAGE                                │
│  `.sipsup/state.db` (SQLite) │ `.sipsup/traces/*.jsonl` │ `.sipsup/MEMORY.md`│
└───────────────────────────────────────────────────────────────────────────┘
```

## Component Responsibilities

| Component | Responsibility | File |
|-----------|----------------|------|
| `SipSup` Facade | Coordinates config, db, tools, memory, session, and turn lifecycle | `sipsup/app.py` |
| `Settings` | Typed configuration dataclass loaded once from `.env` | `sipsup/config.py` |
| Database Engine | SQLite schema, FTS5 virtual tables, triggers, and migrations | `sipsup/db.py` |
| Core ReAct Loop | Bounded loop executing LLM inference and tool dispatches | `sipsup/loop/agent.py` |
| Provider Adapter | Unifies Anthropic and OpenAI-compatible providers under one wire interface | `sipsup/loop/models.py` |
| Graph Engine | Directed workflow graph runner with parallel execution and streaming | `sipsup/graph/engine.py` |
| Memory Facade | Coordinates procedural, semantic, and episodic memory layers | `sipsup/memory/__init__.py` |
| Retrieval Gate | Small-model classifier deciding whether to query long-term memory | `sipsup/memory/retrieval_gate.py` |
| Memory Consolidation | Distills raw chat history into facts and dated episodes every N turns | `sipsup/memory/consolidation.py` |
| Tool Registry | Discovers, formats schemas for, and safely dispatches tool calls | `sipsup/tools/registry.py` |
| Gateways | Adapts channel protocols (CLI, Voice, Telegram, Discord, WhatsApp) | `sipsup/gateway/` |
| Ops Dashboard | HTTP server providing real-time chats, traces, and integration settings | `sipsup/ops/dashboard.py` |
| Tracer | JSONL structured turn logging and OpenTelemetry exporter | `sipsup/ops/tracing.py` |
| Release Gate | Automated CI/local gate verifying deterministic evals and judge scores | `sipsup/ops/release_gate.py` |

## Pattern Overview

**Overall:** Local-First Layered Micro-Kernel with Four Decoupled Pillars (Harness, Loop, Memory, Ops).

**Key Characteristics:**
- **Zero Heavy Frameworks:** Built with Python standard library constructs and direct provider SDKs rather than monolithic frameworks.
- **Fail-Open Gatekeeping:** Sub-model classifications (retrieval gate, triage graph) always fail open to full execution upon unexpected error or missing output.
- **Sliding Working Memory:** Bounded context window prevents token explosions, offloading long-term knowledge to local FTS5 indexing.
- **Observable Events:** All loop transitions, tool calls, and model tokens stream through functional `Observer` callables (`Callable[[str, LoopEvent], None]`).

## Layers

**Harness Layer (`sipsup/gateway/`, `sipsup/runtime/`):**
- Purpose: User-facing entrypoints across terminal, voice, chat apps, and web.
- Depends on: `sipsup/app.py`, `sipsup/config.py`.
- Used by: End users, automated supervisors.

**Loop & Graph Layer (`sipsup/loop/`, `sipsup/graph/`):**
- Purpose: Model reasoning, tool selection, structured task graphs, and iterative convergence.
- Depends on: `sipsup/tools/`, `sipsup/loop/models.py`, `anthropic`, `openai`.
- Used by: `sipsup/app.py`.

**Memory Layer (`sipsup/memory/`):**
- Purpose: Multi-tier memory retention (procedural skills, semantic facts, episodic history).
- Location: `sipsup/memory/`.
- Depends on: `sipsup/db.py`, `sipsup/config.py`, model clients.
- Used by: `sipsup/app.py`, `sipsup/tools/memory_admin.py`.

**Ops & Evaluation Layer (`sipsup/ops/`, `evals/`):**
- Purpose: Turn tracing, token pricing calculations, web monitoring UI, and test-driven regression gates.
- Depends on: `sipsup/config.py`, `sipsup/db.py`, `pytest`.
- Used by: Maintainers, CI pipelines, local dashboard server.

## Data Flow

### Primary Request Path

1. **User Input:** Message received via Gateway (e.g. CLI prompt in `sipsup/gateway/cli.py:50` or HTTP POST `/chat` in `sipsup/ops/dashboard.py:410`).
2. **Turn Coordination:** Gateway invokes `SipSup.respond(user_message, observer, source)` in `sipsup/app.py:42`.
3. **Trace Initialization:** Turn context opens in `Tracer.turn()` (`sipsup/ops/tracing.py:45`).
4. **System Prompt Construction:** `Session.build_system()` in `sipsup/ops/runtime/session.py:35` triggers:
   - `Memory.gated_retrieve()` (`sipsup/memory/__init__.py:91`), which calls `retrieval_gate.should_retrieve()` using `SIPSUP_SMALL_MODEL`.
   - If gate returns `True`, queries `facts_fts` and `episodes_fts` in `state.db`.
   - `SkillLoader.match()` (`sipsup/memory/procedural/loader.py:40`) scans skill trigger phrases in `skills/*/SKILL.md`.
5. **Context Windowing:** Bounded prompt history is extracted (`session.history[-history_turns * 2:]`) in `sipsup/app.py:124`.
6. **ReAct Loop Execution:** `run_loop()` in `sipsup/loop/agent.py:41` iterates:
   - LLM reason call: `client.messages.create()` or `client.messages.stream()`.
   - Tool dispatch: `tools.execute(name, args)` executed against `ToolRegistry` (`sipsup/tools/registry.py:45`).
   - Observe: Tool outputs appended to working memory as `tool_result` blocks.
7. **Storage & Consolidation:**
   - Raw interaction logged to `chat_log` in `state.db` with performance metadata (`sipsup/memory/__init__.py:109`).
   - `Memory.maybe_consolidate()` checks exchange count threshold; if due, runs background distillation (`sipsup/memory/consolidation.py:30`).
   - `Memory.export_markdown()` updates `.sipsup/MEMORY.md`.
8. **Trace Finalization:** `Tracer.end_turn()` commits JSONL line to `.sipsup/traces/trace-YYYY-MM-DD.jsonl`.
9. **Return:** `LoopResult` containing reply text and tool execution events returned to caller.

### Secondary Flow: Graph Triage Workflow

1. User sends message when `SIPSUP_GRAPH_WORKFLOWS=1`.
2. `SipSup._respond_via_graph()` constructs the triage DAG (`sipsup/graph/workflows/triage.py`).
3. Classify node uses `small_model` to score request as either `quick_reply` or `full_agent`.
4. If `quick_reply`, returns direct formatted response without initializing tool schemas.
5. If `full_agent` or if any graph node throws an exception, workflow executes or fails open to `_run_full_turn()`.

**State Management:**
- Persistent relational and FTS5 state stored in SQLite file: `.sipsup/state.db`.
- In-memory conversation session tracked in `Session` class (`sipsup/ops/runtime/session.py`).
- Read/write thread synchronization in ops dashboard handled via `threading.Lock` around database connection and agent instances.

## Key Abstractions

- `Tool`: Dataclass declaring name, description, JSON schema parameters, and execution callable (`sipsup/tools/registry.py`).
- `Provider`: Dataclass declaring wire protocol adapter, endpoint mappings, and default flagship/fast models (`sipsup/loop/models.py`).
- `FactStore`: Abstract protocol for semantic memory implementations (SQLite FTS5, Supabase, Mem0, Zep, LangMem) (`sipsup/memory/semantic/base.py`).
- `EpisodeStore`: Protocol for episodic history backends (`SqliteEpisodeStore`, `NotionEpisodeStore`).
- `Skill`: Represents procedural instructions loaded from disk (`sipsup/memory/procedural/loader.py`).
- `Graph`: Lightweight directed acyclic graph composed of named nodes, transitions, and parallel branches (`sipsup/graph/engine.py`).

## Entry Points

- **CLI Application:** `sipsup` executable pointing to `sipsup.__main__:main` (`sipsup/__main__.py`).
- **Dashboard Web Server:** `python -m sipsup.ops.dashboard` (or `make dashboard`), listening on `http://localhost:7777`.
- **Channel Gateways:**
  - `python -m sipsup telegram` (`sipsup/gateway/telegram.py`)
  - `python -m sipsup discord` (`sipsup/gateway/discord.py`)
  - `python -m sipsup whatsapp` (`sipsup/gateway/whatsapp.py`)
  - `python -m sipsup voice` (`sipsup/gateway/voice.py`)
- **Release Verification Gate:** `python -m sipsup.ops.release_gate` (or `make gate`).

## Architectural Constraints

- **Single SQLite Source of Truth:** All persistent state is in `state.db`. Multiple processes accessing it must respect SQLite file locking; `PRAGMA busy_timeout=3000` is enforced in `sipsup/db.py`.
- **Threading Model:** Single-process event loop / thread per request in `ThreadingHTTPServer`. Database access from secondary threads requires `check_same_thread=False` and explicit locking.
- **Fail-Open Strategy:** If any optimization classifier (retrieval gate, triage router) fails or times out, execution must immediately default to standard un-gated agent loop.
- **Reasoning Token Headroom:** Large token budget (`max_tokens=8192`) must be reserved when calling reasoning models (Kimi K3, DeepSeek-R1, OpenAI o-series) to prevent truncated reasoning blocks.

## Anti-Patterns

### Default-On Memory Retrieval
- **What happens:** Querying vector/FTS database on every single turn regardless of topic.
- **Why it's wrong:** Introduces unnecessary latency and injects irrelevant context that causes the model to hallucinate or over-interpret unrelated personal details.
- **Do this instead:** Use the LLM retrieval gate (`sipsup/memory/retrieval_gate.py`) to classify whether retrieval is required before issuing searches.

### Unbounded Prompt Context Accumulation
- **What happens:** Appending all previous conversation history indefinitely into the prompt array.
- **Why it's wrong:** Rapidly exhausts token budgets, skyrockets API costs, increases response latency, and eventually triggers context overflow errors.
- **Do this instead:** Maintain a bounded sliding window (`history_turns * 2`) in working memory (`sipsup/app.py:123`), relying on consolidation and FTS5 retrieval for older history.

### Crashing on Tool Exceptions
- **What happens:** Allowing third-party tool execution errors (e.g. calendar API, network search) to raise unhandled exceptions.
- **Why it's wrong:** Abruptly terminates the conversation turn and degrades user experience.
- **Do this instead:** Tools must catch internal exceptions and return actionable error descriptions as string results in the tool block (`BLE001` intentional ignore).

## Error Handling

**Strategy:** Fail-soft and fail-open. Recover gracefully with descriptive diagnostics instead of process crashes.

**Patterns:**
- Gate Fail-Open: `sipsup/memory/retrieval_gate.py:54` returns `True, message, "gate failed open"` upon JSON decoding error or exception.
- Graph Fail-Open: `sipsup/app.py:78` falls open to `_run_full_turn` if graph workflow execution raises.
- Tool Isolation: Tool executions in `sipsup/tools/registry.py` catch exceptions and serialize them as `"Error: ..."` content blocks.

## Cross-Cutting Concerns

**Logging:** Handled transparently by `Tracer` (`sipsup/ops/tracing.py`), which writes append-only JSONL files and optionally forwards spans to OpenTelemetry collectors.
**Validation:** Lightweight typing via Python dataclasses, custom normalization routines in `sipsup/integrations.py`, and JSON schema contracts in `sipsup/tools/registry.py`.
**Authentication:** Environment variable secrets discovery via `sipsup.config._load_env()`, local allowlist gating for channel gateways, and OAuth token persistence in `.sipsup/`.

---

*Architecture analysis: 2026-10-05*
