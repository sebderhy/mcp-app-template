# AGENTS.md

MCP App template: React widgets + Python MCP server. Apps render in MCP hosts (Claude, ChatGPT, VS Code, Goose) via the MCP Apps protocol.

## Commands

```bash
./setup.sh           # First-time setup (installs deps, builds, tests)
pnpm run build       # Build widgets (REQUIRED before server)
pnpm run test        # Server + UI tests (run after every change)
pnpm run test:all    # All tests including browser (requires Playwright)
pnpm run server      # Start MCP server at localhost:8000
pnpm run ui-test --widget <name>  # Visual test a widget
```

**Workflow:** `pnpm run build && pnpm run test && pnpm run ui-test --widget <name>`

**Thorough check:** `pnpm run build && pnpm run test:all`

## File Structure

| Path | Purpose |
|------|---------|
| `src/{widget}/index.tsx` | Widget entry point |
| `src/*.ts` | Shared hooks (useWidgetProps, useTheme, useHostGlobal) |
| `internal/apptester/` | App tester UI (infrastructure - do not modify) |
| `internal/sandbox-proxy/` | Sandbox proxy (infrastructure - do not modify) |
| `server/main.py` | MCP server - tools and handlers |
| `build-all.mts` | Build script (auto-discovers `src/*/index.tsx` and `internal/*/index.tsx`) |
| `tests/*.test.ts` | UI unit tests (Vitest) |
| `tests/browser/*.spec.ts` | Browser compliance tests (Playwright) |
| `server/tests/test_*.py` | Server tests and grading (pytest) |

## Critical Rules

- **Build before server:** `pnpm run build` must complete before `pnpm run server`
- **Input models:** All Pydantic `*Input` models MUST have `extra='forbid'` and defaults
- **Theme support:** Widgets MUST work in both light and dark modes
- **Test after changes:** ALWAYS run `pnpm run test` after any code change
- **MCP best practices:** Tests grade the server against MCP guidelines (run `pnpm run test` to generate `server/tests/mcp_best_practices_report.txt`)
- **MCP Apps compliance:** Tests grade against MCP Apps protocol (generates `server/tests/mcp_apps_compliance_report.txt`)
- **Output quality:** Tests grade tool output quality - schema stability, null handling, response size (generates `server/tests/output_quality_report.txt`)

## Documentation

Read these before building:

- `docs/README.md` - Step-by-step walkthrough for adding widgets (start here)
- `docs/what-makes-a-great-chatgpt-app.md` - Know/Do/Show framework, capability design, conversation patterns (OpenAI guidance)
- `docs/widget-development.md` - Project-specific hooks (`useWidgetProps`, `useTheme`, `useHostGlobal`), patterns
- `docs/mcp-development-guidelines.md` - MCP best practices (tool naming, descriptions, error handling)
- `docs/mcp-apps-docs.md` - MCP Apps overview, getting started, examples
- `docs/mcp-apps-specs.mdx` - MCP Apps protocol specification (SEP-1865) - message formats, lifecycle, security

## Adding a Widget

1. Create `src/my-widget/index.tsx` with React component
2. Add Input model, Widget config, and handler in `server/main.py`
3. Run `pnpm run build && pnpm run test && pnpm run ui-test --widget my-widget`

## ⚠️ DO NOT Modify Infrastructure

**Never modify or delete:** `internal/apptester/`, `internal/sandbox-proxy/`, `src/use-*.ts` hooks, `tests/browser/apptester-e2e.spec.ts`

These are the testing framework (not example widgets). Modifying them breaks the entire development workflow even if tests pass. Only modify: widget folders (`src/my-widget/`) and `server/main.py` handlers.

## Finalizing Your App

After building your widgets, remove the template examples:

1. Delete example widget folders from `src/` (boilerplate, carousel, list, gallery, dashboard, solar-system, todo, shop)
2. Remove example Input models, Widget configs, and handlers from `server/main.py`
4. Remove unused dependencies from `package.json` (e.g., `three`, `@react-three/*` if not using 3D)
5. Run `pnpm install && pnpm run build && pnpm run test:all` to verify everything works

See `docs/README.md` for the detailed cleanup checklist.

## Local App Tester

```bash
pnpm run build && pnpm run server
# Open http://localhost:8000/assets/apptester.html
```

No API key required - uses Puter.js fallback for testing.

## Testing with MCP Hosts

### Claude (Web or Desktop)
Expose your local server via a tunnel, then add as a custom connector:
```bash
pnpm run server  # Terminal 1
npx cloudflared tunnel --url http://localhost:8000  # Terminal 2
```
Add the tunnel URL as a custom connector in Claude settings.

### MCP Apps Basic Host
Clone the ext-apps repo and run the basic-host test interface:
```bash
git clone https://github.com/modelcontextprotocol/ext-apps
cd ext-apps/examples/basic-host
npm install && SERVERS='["http://localhost:8000"]' npm start
```

## Browser Compliance Tests

Browser tests (`tests/browser/*.spec.ts`) run each widget in a real Chromium browser:

| Test | What it catches |
|------|-----------------|
| No JS errors | Syntax errors, missing imports, runtime exceptions |
| Renders content | Empty widgets, failed hydration |
| Dark theme works | Theme-specific bugs, hardcoded colors |
| No unhandled rejections | Async errors, failed API calls |
| Images have alt text | Accessibility issues for screen readers |
| No duplicate IDs | HTML validity issues |
| callTool invocations callable | Widget calls tools that don't exist on server |
| Text contrast (warning) | WCAG AA contrast ratio violations |
| Keyboard accessible (warning) | Missing tabindex or ARIA roles |

Setup (one-time):
```bash
pnpm run setup:test              # Install Playwright browsers
npx playwright install-deps      # Install system deps (may need sudo)
```

Run: `pnpm run test:browser`

Tests auto-discover widgets from `/tools` endpoint and skip gracefully if browser dependencies aren't installed.

## VPS / Remote Deployment

When running on a VPS or accessing via public IP, set `BASE_URL`:

```bash
BASE_URL=http://YOUR_IP:8000/assets pnpm run server
```

Or use a `.env` file at the repo root (see `.env.example`).
