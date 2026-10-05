# Codebase Concerns

**Analysis Date:** 2026-10-05

## Tech Debt

**Google Calendar OAuth Bundled Client Configuration:**
- Issue: Hardcoded empty placeholders in `BUNDLED_CLIENT_CONFIG` marked with a TODO comment.
- Files: `sipsup/tools/google_calendar.py:34-45`
- Impact: Users attempting to use the browser-based Google Calendar consent flow without personal GCP credentials will encounter authorization failures.
- Fix approach: Provision an official desktop OAuth client ID and secret in the Google Cloud Console, or clarify documentation that users must supply their own client credentials in `.env`.

**Unsorted Imports / Ruff Lint Violations:**
- Issue: 11 lint errors flagged by `ruff check` under rule `I001` (unsorted import blocks, e.g. `from datetime import timezone, datetime` instead of alphabetical `datetime, timezone`).
- Files: `sipsup/app.py:7`, `sipsup/integrations.py:8`, `sipsup/ops/dashboard.py:21`, `sipsup/ops/browser_agent.py:26`, `sipsup/ops/tracing.py:20`, `sipsup/tools/experimental.py:31`, `sipsup/tools/messages.py:8`, `sipsup/tools/mcp_cli.py:17`, `evals/deterministic/test_packaging.py:24`, `evals/deterministic/test_version.py:13`
- Impact: CI lint checks will fail unless `ruff check --fix` is applied.
- Fix approach: Run `uv run --extra dev ruff check --fix sipsup evals scripts` to automatically reorder imports.

**Python 3.10 Standard Library `tomllib` Incompatibility in Tests:**
- Issue: `pyproject.toml` declares support for `requires-python = ">=3.10"`, but tests import `tomllib` unconditionally. `tomllib` was introduced in Python 3.11.
- Files: `evals/deterministic/test_packaging.py:25`, `evals/deterministic/test_version.py:14`
- Impact: Running deterministic tests on Python 3.10 fails collection for these two modules with `ModuleNotFoundError: No module named 'tomllib'`.
- Fix approach: Replace direct imports with a conditional fallback:
  ```python
  try:
      import tomllib
  except ImportError:
      import tomli as tomllib
  ```
  and add `tomli` to test dependencies for Python < 3.11.

## Known Bugs

**Test Collection Failure on Python 3.10:**
- Symptoms: `pytest` halts with 2 errors during test collection.
- Files: `evals/deterministic/test_packaging.py`, `evals/deterministic/test_version.py`
- Trigger: Running `pytest evals/deterministic` on any Python 3.10.x runtime.
- Workaround: Execute tests under Python 3.11 or Python 3.12, or install `tomli`.

## Security Considerations

**Subprocess Invocations in Apple Tools and Sub-Agent Delegation:**
- Risk: User input or model-generated arguments passed to shell/subprocess commands could present command injection vectors if sanitization fails.
- Files: `sipsup/tools/apple.py`, `sipsup/tools/experimental.py`, `sipsup/tools/github.py`
- Current mitigation: AppleScript commands format strings with basic quoting; Pi delegation passes arguments via array lists in `subprocess.Popen`.
- Recommendations: Avoid shell execution strings, enforce strict character allowlists for workspace folder names, and sanitize all arguments passed to `osascript`.

**Channel Gateway Permissiveness:**
- Risk: Running Telegram, Discord, or WhatsApp gateways without explicit allowlists can expose the local agent, disk tools, and API keys to arbitrary internet senders.
- Files: `sipsup/gateway/telegram.py`, `sipsup/gateway/discord.py`, `sipsup/gateway/whatsapp.py`
- Current mitigation: Filters check `TELEGRAM_ALLOWED_USER`, `DISCORD_ALLOWED_USER`, `WHATSAPP_ALLOWED_PHONE`.
- Recommendations: Refuse gateway startup if allowlist variables are empty, rather than defaulting to open access.

## Performance Bottlenecks

