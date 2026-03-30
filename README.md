# sipsup 🥤

yo this is sipsup. it's my personal ai assistant running entirely on my local machine. hooks into my stuff, remembers what i tell it, and just gets things done without the bloat.

## what it does
- streams tokens insanely fast using openrouter
- persistent local memory (sqlite) so it actually remembers shit
- has a fast routing graph for simple questions so it doesn't waste time
- handles web search, tools, and workflows natively

## how to run
grab `uv`, clone this down, and set it up:

```bash
uv venv
source .venv/bin/activate
uv pip install -e .
```

throw your keys in a `.env` file:
```env
SIPSUP_PROVIDER=openrouter
SIPSUP_MODEL=anthropic/claude-3-haiku
OPENROUTER_API_KEY=your_key
TAVILY_API_KEY=your_key
```

### spin it up
for the web dashboard:
```bash
make dashboard
```
then hit up `http://localhost:7777`.

or if you just want the terminal:
```bash
python -m sipsup.gateway.cli
```

that's pretty much it.
