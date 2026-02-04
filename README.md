# MCP App Template

**The AI-agent-first MCP App template.** Built so coding agents (Claude Code, Codex, Cursor, ...) can modify, test, and go as far as possible autonomously - without human in the loop.

Works with any MCP Apps host: **Claude**, **ChatGPT**, **VS Code**, **Goose**, and many more to come.

## What are MCP Apps?

![MCP Apps - Build once, run on ChatGPT, Claude, Gemini & more](./images/infographic_mcp_apps.png)
*credit: image generated using [Nano Banana](https://ai.google.dev/gemini-api/docs/image-generation)*

[MCP Apps](https://modelcontextprotocol.io/docs/extensions/apps) are an extension to the [Model Context Protocol](https://modelcontextprotocol.io/) that let MCP servers return **interactive UIs** -- React widgets rendered directly inside AI hosts like ChatGPT, Claude, VS Code, and so on... Instead of tools returning plain text, they return rich, interactive experiences displayed in sandboxed iframes within the conversation.

This is a **platform shift**. AI chatbots are becoming app platforms -- ChatGPT alone has [800M+ weekly users](https://openai.com/index/introducing-apps-in-chatgpt/), and apps now run inside that distribution channel. One MCP server works across every host. 

For more context, see the [MCP Apps blog post](http://blog.modelcontextprotocol.io/posts/2025-11-21-mcp-apps/) and the [protocol specification (SEP-1865)](https://github.com/modelcontextprotocol/ext-apps/blob/main/specification/draft/apps.mdx).

## Why This Template?

Most templates assume a human developer. This one is designed for AI agents to work as much as possible autonomously:

### 1. Orthogonal Test Suite
~220 shared tests verify infrastructure (MCP Apps compliance, protocol format, accessibility, browser rendering) — not your business logic. Another ~18 tests per widget are auto-discovered (input validation, build output, browser rendering) — you never write them, they appear automatically when you add a widget. Modify widgets, change data, add features — tests still pass. Automated grading generates reports with actionable `FIX:` hints to steer coding agents.

### 2. Hierarchical Documentation
`AGENTS.md` for quick onboarding → `docs/README.md` for a step-by-step building guide → deep docs covering MCP best practices, widget patterns, and complete SDK reference (`llms-full.txt`).

### 3. Automated Visual Testing
AI agents can test widgets and capture screenshots - no API key required:
```bash
pnpm run ui-test --tool show_carousel  # Renders tool, saves screenshot
```
Agents read `/tmp/ui-test/screenshot.png` to verify their changes work.

### 4. Zero-Config App Tester
Local app tester for manual testing - works instantly without API key via [Puter.js](https://puter.com). Add an OpenAI key for AI-in-the-loop testing.

### 5. Working Examples
12 production-ready widgets demonstrating state management, theming, 3D visualization, drag-and-drop, real-time monitoring, and more.

## Demos
### Claude Code autonomously building an app **end-to-end** from the template
https://github.com/user-attachments/assets/407393de-c9d8-4da3-b541-54b8b9a2d7dc

### Showcase of widgets within ChatGPT
https://github.com/user-attachments/assets/f5877544-0dce-4c31-979e-50b5533f9a16

## Quick Start

```bash
# Clone and setup
git clone https://github.com/sebderhy/mcp-app-template.git my-app
cd my-app
./setup.sh        # Installs deps, builds widgets, runs tests

# Start the server
pnpm run server   # Starts on http://localhost:8000
```

<details>
<summary>Manual setup (alternative)</summary>

```bash
pnpm install
cd server && python3 -m venv .venv && .venv/bin/pip install -e ".[dev]" && cd ..
pnpm run setup:test   # Install Playwright
pnpm run build
pnpm run test
```

**Tip:** If you have [uv](https://docs.astral.sh/uv/) installed, you can use `uv pip install -e ".[dev]"` for faster package installation, or simply run `uv sync` in the server directory.
</details>

Open the app tester: **http://localhost:8000/assets/apptester.html**

That's it! The app tester uses [Puter.js](https://puter.com) for free AI - no API key required for manual testing.

## Creating Your Own App

The template includes 12 example widgets. To start fresh with only the widgets you need:

```bash
# Remove all example widgets (start from scratch)
./create_new_app.sh

# Keep specific widgets as starting points
./create_new_app.sh --keep carousel
./create_new_app.sh --keep carousel,todo

# Set your app name
./create_new_app.sh --keep boilerplate --name my-app
```

The script:
- Deletes widget directories from `src/` and `server/widgets/`
- Removes unused dependencies (three.js, framer-motion, chart.js, etc.)
- Updates the lockfile and runs build + tests to verify

After running, add your own widgets following the [Adding Your Own Widget](#adding-your-own-widget) section.

## Local App Tester

The app tester lets you test widgets without deploying to a real MCP host. It works in two modes:

### Zero-Config Mode (No API Key)

Just start the server and open the app tester - it works immediately:

```bash
pnpm run build
pnpm run server
# Open http://localhost:8000/assets/apptester.html
```

The app tester automatically detects when no API key is configured and uses [Puter.js](https://puter.com) - a free, browser-based AI service. This is perfect for:
- Quick prototyping sessions
- Demos and presentations
- Manual testing without credentials

Note: Puter.js is only used in the local app tester. In production, your app connects to real MCP hosts (Claude, ChatGPT, etc.) which provide the AI.

### Full Mode (With OpenAI API Key)

For production-quality testing with your preferred model:

1. Add your OpenAI API key to `.env`:
   ```bash
   OPENAI_API_KEY=sk-...
   ```

2. Optionally configure the model in `server/simulator_config.json`:
   ```json
   {
     "model": "gpt-4o-mini",
     "mcp_server_url": "http://localhost:8000/mcp"
   }
   ```

3. Restart the server and open the app tester

The app tester shows which mode is active in the header.

### App Tester Features

| Feature | Description |
|---------|-------------|
| **Zero-config mode** | Works instantly without any API key |
| **Inline widgets** | Widgets appear in chat just like real MCP hosts |
| **Expand to fullscreen** | Click the expand icon to view widgets fullscreen |
| **Theme toggle** | Test light/dark mode |
| **MCP protocol** | Uses the same MCP Apps protocol as real hosts |

Try prompts like *"Show me a carousel of restaurants"* or *"Display a dashboard"*

## Test with Real MCP Hosts

### Claude (Desktop or Web)

1. Expose your local server via a tunnel:
   ```bash
   npx cloudflared tunnel --url http://localhost:8000  # or: ngrok http 8000 --host-header=rewrite
   ```
2. Add the tunnel URL as a custom connector in Claude settings
3. Ask: *"Show me the boilerplate widget"*

### ChatGPT

1. Enable [Developer Mode](https://platform.openai.com/docs/guides/developer-mode)
2. Expose your local server via a tunnel:
   ```bash
   npx cloudflared tunnel --url http://localhost:8000  # or: ngrok http 8000 --host-header=rewrite
   ```
3. Add connector in ChatGPT Settings → Connectors (tunnel URL + `/mcp`)
4. Ask: *"Show me the boilerplate widget"*

> **Note:** The server disables DNS rebinding protection by default to support tunneling with random hostnames. For production deployments with a fixed domain, re-enable it in `server/main.py` (`TransportSecuritySettings`).

### MCP Apps Basic Host

For testing with the reference implementation:

```bash
git clone https://github.com/modelcontextprotocol/ext-apps
cd ext-apps/examples/basic-host
npm install && SERVERS='["http://localhost:8000"]' npm start
```

## How It Works

```
User Prompt → MCP Host → MCP Tool Call → Python Server → Widget renders in host
```

- **Widgets** (`src/`) - React/TypeScript UIs that render inside MCP hosts
- **Server** (`server/main.py`) - Python MCP server that handles tool calls
- **App Tester** (`internal/apptester/`) - Local development UI with Puter.js fallback
- **Assets** (`assets/`) - Built widget bundles (generated by `pnpm run build`)

## Included Examples

| Widget | Description |
|--------|-------------|
| `boilerplate` | Basic interactive card with state management |
| `carousel` | Horizontal scrolling cards |
| `list` | Vertical list with thumbnails |
| `gallery` | Image grid with lightbox |
| `dashboard` | Stats and metrics display |
| `solar-system` | 3D visualization (Three.js) |
| `todo` | Task manager with drag-and-drop |
| `shop` | E-commerce cart flow |
| `qr` | QR code generator with customization |
| `system-monitor` | Real-time CPU & memory monitoring (Chart.js) |
| `scenario-modeler` | SaaS financial projections with interactive sliders |
| `map` | Interactive 3D globe with geocoding (CesiumJS) |

Try them: *"Show me the carousel"*, *"Show me the dashboard"*, etc.

## Adding Your Own Widget

1. Create `src/my-widget/index.tsx` (entry point must target `my-widget-root`)
2. Add `"my-widget"` to the `targets` array in `build-all.mts`
3. Add a tool handler in `server/main.py` following the [MCP server guidelines](docs/mcp-development-guidelines.md)
4. Run `pnpm run build && pnpm run test`
5. Test in the app tester: `http://localhost:8000/assets/apptester.html`

When customizing this template for your own app, follow the guidelines in [`docs/mcp-development-guidelines.md`](docs/mcp-development-guidelines.md) for tool naming conventions, descriptions, and error handling best practices.

## Testing

```bash
pnpm run test          # Server + UI tests (fast, run after every change)
pnpm run test:all      # All tests including browser (requires Playwright)
pnpm run test:server   # Server tests only
pnpm run test:ui       # UI unit tests only
pnpm run test:browser  # Browser compliance tests only (requires Playwright)
```

**Tests are orthogonal to your app.** They verify:
- MCP Apps protocol compliance
- SDK format requirements
- Build output structure
- React hooks work correctly
- Widgets render without errors in real browsers

They don't verify your specific widgets, data, or business logic. Modify anything - tests still pass.

### Browser Compliance Tests

Browser tests run each widget in a real Chromium browser to verify:
- No JavaScript errors when rendering
- Widget renders visible content
- Works in both light and dark themes
- No unhandled promise rejections
- Images have alt text (accessibility)
- No duplicate HTML IDs
- All callTool invocations from widgets are callable on the server
- Text contrast meets WCAG guidelines (warnings only)
- Interactive elements are keyboard accessible (warnings only)

**Setup (one-time):**
```bash
pnpm run setup:test           # Install Playwright browsers
npx playwright install-deps   # Install system dependencies (may need sudo)
```

**Run:**
```bash
pnpm run test:browser
```

Tests skip gracefully if browser dependencies aren't installed, so they won't break CI pipelines that lack browser support.

### Automated Grading

The test suite includes automated grading against best practices. After running tests, check these reports:

**MCP Best Practices** (`server/tests/mcp_best_practices_report.txt`):
Grades against [MCP server guidelines](docs/mcp-development-guidelines.md) - tool naming, descriptions, error handling.

**MCP App Guidelines** (`server/tests/mcp_app_guidelines_report.txt`):
Grades against app design guidance - Know/Do/Show value, model-friendly outputs, ecosystem fit.

**Output Quality** (`server/tests/output_quality_report.txt`):
Grades tool output quality - response size limits, schema stability, null handling, ID consistency, boundary value handling.

Example report:
```
============================================================
MCP APP GUIDELINES GRADE REPORT
============================================================

1. Value Proposition: 100.0%
  ✓ Clear Know/Do/Show value: 100%

2. Model-Friendly Outputs: 94.3%
  ✓ List items have IDs: 100%
  ✗ Complex outputs have summary: 88%
      FIX: Add 'summary' field: {"summary": "3 items", "items": [...]}

OVERALL SCORE: 95.5% (Grade: A)
============================================================
```

When a check fails, the report includes a `FIX:` hint explaining exactly how to resolve it - useful for AI agents improving the server.

## Automated UI Testing (for AI Agents)

AI coding agents can visually test widgets using the built-in UI test tool. This enables AI agents to verify their changes work correctly by examining screenshots.

### Setup (One-time)

```bash
pnpm run setup:test   # Install Playwright browsers (~150MB)
```

### Two Testing Modes

**1. Direct Mode (no API key)** - Test specific tools directly:
```bash
pnpm run ui-test --tool show_carousel           # Test a tool
pnpm run ui-test --tool show_carousel --theme dark  # Test in dark mode
```
This is the recommended mode for AI coding agents.

**2. AI-in-the-loop Mode (requires OpenAI API key)** - Full app tester with AI:
```bash
pnpm run ui-test "Show me the carousel widget"
```
The AI receives your prompt, decides which widget to show, and the tool captures the result.

### Output

Both modes save artifacts to `/tmp/ui-test/`:
- `screenshot.png` - Visual capture of the rendered widget
- `dom.json` - Structured data about what rendered
- `console.log` - Browser console output

AI agents can read the screenshot to verify widgets rendered correctly:
```
Read tool → /tmp/ui-test/screenshot.png
```

### Example Workflow (Coding Agents)

```
User: "Add a new stats card to the dashboard"

Coding Agent (Claude Code, Codex, Cursor, etc.):
1. Modifies src/dashboard/index.tsx
2. Runs pnpm run build
3. Runs pnpm run ui-test --tool show_dashboard
4. Reads /tmp/ui-test/screenshot.png
5. Verifies the new card appears correctly
```

## Key APIs

```tsx
// Read data from server
const { title, items } = useWidgetProps({ title: "", items: [] });

// Persist state across tool calls
const [state, setState] = useWidgetState({ count: 0 });

// Respond to theme/display changes
const theme = useTheme();           // "light" | "dark"
const mode = useDisplayMode();      // "inline" | "fullscreen" | "pip"

// Call tools from widget
await window.openai.callTool("my_tool", { arg: "value" });
```

## Deployment

### Local Development

No configuration needed - just run:
```bash
pnpm run build
pnpm run server
```

### VPS / Remote Server

When running on a VPS or remote server, set the `BASE_URL` environment variable so widgets load correctly:

```bash
# Build once (no BASE_URL needed - uses placeholder)
pnpm run build

# Set BASE_URL when starting the server
BASE_URL=http://YOUR_SERVER_IP:8000/assets pnpm run server

# Or use a .env file at the repo root
cp .env.example .env
# Edit .env and set BASE_URL=http://YOUR_SERVER_IP:8000/assets
```

The server replaces the `__BASE_URL__` placeholder at runtime, so you can rebuild once and deploy anywhere by just changing the environment variable.

### Production

For production with a domain and HTTPS:

```bash
BASE_URL=https://your-domain.com/assets pnpm run server
```

Deploy the Python server to any platform (Fly.io, Render, Railway, Cloud Run, etc.). Requirements: HTTPS, `/mcp` endpoint, SSE streaming support.

## Resources

- [MCP Apps Protocol](https://modelcontextprotocol.io/docs/extensions/apps) - Official MCP Apps specification (see also local copies: `docs/mcp-apps-docs.md`, `docs/mcp-apps-specs.mdx`)
- [MCP Protocol](https://modelcontextprotocol.io/) - Model Context Protocol
- [OpenAI Apps SDK](https://developers.openai.com/apps-sdk) - OpenAI's implementation
- [Apps SDK UI Components](https://openai.github.io/apps-sdk-ui/)
- [Puter.js](https://developer.puter.com/) - Powers the app tester's zero-config mode (free for dev/testing)

## Acknowledgments

Based on [OpenAI's Apps SDK Examples](https://github.com/openai/openai-apps-sdk-examples) and the [MCP Apps Protocol](https://modelcontextprotocol.io/docs/extensions/apps).

The `qr`, `system-monitor`, `scenario-modeler`, and `map` widgets are ported from [modelcontextprotocol/ext-apps](https://github.com/modelcontextprotocol/ext-apps) (MIT License).

## License

MIT