**Synchronous Memory Consolidation Latency:**
- Problem: Periodic memory consolidation runs synchronously inside `SipSup.respond()`.
- Files: `sipsup/app.py:108`, `sipsup/memory/consolidation.py`
- Cause: Every Nth exchange (`SIPSUP_CONSOLIDATE_EVERY=6`), the agent triggers an additional LLM call to summarize recent chats and extract facts before returning the reply.
- Improvement path: Offload `maybe_consolidate()` to a background daemon thread or asynchronous task so turn latency remains consistent.

**SQLite Concurrency and Lock Contention:**
- Problem: Potential `sqlite3.OperationalError: database is locked`.
- Files: `sipsup/db.py:104`, `sipsup/ops/dashboard.py`
- Cause: Multiple concurrent components (the dashboard HTTP server, background consolidation, active chat sessions) sharing `.sipsup/state.db`.
- Improvement path: Enable WAL (Write-Ahead Logging) mode (`PRAGMA journal_mode=WAL;`) during connection initialization.

## Fragile Areas

**Upstream LLM Provider Model ID Drift:**
- Files: `sipsup/loop/models.py`
- Why fragile: AI providers regularly deprecate model aliases (e.g. OpenAI deprecated `-chat-latest`, Gemini deprecated `-pro` aliases in favor of preview tags).
- Safe modification: Update `PROVIDERS` dictionary and verify tool calling capability against the provider before deploying.
- Test coverage: Guarded by `evals/deterministic/test_models.py` and `evals/deterministic/test_pinned_models.py`.

**Dashboard Shared State and Connection Locking:**
- Files: `sipsup/ops/dashboard.py`, `sipsup/ops/browser_agent.py`
- Why fragile: Dashboard reuses a single agent and database connection across multiple HTTP handler threads guarded by a coarse `agent_lock`. A hanging LLM call blocks all dashboard UI routes.
- Safe modification: Ensure all operations acquire `agent_lock` with timeouts or use separate read-only database connections for stats/session listing.

## Scaling Limits

**Local-First Single User Architecture:**
- Current capacity: Single active user on a personal laptop or workstation (~10-20 turns/minute).
- Limit: SQLite file locking and single-process Python execution break under multi-user concurrent write loads.
- Scaling path: Transition from local SQLite to client-server database (e.g. PostgreSQL + Supabase pgvector) and isolate sessions per worker.

## Dependencies at Risk

**Unpinned Optional Gateway Dependencies:**
- Package: `python-telegram-bot>=21.0`, `discord.py>=2.4`
- Risk: Non-breaking minor releases can introduce breaking API changes over time.
- Impact: Gateway bots may fail to start or crash during event handling.
- Migration plan: Pin exact or tight minor version bounds in `pyproject.toml` (similar to how `ruff==0.16.0` is pinned).

**Heavy Neural Voice Dependencies:**
- Package: `kokoro>=0.9`, `torch`
- Risk: Installing `.[voice-neural]` downloads multi-gigabyte PyTorch binaries, which may fail on bandwidth-constrained or resource-limited edge hardware.
- Migration plan: Keep neural voice as an optional extra; default to OS-native TTS (macOS `say` or lightweight eSpeak).

## Missing Critical Features

**Native Local Vector Embedding Search:**
- Problem: Out-of-the-box semantic search relies entirely on SQLite FTS5 keyword matching. True semantic vector similarity requires configuring external Supabase pgvector and OpenAI API keys.
- Blocks: Semantic retrieval of conceptually similar memories that lack exact keyword matches when operating purely offline.

## Test Coverage Gaps

**Real Audio Hardware and Microphone Gateways:**
- What's not tested: Real microphone capture, sounddevice buffer streaming, and Whisper speech recognition in live environments.
- Files: `sipsup/gateway/voice.py`
- Risk: Audio device incompatibility, sample rate mismatches, or ALSA/CoreAudio driver crashes.
- Priority: Medium

**Live WhatsApp Meta Webhook Integration:**
- What's not tested: End-to-end webhook handshake with Meta Graph API servers over public HTTPS.
- Files: `sipsup/gateway/whatsapp.py`
- Risk: Meta API schema changes or header signature mismatch unnoticed until live deployment.
- Priority: Medium

---

*Concerns audit: 2026-10-05*
