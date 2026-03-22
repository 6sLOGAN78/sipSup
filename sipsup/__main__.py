"""Entrypoints — installed as the `sipsup` command (and `python -m sipsup`):

  sipsup                       chat in the terminal (default)
  sipsup dashboard             the browser cockpit → localhost:7777 (+ Telegram if configured)
  sipsup connections           list configured integrations and their health
  sipsup mcp                   MCP servers, and which account each knows you as
  sipsup mcp login <name>      sign in again — as someone else, or after expiry
  sipsup voice                 talk to it (needs the [voice] extra)
  sipsup telegram              phone → laptop (needs TELEGRAM_BOT_TOKEN)
  sipsup discord               Discord → laptop (needs DISCORD_BOT_TOKEN)
  sipsup whatsapp              WhatsApp → laptop (needs WHATSAPP_TOKEN, public URL)
  sipsup brief                 morning briefing (calendar + mail + memory) — as a LOOP
  sipsup gather                same job as a GRAPH: github, web, calendar and
                             memory fetched together, then one digest
  sipsup skill install <url>   install a community skill
"""

from __future__ import annotations

import sys


def _tolerant_stdio() -> None:
    """Windows consoles default to a legacy codepage (cp1252) that cannot
    encode the arrows and middots in our output — printing the dashboard
    banner would crash with UnicodeEncodeError before the server even
    started. Keep the console's encoding but replace what it can't show."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(errors="replace")
        except (AttributeError, ValueError):
            pass  # not a real console stream (tests, pipes) — leave it alone


def main() -> None:
    _tolerant_stdio()
    args = sys.argv[1:]
    if not args:
        from sipsup.gateway.cli import main as cli_main

        cli_main()
    elif args[0] == "dashboard":
        from sipsup.ops.dashboard import main as dash_main

        dash_main()
    elif args[0] == "connections":
        from sipsup.integrations import cli_main

        sys.exit(cli_main())
    elif args[0] == "voice":
        from sipsup.gateway.voice import main as voice_main

        voice_main()
    elif args[0] == "telegram":
        from sipsup.gateway.telegram import main as tg_main

        tg_main()
    elif args[0] == "discord":
        from sipsup.gateway.discord import main as discord_main

        discord_main()
    elif args[0] == "whatsapp":
        from sipsup.gateway.whatsapp import main as wa_main

        wa_main()
    elif args[0] == "brief":
        from sipsup.ops.brief import main as brief_main

        brief_main()
    elif args[0] == "gather":
        from sipsup.ops.gather import main as gather_main

        gather_main()
    elif args[0] == "mcp":
        from sipsup.tools.mcp_cli import cli_main as mcp_main

        sys.exit(mcp_main())
    elif args[0] == "skill" and len(args) >= 3 and args[1] == "install":
        from sipsup.memory.procedural.installer import install

        install(args[2])
    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
