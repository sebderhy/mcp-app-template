# MCP App Template - Docs Index

A documentation index and quality checklist for building widgets with this template. Works with any MCP Apps host (Claude, ChatGPT, VS Code, Goose, etc.).

For the step-by-step workflow, see the main [CLAUDE.md](../CLAUDE.md) (or `AGENTS.md`).

---

## Documentation Overview

| Document | What it covers |
|----------|----------------|
| [widget-development.md](./widget-development.md) | Project-specific hooks (`useWidgetProps`, `useTheme`, `useWidgetState`), patterns |
| [mcp-development-guidelines.md](./mcp-development-guidelines.md) | Tool naming, descriptions, error handling, security |
| [what-makes-a-great-chatgpt-app.md](./what-makes-a-great-chatgpt-app.md) | Know/Do/Show framework, capability design (OpenAI guidance) |
| [mcp-apps-docs.md](./mcp-apps-docs.md) | MCP Apps overview, getting started, examples |
| [mcp-apps-specs.mdx](./mcp-apps-specs.mdx) | MCP Apps protocol specification (SEP-1865) - message formats, lifecycle, security |
| [openai-apps-sdk-llms-full.txt](./openai-apps-sdk-llms-full.txt) | OpenAI Apps SDK documentation reference |

---

## Quick Start

See [CLAUDE.md](../CLAUDE.md) for the complete workflow:

1. `./setup.sh` — Setup and verify
2. Read `README.md` and `docs/widget-development.md`
3. Review the `carousel` example (`src/carousel/` + `server/widgets/carousel.py`)
4. `./create_new_app.sh --name my_app` — Create your app
5. Development loop: create widget → `pnpm run build && pnpm run test` → `pnpm run ui-test --tool show_name`
6. `pnpm run test:browser` — Final verification

---

## Pre-Submission Checklist

Before deploying to MCP Apps hosts, verify:

### MCP Server
- [ ] Tool names use `verb_noun` format (e.g., `show_carousel`)
- [ ] All tools have rich descriptions with Args, Returns, Example
- [ ] Error messages suggest next steps
- [ ] Input models have `extra='forbid'` and defaults
- [ ] Check grade reports after `pnpm run test`:
  - `server/tests/mcp_best_practices_report.txt`
  - `server/tests/chatgpt_app_guidelines_report.txt`
  - `server/tests/output_quality_report.txt`

### Widget UX
- [ ] Supports both light and dark themes
- [ ] No nested scrolling in cards
- [ ] Max 2 primary actions per card
- [ ] Carousel has 3-8 items with images
- [ ] Uses system colors and fonts

### Testing
- [ ] `pnpm run test` passes
- [ ] `pnpm run ui-test --tool show_<name>` shows correct rendering
- [ ] `pnpm run test:browser` passes
- [ ] Tested in app tester with real prompts

---

## Finalizing Your App

After building your widgets, remove the template examples. The easiest way:

```bash
./create_new_app.sh --name my_app --keep my-widget
```

This script automatically:
- Removes example widget folders from `src/`
- Removes example server modules from `server/widgets/`
- Cleans unused dependencies from `package.json`
- Runs build and tests to verify

### Manual Cleanup (if needed)

**Widget source folders** (`src/`):
- [ ] `boilerplate/`
- [ ] `carousel/`
- [ ] `list/`
- [ ] `gallery/`
- [ ] `dashboard/`
- [ ] `solar-system/`
- [ ] `todo/`
- [ ] `shop/`
- [ ] `qr/`
- [ ] `scenario-modeler/`
- [ ] `system-monitor/`
- [ ] `map/`

**Server widget modules** (`server/widgets/`):
- [ ] Remove corresponding `*.py` files for deleted widgets

**Dependencies** (`package.json`):
- [ ] Remove `three`, `@react-three/fiber`, `@react-three/drei`, `@react-three/postprocessing`, `@react-spring/three` if not using 3D
- [ ] Remove `@types/three` from devDependencies if not using 3D
- [ ] Remove `chart.js` if not using charts
- [ ] Remove `framer-motion` if not using animations
- [ ] Remove any other unused dependencies

### Final Verification

```bash
pnpm install           # Update lockfile after dependency changes
pnpm run build         # Build your widgets
pnpm run test:all      # All tests (server, UI, browser)
```

---

## Troubleshooting

### Widget not rendering
1. Check `pnpm run build` completed successfully
2. Check browser console for errors (F12 → Console)
3. Verify widget has `src/<name>/index.tsx` entry point
4. Verify the element ID matches: `document.getElementById("<name>-root")`

### Tool not appearing in MCP host
1. Check server module exists: `server/widgets/<name>.py`
2. Verify module exports `WIDGET`, `INPUT_MODEL`, and `handle()`
3. Check for Python syntax errors: `pnpm run test:server`
4. Restart the server after adding new widgets

### Tests failing
1. Ensure `extra='forbid'` on all Input models
2. Check all Input fields have defaults
3. Verify widget HTML exists in `assets/` (run `pnpm run build`)
4. Check `component_name` in Widget matches the folder name in `src/`

### Visual test shows wrong content
1. Run `pnpm run build` to rebuild widgets
2. Check `/tmp/ui-test/console.log` for errors
3. Verify `structuredContent` in handler matches widget's `useWidgetProps` type
