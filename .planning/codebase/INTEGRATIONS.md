# External Integrations

**Analysis Date:** 2026-10-05

## APIs & External Services

**AI & LLM Providers:**
- **Anthropic:** Primary native model provider (Claude Sonnet 5, Opus 4.8, Haiku 4.5)
  - SDK/Client: `anthropic` Python SDK (`sipsup/loop/models.py`)
  - Auth: `ANTHROPIC_API_KEY` or `SIPSUP_API_KEY`
- **OpenAI:** GPT models (GPT-5.5, GPT-4.1-mini) and embeddings provider
  - SDK/Client: `openai` Python SDK (`sipsup/loop/models.py`)
  - Auth: `OPENAI_API_KEY` or `SIPSUP_API_KEY`
- **Google Gemini:** Gemini models via OpenAI compatibility layer
  - Endpoint: `https://generativelanguage.googleapis.com/v1beta/openai/`
  - SDK/Client: `openai` Python SDK
  - Auth: `GEMINI_API_KEY`
- **DeepSeek:** DeepSeek models (DeepSeek-V4-Pro)
  - Endpoint: `https://api.deepseek.com`
  - SDK/Client: `openai` Python SDK
  - Auth: `DEEPSEEK_API_KEY`
- **Moonshot AI (Kimi):** Kimi reasoning models (Kimi-K3, Kimi-K2.6)
  - Endpoint: `https://api.moonshot.ai/anthropic` (Global) or `https://api.moonshot.cn/anthropic` (China)
  - SDK/Client: `anthropic` Python SDK (Anthropic wire format)
  - Auth: `MOONSHOT_API_KEY`, `MOONSHOT_BASE_URL`
- **MiniMax:** MiniMax models (MiniMax-M3, MiniMax-M2)
  - Endpoint: `https://api.minimaxi.com/anthropic` or `https://api.minimax.io/anthropic`
  - SDK/Client: `anthropic` Python SDK
  - Auth: `MINIMAX_API_KEY`, `MINIMAX_BASE_URL`
- **Zhipu AI (GLM):** GLM models (GLM-5.2, GLM-5-Turbo)
  - Endpoint: `https://api.z.ai/api/anthropic` or `https://open.bigmodel.cn/api/anthropic`
  - SDK/Client: `anthropic` Python SDK
  - Auth: `ZHIPU_API_KEY`, `ZHIPU_BASE_URL`
- **xAI:** Grok models (Grok-4, Grok-4-fast)
  - Endpoint: `https://api.x.ai/v1`
  - SDK/Client: `openai` Python SDK
  - Auth: `XAI_API_KEY`
- **OpenRouter:** Universal aggregator offering commercial models and free tier (`nvidia/nemotron-3-super-120b-a12b:free`, `google/gemma-4-26b-a4b-it:free`)
  - Endpoint: `https://openrouter.ai/api/v1`
  - SDK/Client: `openai` Python SDK
  - Auth: `OPENROUTER_API_KEY`
- **OpenCode:** Free and fast platform models (DeepSeek-V4-flash variants)
  - Endpoints: `https://opencode.ai/zen/v1` and `https://opencode.ai/zen/go/v1`
  - SDK/Client: `openai` Python SDK
  - Auth: `OPENCODE_ZEN_API_KEY`, `OPENCODE_GO_API_KEY`

**Communication Channels (Gateways):**
- **Telegram Bot:** Two-way messaging bridge (`sipsup/gateway/telegram.py`)
  - SDK/Client: `python-telegram-bot`
  - Auth: `TELEGRAM_BOT_TOKEN`, filtered by `TELEGRAM_ALLOWED_USER`
- **Discord Bot:** Server channel bridge (`sipsup/gateway/discord.py`)
  - SDK/Client: `discord.py`
  - Auth: `DISCORD_BOT_TOKEN`, filtered by `DISCORD_ALLOWED_USER`, `DISCORD_ALLOWED_CHANNEL`
- **WhatsApp Cloud API:** Two-way messaging bridge via Meta Graph API (`sipsup/gateway/whatsapp.py`)
  - SDK/Client: `httpx` HTTP client
  - Auth: `WHATSAPP_TOKEN`, `WHATSAPP_PHONE_NUMBER_ID`, `WHATSAPP_APP_SECRET`, `WHATSAPP_VERIFY_TOKEN`, `WHATSAPP_ALLOWED_PHONE`

**Calendar & Productivity Services:**
- **Google Calendar:** Write-through synchronization for created events (`sipsup/tools/google_calendar.py`)
  - SDK/Client: `google-api-python-client`, `google-auth-oauthlib`
  - Auth: OAuth2 browser consent flow; cached in `.sipsup/google_calendar_token.json`
- **Apple Calendar & Workspace Tools:** Local macOS Calendar, Reminders, Notes, and Mail (`sipsup/tools/apple.py`)
  - SDK/Client: Subprocess dispatching AppleScript via `/usr/bin/osascript`
  - Auth: macOS system automation permission prompts
- **GitHub:** Repository search, issues, and PR inspection (`sipsup/tools/github.py`)
  - SDK/Client: Subprocess dispatching local `gh` CLI
  - Auth: Existing authenticated `gh auth login` token on host system
- **Web Search (Tavily):** Real-time web search (`sipsup/tools/search.py`)
  - SDK/Client: `urllib.request` REST client
  - Auth: `TAVILY_API_KEY`
