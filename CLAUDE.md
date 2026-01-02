# CLAUDE.md

## What This Is

ChatGPT App template: React widgets + Python MCP server. Widgets render inside ChatGPT via the Apps SDK.

**Stack:** React/TypeScript (Vite, Tailwind) + Python/FastAPI

**Data flow:** `ChatGPT → MCP tool call → server/main.py → widget HTML + toolOutput → widget reads window.openai.toolOutput`

## File Map

| Path | Purpose |
|------|---------|
| `src/{widget}/` | Widget source (each has `index.tsx` entry point) |
| `src/*.ts` | Shared hooks (`useWidgetProps`, `useWidgetState`, etc.) |
| `server/main.py` | MCP server - tool handlers and widget loading |
| `build-all.mts:6` | Widget targets array (add new widgets here) |
| `assets/` | Built bundles (generated, don't edit) |

## Commands

```bash
pnpm run build      # Build widgets (required before server)
pnpm run test       # Run all 272 tests
pnpm run server     # Start MCP server at localhost:8000
pnpm run dev        # Dev mode with hot reload
```

## Verification

**IMPORTANT: Always run `pnpm run test` after any code change.**

Tests are infrastructure-only - they pass regardless of widget content or business logic. Use them to verify changes work without connecting to ChatGPT.

## Adding a Widget

1. Create `src/my-widget/index.tsx` targeting `my-widget-root`
2. Add `"my-widget"` to targets in `build-all.mts:6`
3. Add tool handler in `server/main.py` (follow existing patterns)
4. Run `pnpm run build && pnpm run test`

## Critical Gotchas

- **Build before server:** `pnpm run build` must complete before `pnpm run server`
- **Restart after rebuild:** Server caches HTML; restart it after rebuilding
- **MIME type:** Widget responses require `mimeType: "text/html+skybridge"`
- **Input models:** All Pydantic `*Input` models must have `extra='forbid'` and default values
