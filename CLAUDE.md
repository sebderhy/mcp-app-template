# CLAUDE.md

This file provides guidance to Claude Code when working with this ChatGPT App boilerplate.

## Overview

This is a boilerplate for building ChatGPT Apps using the Apps SDK. It includes:
- React widgets (TypeScript) that render inside ChatGPT
- Python MCP server (FastAPI) that handles tool calls
- Build tooling (Vite, Tailwind) for widget bundling

## Key Architecture Pattern

```
ChatGPT → MCP Tool Call → Python Server → structuredContent + widget HTML
                                                    ↓
                                          Widget reads window.openai.toolOutput
```

## Development Commands

```bash
# Build widgets (required before running server)
pnpm run build

# Start Python MCP server (also serves widget assets)
pnpm run server

# Local development with hot reload
pnpm run dev
```

## File Structure

- `src/` - Widget source code (React + TypeScript)
- `src/boilerplate/` - Main boilerplate widget
- `src/*.ts` - Shared hooks for window.openai integration
- `server/main.py` - Python MCP server
- `assets/` - Built widget bundles (generated)

## Adding New Widgets

1. Create `src/my-widget/index.tsx` and `src/my-widget/App.tsx`
2. Add "my-widget" to `targets` array in `build-all.mts`
3. Add corresponding tools in `server/main.py`
4. Run `pnpm run build`

## Key Files to Modify

- `src/boilerplate/App.tsx` - Main widget UI
- `server/main.py` - Tool definitions and handlers
- `build-all.mts` - Add new widget targets

## Important Notes

- Always run `pnpm run build` before starting the Python server
- Restart Python server after rebuilding (LRU cache)
- Widget HTML must have `mimeType: "text/html+skybridge"`
- Use `window.openai.*` for ChatGPT host communication