- **Sub-Agent Delegation (Pi):** Local autonomous sub-agent runner (`sipsup/tools/experimental.py`)
  - SDK/Client: Subprocess executing `@earendil-works/pi-coding-agent` CLI
  - Auth: Inherits host environment API keys
- **Model Context Protocol (MCP):** Connects external tool servers (`sipsup/tools/mcp_client.py`)
  - Transports: Local subprocess stdio or remote Streamable HTTP via `httpx`
  - Configuration: Loaded from `.sipsup/mcp.json`

## Data Storage

**Databases:**
- **Local SQLite (Default):**
  - Path: `.sipsup/state.db`
  - Client: Python standard library `sqlite3`
  - Features: WAL mode support, FTS5 virtual tables (`facts_fts`, `episodes_fts`), automatic schema migrations in `sipsup/db.py`
- **Supabase (pgvector - Optional Semantic Memory):**
  - Endpoint: Configured via `SUPABASE_URL`
  - Client: `supabase` Python client (`sipsup/memory/semantic/supabase_store.py`)
  - Auth: `SUPABASE_SERVICE_KEY`, plus `OPENAI_API_KEY` for vector embeddings
- **Notion (Optional Episodic Memory):**
  - Client: `notion-client` (`sipsup/memory/episodic/notion_store.py`)
  - Auth: `NOTION_TOKEN`, targeted database `NOTION_EPISODES_DATABASE_ID`
- **Hosted Memory Arena Backends (Benchmarking):**
  - Mem0: `mem0ai` client, `MEM0_API_KEY`
  - Zep: `zep-cloud` client, `ZEP_API_KEY`
  - LangMem: `langmem` client, `OPENAI_API_KEY`, optional `SIPSUP_LANGMEM_POSTGRES`

**File Storage:**
- Local filesystem only (`.sipsup/` directory by default):
  - State database: `.sipsup/state.db`
  - Human-readable memory mirror: `.sipsup/MEMORY.md` (regenerated after every turn)
  - ICS calendar export: `.sipsup/calendar.ics`
  - Outbox mail mock: `.sipsup/outbox/`
  - Workspace directory: `.sipsup/workspace/`

**Caching:**
- In-memory process cache for provider model catalogs (`sipsup/ops/catalog.py`) with disk backup at `.sipsup/models_cache.json`
- Integration connection health cache at `.sipsup/connections_health.json`

## Authentication & Identity

**Auth Provider:**
- No user accounts or external identity provider for core agent operation (single-tenant local user model)
- Channel Gateways: Authenticate incoming senders via allowlists (`TELEGRAM_ALLOWED_USER`, `DISCORD_ALLOWED_USER`, `WHATSAPP_ALLOWED_PHONE`)
- Third-party APIs: Individual API bearer tokens or OAuth2 refresh tokens

## Monitoring & Observability

**Error Tracking:**
- No external crash reporter or telemetry phone-home service (strict local-first privacy)
- Exceptions in tools or observers are captured into turn metadata or trace events without crashing the loop

**Logs & Traces:**
- **Local JSONL Tracing:** Every turn, LLM prompt/response, tool execution, and timing is logged to `.sipsup/traces/trace-YYYY-MM-DD.jsonl` via `sipsup/ops/tracing.py`
- **OpenTelemetry / Arize Phoenix:** Optional OTLP trace export configured via `OTEL_EXPORTER_OTLP_ENDPOINT` (or viewed locally via `make trace` on port 6006)
- **Web Dashboard:** Embedded management UI served at `http://localhost:7777` (`sipsup/ops/dashboard.py`)

## CI/CD & Deployment

**Hosting:**
- Self-hosted local daemon or personal server execution (`python -m sipsup`)
- No cloud hosting required

**CI Pipeline:**
- GitHub Actions workflow (`.github/workflows/`) validating code formatting, skill definitions (`scripts/validate_skills.py`), deterministic evals, and packaging checks

## Environment Configuration

**Required env vars:**
- One active LLM provider key:
  - `ANTHROPIC_API_KEY` (if `SIPSUP_PROVIDER=anthropic`) OR
  - `OPENAI_API_KEY` (if `SIPSUP_PROVIDER=openai`) OR
  - Equivalent key for configured provider (`GEMINI_API_KEY`, `DEEPSEEK_API_KEY`, `MOONSHOT_API_KEY`, `OPENROUTER_API_KEY`, etc.)

**Key Optional vars:**
- `SIPSUP_PROVIDER` (default: `anthropic`)
- `SIPSUP_MODEL` / `SIPSUP_SMALL_MODEL`
- `SIPSUP_HOME` (default: `.sipsup`)
- `TELEGRAM_BOT_TOKEN`, `DISCORD_BOT_TOKEN`, `WHATSAPP_TOKEN` (for channel gateways)
- `TAVILY_API_KEY` (for web search)
- `OTEL_EXPORTER_OTLP_ENDPOINT` (for OpenTelemetry tracing)

**Secrets location:**
- Stored exclusively in local `.env` file (git-ignored)
- Discovered automatically from current working directory or upward ancestry via `sipsup.config._load_env()`

## Webhooks & Callbacks

**Incoming:**
- **WhatsApp Webhook:** Handled by `sipsup/gateway/whatsapp.py`:
  - `GET /webhook` - Meta verification handshake (`hub.challenge`, `hub.verify_token`)
  - `POST /webhook` - Inbound message payloads with HMAC-SHA256 signature verification (`X-Hub-Signature-256`)

**Outgoing:**
- None (outgoing actions are synchronous client HTTP requests or stdio tool invocations)

---

*Integration audit: 2026-10-05*
