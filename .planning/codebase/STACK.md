# Technology Stack

**Analysis Date:** 2026-10-05

## Languages

**Primary:**
- Python >=3.10 (tested on 3.10.12; targets 3.11, 3.12) - Core agent framework, runtime, gateways, memory engines, tools, ops dashboard backend, and evaluation suites (`sipsup/`, `evals/`, `scripts/`)

**Secondary:**
- JavaScript (Vanilla ES6) / HTML5 / CSS3 - Built-in single-page ops and chat dashboard frontend (`sipsup/ops/static/index.html`, `sipsup/ops/static/app.js`, `sipsup/ops/static/style.css`)
- SQL (SQLite 3 dialect + FTS5 full-text search) - Relational state storage, chat logs, semantic facts, and episodic memory (`sipsup/db.py`, `sql/init_supabase.sql`)
- Bash - Command automation, Git history maintenance, and developer shortcuts (`Makefile`, `rewrite_git.sh`)

## Runtime

**Environment:**
- Python 3.10+ runtime environment (CPython Linux x86_64; Darwin supported for macOS-specific AppleScript integrations)
- Process architecture: Local single-process daemon or CLI runner with standard multi-threaded HTTP server for dashboard ops

**Package Manager:**
- `uv` (version 0.9.18) with pip/wheel compatibility
- Lockfile: `uv.lock` present and tracked in Git

## Frameworks

**Core:**
- Standard Library First: Custom lightweight ReAct loop and workflow engine built on Python stdlib (`dataclasses`, `sqlite3`, `http.server`, `urllib`, `threading`, `subprocess`) rather than bloated agent frameworks like LangChain or CrewAI
- Wire Adapters:
  - Native Anthropic Messages protocol (`anthropic>=0.40`)
  - OpenAI-compatible completion adapter (`openai>=1.50`)
- Build Backend: Hatchling (`hatchling.build`) with dynamic versioning pointed at `sipsup/__init__.py`

**Testing:**
- `pytest` (>=8.0) - Core test runner for deterministic evals in `evals/deterministic/`
- `deepeval` (>=2.0) - LLM evaluation framework used for LLM-as-judge scoring in `evals/judge/`

**Build/Dev:**
- `hatchling` (`hatchling.build`) - PEP 517/518 build system
- `ruff` (`0.16.0` pinned strictly) - Static analysis, linting, and formatting
- `make` (`Makefile`) - Unified command shortcuts for all four pillars (`run`, `voice`, `telegram`, `dashboard`, `gate`)

## Key Dependencies

**Critical:**
- `anthropic` (>=0.40, installed 0.116.0) - Native wire format used for Anthropic, Kimi/Moonshot, GLM/Z.ai, and MiniMax
- `openai` (>=1.50, installed 2.45.0) - Wire format adapter used for OpenAI, Google Gemini, DeepSeek, xAI Grok, OpenRouter, and embeddings
- `python-dotenv` (>=1.0, installed 1.2.2) - Environment configuration loader utilizing `find_dotenv(usecwd=True)`
- `rich` (>=13.0, installed 14.3.4) - Terminal formatting, syntax highlighting, status spinners, and CLI layouts

**Infrastructure & Optional Integrations:**
- `python-telegram-bot` (>=21.0, installed 22.8) - Optional Telegram bot gateway
- `discord.py` (>=2.4) - Optional Discord channel gateway
- `httpx` (>=0.25, installed 0.28.1) - HTTP client for WhatsApp Meta Cloud API gateway and MCP transports
- `google-api-python-client` (>=2.0), `google-auth-oauthlib` (>=1.0) - Optional Google Calendar synchronization
- `faster-whisper` (>=1.0), `sounddevice` (>=0.4), `numpy` (>=1.24) - Local push-to-talk and voice listening
- `kokoro` (>=0.9), `soundfile` (>=0.12) - High-fidelity local neural TTS voice engine (Kokoro-82M, Apache-2.0)
- `mcp` (>=2.1) - Model Context Protocol stdio and Streamable HTTP client integration (`.sipsup/mcp.json`)
- `supabase` (>=2.0) - Optional PostgreSQL / pgvector semantic memory backend
- `notion-client` (>=2.5) - Optional Notion database episodic memory backend (API version 2025-09-03)
- `arize-phoenix` (>=7.0), `opentelemetry-sdk` (>=1.27) - Local trace waterfall server and OTLP trace export
- `mem0ai` (>=2.0), `zep-cloud` (>=2.0), `langmem` (>=0.0.30), `langgraph` (>=0.3) - Memory arena competitive benchmark suites

## Configuration

**Environment:**
- Controlled entirely via environment variables defined in `.env` (template in `.env.example`)
- Configuration loaded at startup via `sipsup.config.Settings` dataclass
- Key configuration variables:
  - `SIPSUP_PROVIDER`: Active model provider (`anthropic`, `openai`, `gemini`, `deepseek`, `kimi`, `minimax`, `glm`, `xai`, `openrouter`)
  - `SIPSUP_MODEL`: Primary model ID for the agent loop
  - `SIPSUP_SMALL_MODEL`: Cheaper model ID for retrieval gate classification and consolidation
  - `SIPSUP_HOME`: Path to agent state directory (default: `.sipsup`)
  - `SIPSUP_MAX_ITERATIONS`: Loop iteration limit guardrail (default: 10)
  - `SIPSUP_MAX_TOKENS`: Max generation tokens per turn, leaving headroom for reasoning models (default: 8192)
  - `SIPSUP_HISTORY_TURNS`: Sliding window size for prompt working memory (default: 12 turns / 24 messages)
  - `SIPSUP_CONSOLIDATE_EVERY`: Exchange frequency for distilling chat history into durable facts (default: 6)
  - `SIPSUP_RETRIEVAL_TOP_K`: Top K facts retrieved by semantic search (default: 4)
  - `SIPSUP_SEMANTIC_STORE`: Semantic memory store choice (`sqlite` or `supabase`, `mem0`, `zep`, `langmem`)
  - `SIPSUP_EPISODIC_STORE`: Episodic memory store choice (`sqlite` or `notion`)

**Build:**
- `pyproject.toml`: Configures project metadata, scripts (`sipsup = sipsup.__main__:main`), hatchling sdist exclusions (`docs/`, `examples/`), and force-includes root `skills/` into wheel package `sipsup/skills`.

## Platform Requirements

**Development:**
- Linux (tested Ubuntu 22.04 LTS / Debian) or macOS (macOS 14+ required for Apple Calendar and Apple Mail integrations)
- Python 3.10+ (Python 3.11+ strongly recommended to natively provide `tomllib` without test suite collection warnings)
- Working audio input/output device for voice gateway
- Optional developer tools: GitHub CLI (`gh`) for PR/issue tools; Node.js/npm for sub-agent delegation (`@earendil-works/pi-coding-agent`)

**Production:**
- Local-first deployment on desktop workstation, laptop, or private edge server
- Persistent filesystem storage for `.sipsup/state.db` and traces
- Outbound HTTPS network access to LLM provider endpoints
- Inbound HTTPS network endpoint or webhook tunnel (e.g. ngrok/Cloudflare Tunnel) only if WhatsApp Meta Cloud API gateway is enabled

---

*Stack analysis: 2026-10-05*
