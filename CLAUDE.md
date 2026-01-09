# CLAUDE.md

## What This Is

ChatGPT App template: React widgets + Python MCP server. Widgets render inside ChatGPT via the Apps SDK.

**Stack:** React/TypeScript (Vite, Tailwind) + Python/FastAPI

**Data flow:** `ChatGPT → MCP tool call → server/main.py → widget HTML + toolOutput → widget reads window.openai.toolOutput`

## File Map

| Path | Purpose |
|------|---------|
| `src/{widget}/` | Widget source (each has `index.tsx` entry point) |
| `src/simulator/` | Local ChatGPT simulator UI (not exposed to real ChatGPT) |
| `src/*.ts` | Shared hooks (`useWidgetProps`, `useWidgetState`, etc.) |
| `server/main.py` | MCP server - tool handlers and widget loading |
| `server/agent_runner.py` | OpenAI Agents SDK integration for simulator |
| `server/simulator_config.json` | Simulator config (model, MCP URL) |
| `build-all.mts:6` | Widget targets array (add new widgets here) |
| `assets/` | Built bundles (generated, don't edit) |

## Commands

```bash
pnpm run build      # Build widgets (required before server)
pnpm run test       # Run all 282 tests
pnpm run server     # Start MCP server at localhost:8000
pnpm run dev        # Dev mode with hot reload
```

## Local Simulator

Test widgets locally without connecting to ChatGPT. **No API key required** - the simulator uses Puter.js as a free fallback.

### Zero-Config Mode (Recommended for AI Agents)

```bash
pnpm run build
pnpm run server
# Open http://localhost:8000/assets/simulator.html
```

The simulator automatically detects when no API key is configured and uses [Puter.js](https://puter.com) - a free browser-based AI for development/testing. No credentials needed to test widgets.

Note: Puter.js is only used in the simulator. In production, the app connects to real ChatGPT which provides the AI.

### Full Mode (With OpenAI API Key)

For production-quality testing with your preferred model:

1. Set `OPENAI_API_KEY` in `.env`
2. Optionally configure model in `server/simulator_config.json`
3. Run `pnpm run server`
4. Open `http://localhost:8000/assets/simulator.html`

**Config file** (`server/simulator_config.json`):
```json
{
  "model": "gpt-4o-mini",
  "mcp_server_url": "http://localhost:8000/mcp",
  "max_conversation_history": 20
}
```

**Note:** The simulator is a dev tool only - it's not registered as an MCP tool and won't appear in real ChatGPT.

## Verification

**IMPORTANT: Always run `pnpm run test` after any code change.**

Tests are infrastructure-only - they pass regardless of widget content or business logic. Use them to verify changes work without connecting to ChatGPT.

## Adding a Widget

1. Create `src/my-widget/index.tsx` targeting `my-widget-root`
2. Add `"my-widget"` to targets in `build-all.mts:6`
3. Add tool handler in `server/main.py` (follow existing patterns)
4. Run `pnpm run build && pnpm run test`
5. Test in simulator: `http://localhost:8000/assets/simulator.html`

## Critical Gotchas

- **Build before server:** `pnpm run build` must complete before `pnpm run server`
- **Restart after rebuild:** Server caches HTML; restart it after rebuilding
- **MIME type:** Widget responses require `mimeType: "text/html+skybridge"`
- **Input models:** All Pydantic `*Input` models must have `extra='forbid'` and default values
- **Simulator vs widgets:** The simulator (`src/simulator/`) is for local dev only - don't add it to `WIDGETS` in `main.py`
