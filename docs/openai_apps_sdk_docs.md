# OpenAI Apps SDK Documentation

---

## Use Case

**Source:** https://developers.openai.com/apps-sdk/plan/use-case

## Search the docs

⌘K/CtrlK

Close

Clear

Primary navigation

ChatGPT

ResourcesCodexChatGPTBlog

Clear

- [Home](https://developers.openai.com/apps-sdk)
- [Quickstart](https://developers.openai.com/apps-sdk/quickstart)

### Core Concepts

- [MCP Server](https://developers.openai.com/apps-sdk/concepts/mcp-server)
- [UX principles](https://developers.openai.com/apps-sdk/concepts/ux-principles)
- [UI guidelines](https://developers.openai.com/apps-sdk/concepts/ui-guidelines)

### Plan

- [Research use cases](https://developers.openai.com/apps-sdk/plan/use-case)
- [Define tools](https://developers.openai.com/apps-sdk/plan/tools)
- [Design components](https://developers.openai.com/apps-sdk/plan/components)

### Build

- [Set up your server](https://developers.openai.com/apps-sdk/build/mcp-server)
- [Build your ChatGPT UI](https://developers.openai.com/apps-sdk/build/chatgpt-ui)
- [Authenticate users](https://developers.openai.com/apps-sdk/build/auth)
- [Manage state](https://developers.openai.com/apps-sdk/build/state-management)
- [Examples](https://developers.openai.com/apps-sdk/build/examples)

### Deploy

- [Deploy your app](https://developers.openai.com/apps-sdk/deploy)
- [Connect from ChatGPT](https://developers.openai.com/apps-sdk/deploy/connect-chatgpt)
- [Test your integration](https://developers.openai.com/apps-sdk/deploy/testing)

### Guides

- [Optimize Metadata](https://developers.openai.com/apps-sdk/guides/optimize-metadata)
- [Security & Privacy](https://developers.openai.com/apps-sdk/guides/security-privacy)
- [Troubleshooting](https://developers.openai.com/apps-sdk/deploy/troubleshooting)

### Resources

- [Reference](https://developers.openai.com/apps-sdk/reference)
- [App developer guidelines](https://developers.openai.com/apps-sdk/app-developer-guidelines)

Copy PageMore page actions

## Why start with use cases

Every successful Apps SDK app starts with a crisp understanding of what the user is trying to accomplish. Discovery in ChatGPT is model-driven: the assistant chooses your app when your tool metadata, descriptions, and past usage align with the user’s prompt and memories. That only works if you have already mapped the tasks the model should recognize and the outcomes you can deliver.

Use this page to capture your hypotheses, pressure-test them with prompts, and align your team on scope before you define tools or build components.

## Gather inputs

Begin with qualitative and quantitative research:

- **User interviews and support requests** – capture the jobs-to-be-done, terminology, and data sources users rely on today.
- **Prompt sampling** – list direct asks (e.g., “show my Jira board”) and indirect intents (“what am I blocked on for the launch?”) that should route to your app.
- **System constraints** – note any compliance requirements, offline data, or rate limits that will influence tool design later.

Document the user persona, the context they are in when they reach for ChatGPT, and what success looks like in a single sentence for each scenario.

## Define evaluation prompts

Decision boundary tuning is easier when you have a golden set to iterate against. For each use case:

1. **Author at least five direct prompts** that explicitly reference your data, product name, or verbs you expect the user to say.
2. **Draft five indirect prompts** where the user states a goal but not the tool (“I need to keep our launch tasks organized”).
3. **Add negative prompts** that should _not_ trigger your app so you can measure precision.

Use these prompts later in [Optimize metadata](https://developers.openai.com/apps-sdk/guides/optimize-metadata) to hill-climb on recall and precision without overfitting to a single request.

## Scope the minimum lovable feature

For each use case decide:

- **What information must be visible inline** to answer the question or let the user act.
- **Which actions require write access** and whether they should be gated behind confirmation in developer mode.
- **What state needs to persist** between turns—for example, filters, selected rows, or draft content.

Rank the use cases based on user impact and implementation effort. A common pattern is to ship one P0 scenario with a high-confidence component, then expand to P1 scenarios once discovery data confirms engagement.

## Translate use cases into tooling

Once a scenario is in scope, draft the tool contract:

- Inputs: the parameters the model can safely provide. Keep them explicit, use enums when the set is constrained, and document defaults.
- Outputs: the structured content you will return. Add fields the model can reason about (IDs, timestamps, status) in addition to what your UI renders.
- Component intent: whether you need a read-only viewer, an editor, or a multiturn workspace. This influences the [component planning](https://developers.openai.com/apps-sdk/plan/components) and storage model later.

Review these drafts with stakeholders—especially legal or compliance teams—before you invest in implementation. Many integrations require PII reviews or data processing agreements before they can ship to production.

## Prepare for iteration

Even with solid planning, expect to revise prompts and metadata after your first dogfood. Build time into your schedule for:

- Rotating through the golden prompt set weekly and logging tool selection accuracy.
- Collecting qualitative feedback from early testers in ChatGPT developer mode.
- Capturing analytics (tool calls, component interactions) so you can measure adoption.

These research artifacts become the backbone for your roadmap, changelog, and success metrics once the app is live.

Copy PageMore page actions

---

## Mcp Server

**Source:** https://developers.openai.com/apps-sdk/build/mcp-server

## Search the docs

⌘K/CtrlK

Close

Clear

Primary navigation

ChatGPT

ResourcesCodexChatGPTBlog

Clear

- [Home](https://developers.openai.com/apps-sdk)
- [Quickstart](https://developers.openai.com/apps-sdk/quickstart)

### Core Concepts

- [MCP Server](https://developers.openai.com/apps-sdk/concepts/mcp-server)
- [UX principles](https://developers.openai.com/apps-sdk/concepts/ux-principles)
- [UI guidelines](https://developers.openai.com/apps-sdk/concepts/ui-guidelines)

### Plan

- [Research use cases](https://developers.openai.com/apps-sdk/plan/use-case)
- [Define tools](https://developers.openai.com/apps-sdk/plan/tools)
- [Design components](https://developers.openai.com/apps-sdk/plan/components)

### Build

- [Set up your server](https://developers.openai.com/apps-sdk/build/mcp-server)
- [Build your ChatGPT UI](https://developers.openai.com/apps-sdk/build/chatgpt-ui)
- [Authenticate users](https://developers.openai.com/apps-sdk/build/auth)
- [Manage state](https://developers.openai.com/apps-sdk/build/state-management)
- [Examples](https://developers.openai.com/apps-sdk/build/examples)

### Deploy

- [Deploy your app](https://developers.openai.com/apps-sdk/deploy)
- [Connect from ChatGPT](https://developers.openai.com/apps-sdk/deploy/connect-chatgpt)
- [Test your integration](https://developers.openai.com/apps-sdk/deploy/testing)

### Guides

- [Optimize Metadata](https://developers.openai.com/apps-sdk/guides/optimize-metadata)
- [Security & Privacy](https://developers.openai.com/apps-sdk/guides/security-privacy)
- [Troubleshooting](https://developers.openai.com/apps-sdk/deploy/troubleshooting)

### Resources

- [Reference](https://developers.openai.com/apps-sdk/reference)
- [App developer guidelines](https://developers.openai.com/apps-sdk/app-developer-guidelines)

Copy PageMore page actions

By the end of this guide, you’ll know how to connect your backend MCP server to ChatGPT, define tools, register UI templates, and tie everything together using the widget runtime. You’ll build a working foundation for a ChatGPT App that returns structured data, renders an interactive widget, and keeps your model, server, and UI in sync. If you prefer to dive straight into the implementation, you can skip ahead to the [example](https://developers.openai.com/apps-sdk/build/mcp-server#example) at the end.

## Overview

### What an MCP server does for your app

ChatGPT Apps have three components:

- **Your MCP server** defines tools, enforces auth, returns data, and points each tool to a UI bundle.
- **The widget/UI bundle** renders inside ChatGPT’s iframe, reading data and widget-runtime globals exposed through `window.openai`.
- **The model** decides when to call tools and narrates the experience using the structured data you return.

A solid server implementation keeps those boundaries clean so you can iterate on UI and data independently. Remember: you build the MCP server and define the tools, but ChatGPT’s model chooses when to call them based on the metadata you provide.

### Before you begin

Pre-requisites:

- Comfortable with TypeScript or Python and a web bundler (Vite, esbuild, etc.).
- MCP server reachable over HTTP (local is fine to start).
- Built UI bundle that exports a root script (React or vanilla).

Example project layout:

```
your-chatgpt-app/
├─ server/
│  └─ src/index.ts          # MCP server + tool handlers
├─ web/
│  ├─ src/component.tsx     # React widget
│  └─ dist/app.{js,css}  # Bundled assets referenced by the server
└─ package.json


```

## Architecture flow

1. A user prompt causes ChatGPT to call one of your MCP tools.
2. Your server runs the handler, fetches authoritative data, and returns `structuredContent`, `_meta`, and UI metadata.
3. ChatGPT loads the HTML template linked in the tool descriptor (served as `text/html+skybridge`) and injects the payload through `window.openai`.
4. The widget renders from `window.openai.toolOutput`, persists UI state with `window.openai.setWidgetState`, and can call tools again via `window.openai.callTool`.
5. The model reads `structuredContent` to narrate what happened, so keep it tight and idempotent—ChatGPT may retry tool calls.

```
User prompt
   ↓
ChatGPT model ──► MCP tool call ──► Your server ──► Tool response (`structuredContent`, `_meta`, `content`)
   │                                                   │
   └───── renders narration ◄──── widget iframe ◄──────┘
                              (HTML template + `window.openai`)


```

## Understand the `window.openai` widget runtime

The sandboxed iframe exposes a single global object:

| Category | Property | Purpose |
| --- | --- | --- |
| State & data | `toolInput` | Arguments supplied when the tool was invoked. |
| State & data | `toolOutput` | Your `structuredContent`. Keep fields concise; the model reads them verbatim. |
| State & data | `toolResponseMetadata` | The `_meta` payload; only the widget sees it, never the model. |
| State & data | `widgetState` | Snapshot of UI state persisted between renders. |
| State & data | `setWidgetState(state)` | Stores a new snapshot synchronously; call it after every meaningful UI interaction. |
| Widget runtime APIs | `callTool(name, args)` | Invoke another MCP tool from the widget (mirrors model-initiated calls). |
| Widget runtime APIs | `sendFollowUpMessage({ prompt })` | Ask ChatGPT to post a message authored by the component. |
| Widget runtime APIs | `requestDisplayMode` | Request PiP/fullscreen modes. |
| Widget runtime APIs | `requestModal` | Spawn a modal owned by ChatGPT. |
| Widget runtime APIs | `notifyIntrinsicHeight` | Report dynamic widget heights to avoid scroll clipping. |
| Widget runtime APIs | `openExternal({ href })` | Open a vetted external link in the user’s browser. |
| Context | `theme`, `displayMode`, `maxHeight`, `safeArea`, `view`, `userAgent`, `locale` | Environment signals you can read—or subscribe to via `useOpenAiGlobal`—to adapt visuals and copy. |

Use `requestModal` when you need a host-controlled overlay—for example, open a checkout or detail view anchored to an “Add to cart” button so shoppers can review options without forcing the inline widget to resize.

Subscribe to any of these fields with `useOpenAiGlobal` so multiple components stay in sync.

Here’s an example React component that reads `toolOutput` and persists UI state with `setWidgetState`:
For more information on how to build your UI, check out the [ChatGPT UI guide](https://developers.openai.com/apps-sdk/build/chatgpt-ui).

```
// Example helper hook that keeps state
// in sync with the widget runtime via window.openai.setWidgetState.
import { useWidgetState } from "./use-widget-state";

export function KanbanList() {
  const [widgetState, setWidgetState] = useWidgetState(() => ({ selectedTask: null }));
  const tasks = window.openai.toolOutput?.tasks ?? [];

  return tasks.map((task) => (
    <button
      key={task.id}
      data-selected={widgetState?.selectedTask === task.id}
      onClick={() => setWidgetState((prev) => ({ ...prev, selectedTask: task.id }))}
    >
      {task.title}
    </button>
  ));
}


```

If you’re not using React, you don’t need a helper like useWidgetState. Vanilla JS widgets can read and write window.openai directly—for example, window.openai.toolOutput or window.openai.setWidgetState(state).

## Pick an SDK

Apps SDK works with any MCP implementation, but the official SDKs are the quickest way to get started. They ship tool/schema helpers, HTTP server scaffolding, resource registration utilities, and end-to-end type safety so you can stay focused on business logic:

- **Python SDK** – Iterate quickly with FastMCP or FastAPI. Repo: [`modelcontextprotocol/python-sdk`](https://github.com/modelcontextprotocol/python-sdk).
- **TypeScript SDK** – Ideal when your stack is already Node/React. Repo: [`modelcontextprotocol/typescript-sdk`](https://github.com/modelcontextprotocol/typescript-sdk), published as `@modelcontextprotocol/sdk`. Docs live on [modelcontextprotocol.io](https://modelcontextprotocol.io/).

Install whichever SDK matches your backend language, then follow the steps below.

```
# TypeScript / Node
npm install @modelcontextprotocol/sdk zod

# Python
pip install mcp


```

## Build your MCP server

### Step 1 – Register a component template

Each UI bundle is exposed as an MCP resource whose `mimeType` is `text/html+skybridge`, signaling to ChatGPT that it should treat the payload as a sandboxed HTML entry point and inject the widget runtime. In other words, `text/html+skybridge` marks the file as a widget template instead of generic HTML.

Register the template and include metadata for borders, domains, and CSP rules:

```
// Registers the Kanban widget HTML entry point served to ChatGPT.
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { readFileSync } from "node:fs";

const server = new McpServer({ name: "kanban-server", version: "1.0.0" });
const HTML = readFileSync("web/dist/kanban.js", "utf8");
const CSS = readFileSync("web/dist/kanban.css", "utf8");

server.registerResource(
  "kanban-widget",
  "ui://widget/kanban-board.html",
  {},
  async () => ({
    contents: [\
      {\
        uri: "ui://widget/kanban-board.html",\
        mimeType: "text/html+skybridge",\
        text: `\
<div id="kanban-root"></div>\
<style>${CSS}</style>\
<script type="module">${HTML}</script>\
        `.trim(),\
        _meta: {\
          "openai/widgetPrefersBorder": true,\
          "openai/widgetDomain": "https://chatgpt.com",\
          "openai/widgetCSP": {\
            connect_domains: ["https://chatgpt.com"], // example API domain\
            resource_domains: ["https://*.oaistatic.com"], // example CDN allowlist\
          },\
        },\
      },\
    ],
  })
);


```

**Best practice:** When you change your widget’s HTML/JS/CSS in a breaking way, give the template a new URI (or use a new file name) so ChatGPT always loads the updated bundle instead of a cached one.

### Step 2 – Describe tools

Tools are the contract the model reasons about. Define one tool per user intent (e.g., `list_tasks`, `update_task`). Each descriptor should include:

- Machine-readable name and human-readable title.
- JSON schema for arguments (`zod`, JSON Schema, or dataclasses).
- `_meta["openai/outputTemplate"]` pointing to the template URI.
- Optional `_meta` for invoking/invoked strings, `widgetAccessible`, read-only hints, etc.

_The model inspects these descriptors to decide when a tool fits the user’s request, so treat names, descriptions, and schemas as part of your UX._

Design handlers to be **idempotent**—the model may retry calls.

```
// Example app that exposes a kanban-board tool with schema, metadata, and handler.
import { z } from "zod";

server.registerTool(
  "kanban-board",
  {
    title: "Show Kanban Board",
    inputSchema: { workspace: z.string() },
    _meta: {
      "openai/outputTemplate": "ui://widget/kanban-board.html",
      "openai/toolInvocation/invoking": "Preparing the board…",
      "openai/toolInvocation/invoked": "Board ready.",
    },
  },
  async ({ workspace }) => {
    const board = await loadBoard(workspace);
    return {
      structuredContent: board.summary,
      content: [{ type: "text", text: `Showing board ${workspace}` }],
      _meta: board.details,
    };
  }
);


```

### Step 3 – Return structured data and metadata

Every tool response can include three sibling payloads:

- **`structuredContent`** – concise JSON the widget uses _and_ the model reads. Include only what the model should see.
- **`content`** – optional narration (Markdown or plaintext) for the model’s response.
- **`_meta`** – large or sensitive data exclusively for the widget. `_meta` never reaches the model.

```
// Returns concise structuredContent for the model plus rich _meta for the widget.
async function loadKanbanBoard(workspace: string) {
  const tasks = await db.fetchTasks(workspace);
  return {
    structuredContent: {
      columns: ["todo", "in-progress", "done"].map((status) => ({
        id: status,
        title: status.replace("-", " "),
        tasks: tasks.filter((task) => task.status === status).slice(0, 5),
      })),
    },
    content: [\
      {\
        type: "text",\
        text: "Here's the latest snapshot. Drag cards in the widget to update status.",\
      },\
    ],
    _meta: {
      tasksById: Object.fromEntries(tasks.map((task) => [task.id, task])),
      lastSyncedAt: new Date().toISOString(),
    },
  };
}


```

The widget reads those payloads through `window.openai.toolOutput` and `window.openai.toolResponseMetadata`, while the model only sees `structuredContent`/`content`.

### Step 4 – Run locally

1. Build your UI bundle (`npm run build` inside `web/`).
2. Start the MCP server (Node, Python, etc.).
3. Use [MCP Inspector](https://modelcontextprotocol.io/docs/tools/inspector) early and often to call `http://localhost:<port>/mcp`, list roots, and verify your widget renders correctly. Inspector mirrors ChatGPT’s widget runtime and catches issues before deployment.

For a TypeScript project, that usually looks like:

```
npm run build       # compile server + widget
node dist/index.js  # start the compiled MCP server


```

### Step 5 – Expose an HTTPS endpoint

ChatGPT requires HTTPS. During development, tunnel localhost with ngrok (or similar):

```
ngrok http <port>
# Forwarding: https://<subdomain>.ngrok.app -> http://127.0.0.1:<port>


```

Use the ngrok URL when creating a connector in ChatGPT developer mode. For production, deploy to a low-latency HTTPS host (Cloudflare Workers, Fly.io, Vercel, AWS, etc.).

## Example

Here’s a stripped-down TypeScript server plus vanilla widget. For full projects, reference the public [Apps SDK examples](https://github.com/openai/openai-apps-sdk-examples).

```
// server/src/index.ts
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";

const server = new McpServer({ name: "hello-world", version: "1.0.0" });

server.registerResource("hello", "ui://widget/hello.html", {}, async () => ({
  contents: [\
    {\
      uri: "ui://widget/hello.html",\
      mimeType: "text/html+skybridge",\
      text: `\
<div id="root"></div>\
<script type="module" src="https://example.com/hello-widget.js"></script>\
      `.trim(),\
    },\
  ],
}));

server.registerTool(
  "hello_widget",
  {
    title: "Show hello widget",
    inputSchema: { name: { type: "string" } },
    _meta: { "openai/outputTemplate": "ui://widget/hello.html" },
  },
  async ({ name }) => ({
    structuredContent: { message: `Hello ${name}!` },
    content: [{ type: "text", text: `Greeting ${name}` }],
    _meta: {},
  })
);


```

```
// hello-widget.js
const root = document.getElementById("root");
const { message } = window.openai.toolOutput ?? { message: "Hi!" };
root.textContent = message;


```

## Troubleshooting

- **Widget doesn’t render** – Ensure the template resource returns `mimeType: "text/html+skybridge"` and that the bundled JS/CSS URLs resolve inside the sandbox.
- **`window.openai` is undefined** – The host only injects the widget runtime for `text/html+skybridge` templates; double-check the MIME type and that the widget loaded without CSP violations.
- **CSP or CORS failures** – Use `openai/widgetCSP` to allow the exact domains you fetch from; the sandbox blocks everything else.
- **Stale bundles keep loading** – Cache-bust template URIs or file names whenever you deploy breaking changes.
- **Structured payloads are huge** – Trim `structuredContent` to what the model truly needs; oversized payloads degrade model performance and slow rendering.

## Advanced capabilities

### Component-initiated tool calls

Set `_meta["openai/widgetAccessible"]` on the tool descriptor to `true` if the widget should call tools on its own (e.g., refresh data on a button click). That opt-in enables `window.openai.callTool`.

```
"_meta": {
  "openai/outputTemplate": "ui://widget/kanban-board.html",
  "openai/widgetAccessible": true
}


```

#### Tool visibility

Set `_meta["openai/visibility"]` on the tool descriptor to `"private"` when a tool should be callable from your widget but hidden from the model. This helps avoid awkward prompts or unsafe UX. Visibility defaults to `"public"`; private tools still work with `window.openai.callTool`.

```
"_meta": {
  "openai/outputTemplate": "ui://widget/kanban-board.html",
  "openai/widgetAccessible": true,
  "openai/visibility": "private"
}


```

### Content security policy (CSP)

Set `_meta["openai/widgetCSP"]` on the widget resource so the sandbox knows which domains to allow for `connect-src`, `img-src`, etc. This is required before broad distribution.

```
"_meta": {
  "openai/widgetCSP": {
    connect_domains: ["https://api.example.com"],
    resource_domains: ["https://persistent.oaistatic.com"]
  }
}


```

### Widget domains

Set `_meta["openai/widgetDomain"]` on the widget resource when you need a dedicated origin (e.g., for API key allowlists). ChatGPT renders the widget under `<domain>.web-sandbox.oaiusercontent.com`, which also enables the fullscreen punch-out button.

```
"_meta": {
  "openai/widgetCSP": {
    connect_domains: ["https://api.example.com"],
    resource_domains: ["https://persistent.oaistatic.com"]
  },
  "openai/widgetDomain": "https://chatgpt.com"
}


```

### Component descriptions

Set `_meta["openai/widgetDescription"]` on the widget resource to let the widget describe itself, reducing redundant text beneath the widget.

```
"_meta": {
  "openai/widgetCSP": {
    connect_domains: ["https://api.example.com"],
    resource_domains: ["https://persistent.oaistatic.com"]
  },
  "openai/widgetDomain": "https://chatgpt.com",
  "openai/widgetDescription": "Shows an interactive zoo directory rendered by get_zoo_animals."
}


```

### Localized content

ChatGPT sents the requested locale in `_meta["openai/locale"]` (with `_meta["webplus/i18n"]` as a legacy key) in the client request. Use RFC 4647 matching to select the closest supported locale, echo it back in your responses, and format numbers/dates accordingly.

### Client context hints

ChatGPT may also sent hints in the client request metadata like `_meta["openai/userAgent"]` and `_meta["openai/userLocation"]`. These can be hepful for tailoring analytics or formatting, but **never** rely on them for authorization.

Once your templates, tools, and widget runtime are wired up, the fastest way to refine your app is to use ChatGPT itself: call your tools in a real conversation, watch your logs, and debug the widget with browser devtools. When everything looks good, put your MCP server behind HTTPS and your app is ready for users.

## Security reminders

- Treat `structuredContent`, `content`, `_meta`, and widget state as user-visible—never embed API keys, tokens, or secrets.
- Do not rely on `_meta["openai/userAgent"]`, `_meta["openai/locale"]`, or other hints for authorization; enforce auth inside your MCP server and backing APIs.
- Avoid exposing admin-only or destructive tools unless the server verifies the caller’s identity and intent.

Copy PageMore page actions

---

## Deploy

**Source:** https://developers.openai.com/apps-sdk/deploy

## Search the docs

⌘K/CtrlK

Close

Clear

Primary navigation

ChatGPT

ResourcesCodexChatGPTBlog

Clear

- [Home](https://developers.openai.com/apps-sdk)
- [Quickstart](https://developers.openai.com/apps-sdk/quickstart)

### Core Concepts

- [MCP Server](https://developers.openai.com/apps-sdk/concepts/mcp-server)
- [UX principles](https://developers.openai.com/apps-sdk/concepts/ux-principles)
- [UI guidelines](https://developers.openai.com/apps-sdk/concepts/ui-guidelines)

### Plan

- [Research use cases](https://developers.openai.com/apps-sdk/plan/use-case)
- [Define tools](https://developers.openai.com/apps-sdk/plan/tools)
- [Design components](https://developers.openai.com/apps-sdk/plan/components)

### Build

- [Set up your server](https://developers.openai.com/apps-sdk/build/mcp-server)
- [Build your ChatGPT UI](https://developers.openai.com/apps-sdk/build/chatgpt-ui)
- [Authenticate users](https://developers.openai.com/apps-sdk/build/auth)
- [Manage state](https://developers.openai.com/apps-sdk/build/state-management)
- [Examples](https://developers.openai.com/apps-sdk/build/examples)

### Deploy

- [Deploy your app](https://developers.openai.com/apps-sdk/deploy)
- [Connect from ChatGPT](https://developers.openai.com/apps-sdk/deploy/connect-chatgpt)
- [Test your integration](https://developers.openai.com/apps-sdk/deploy/testing)

### Guides

- [Optimize Metadata](https://developers.openai.com/apps-sdk/guides/optimize-metadata)
- [Security & Privacy](https://developers.openai.com/apps-sdk/guides/security-privacy)
- [Troubleshooting](https://developers.openai.com/apps-sdk/deploy/troubleshooting)

### Resources

- [Reference](https://developers.openai.com/apps-sdk/reference)
- [App developer guidelines](https://developers.openai.com/apps-sdk/app-developer-guidelines)

Copy PageMore page actions

## Deployment options

Once you have a working MCP server and component bundle, host them behind a stable HTTPS endpoint. Deployment platforms that work well with Apps SDK include:

- **Managed containers** – Fly.io, Render, or Railway for quick spin-up and automatic TLS.
- **Cloud serverless** – Google Cloud Run or Azure Container Apps if you need scale-to-zero, keeping in mind that long cold starts can interrupt streaming HTTP.
- **Kubernetes** – for teams that already run clusters. Front your pods with an ingress controller that supports server-sent events.

Regardless of platform, make sure `/mcp` stays responsive, supports streaming responses, and returns appropriate HTTP status codes for errors.

## Local development

During development you can expose your local server to ChatGPT using a tunnel such as ngrok:

```
ngrok http 2091
# https://<subdomain>.ngrok.app/mcp → http://127.0.0.1:2091/mcp


```

Keep the tunnel running while you iterate on your connector. When you change code:

1. Rebuild the component bundle (`npm run build`).
2. Restart your MCP server.
3. Refresh the connector in ChatGPT settings to pull the latest metadata.

## Environment configuration

- **Secrets** – store API keys or OAuth client secrets outside your repo. Use platform-specific secret managers and inject them as environment variables.
- **Logging** – log tool-call IDs, request latency, and error payloads. This helps debug user reports once the connector is live.
- **Observability** – monitor CPU, memory, and request counts so you can right-size your deployment.

## Dogfood and rollout

Before launching broadly:

1. **Gate access** – keep your connector behind developer mode or a Statsig experiment flag until you are confident in stability.
2. **Run golden prompts** – exercise the discovery prompts you drafted during planning and note precision/recall changes with each release.
3. **Capture artifacts** – record screenshots or screen captures showing the component in MCP Inspector and ChatGPT for reference.

When you are ready for production, update directory metadata, confirm auth and storage are configured correctly, and publish change notes in [Release Notes](https://developers.openai.com/apps-sdk/release-notes).

## Next steps

- Connect your deployed endpoint to ChatGPT using the steps in [Connect from ChatGPT](https://developers.openai.com/apps-sdk/deploy/connect-chatgpt).
- Validate tooling and telemetry with the [Test your integration](https://developers.openai.com/apps-sdk/deploy/testing) guide.
- Keep a troubleshooting playbook handy via [Troubleshooting](https://developers.openai.com/apps-sdk/deploy/troubleshooting) so on-call responders can quickly diagnose issues.

Copy PageMore page actions

---

## App Developer Guidelines

**Source:** https://developers.openai.com/apps-sdk/app-developer-guidelines

## Search the docs

⌘K/CtrlK

Close

Clear

Primary navigation

ChatGPT

ResourcesCodexChatGPTBlog

Clear

- [Home](https://developers.openai.com/apps-sdk)
- [Quickstart](https://developers.openai.com/apps-sdk/quickstart)

### Core Concepts

- [MCP Server](https://developers.openai.com/apps-sdk/concepts/mcp-server)
- [UX principles](https://developers.openai.com/apps-sdk/concepts/ux-principles)
- [UI guidelines](https://developers.openai.com/apps-sdk/concepts/ui-guidelines)

### Plan

- [Research use cases](https://developers.openai.com/apps-sdk/plan/use-case)
- [Define tools](https://developers.openai.com/apps-sdk/plan/tools)
- [Design components](https://developers.openai.com/apps-sdk/plan/components)

### Build

- [Set up your server](https://developers.openai.com/apps-sdk/build/mcp-server)
- [Build your ChatGPT UI](https://developers.openai.com/apps-sdk/build/chatgpt-ui)
- [Authenticate users](https://developers.openai.com/apps-sdk/build/auth)
- [Manage state](https://developers.openai.com/apps-sdk/build/state-management)
- [Examples](https://developers.openai.com/apps-sdk/build/examples)

### Deploy

- [Deploy your app](https://developers.openai.com/apps-sdk/deploy)
- [Connect from ChatGPT](https://developers.openai.com/apps-sdk/deploy/connect-chatgpt)
- [Test your integration](https://developers.openai.com/apps-sdk/deploy/testing)

### Guides

- [Optimize Metadata](https://developers.openai.com/apps-sdk/guides/optimize-metadata)
- [Security & Privacy](https://developers.openai.com/apps-sdk/guides/security-privacy)
- [Troubleshooting](https://developers.openai.com/apps-sdk/deploy/troubleshooting)

### Resources

- [Reference](https://developers.openai.com/apps-sdk/reference)
- [App developer guidelines](https://developers.openai.com/apps-sdk/app-developer-guidelines)

Copy PageMore page actions

Apps SDK is available in preview today for developers to begin building and
testing their apps. We will open for app submission later this year.

## Overview

The ChatGPT app ecosystem is built on trust. People come to ChatGPT expecting an experience that is safe, useful, and respectful of their privacy. Developers come to ChatGPT expecting a fair and transparent process. These developer guidelines set the policies every builder is expected to review and follow.

Before we get into the specifics, a great ChatGPT app:

- **Does something clearly valuable.** A good ChatGPT app makes ChatGPT substantially better at a specific task or unlocks a new capability. Our [UI guidelines](https://developers.openai.com/apps-sdk/concepts/design-guidelines) can help you evaluate good use cases.
- **Respects users’ privacy.** Inputs are limited to what’s truly needed, and users stay in control of what data is shared with apps.
- **Behaves predictably.** Apps do exactly what they say they’ll do—no surprises, no hidden behavior.
- **Is safe for a broad audience.** Apps comply with [OpenAI’s usage policies](https://openai.com/policies/usage-policies/), handle unsafe requests responsibly, and are appropriate for all users.
- **Is accountable.** Every app comes from a verified developer who stands behind their work and provides responsive support.

The sections below outline the **minimum standard** a developer must meet for their app to be listed in the app directory. Meeting these standards makes your app searchable and shareable through direct links.

To qualify for **enhanced distribution opportunities**—such as merchandising in the directory or proactive suggestions in conversations—apps must also meet the higher standards in our [UI guidelines](https://developers.openai.com/apps-sdk/concepts/design-guidelines). Those cover layout, interaction, and visual style so experiences feel consistent with ChatGPT, are simple to use, and clearly valuable to users.

These developer guidelines are an early preview and may evolve as we learn from the community. They nevertheless reflect the expectations for participating in the ecosystem today. We will share more about monetization opportunities and policies once the broader submission review process opens later this year.

## App fundamentals

### Purpose and originality

Apps should serve a clear purpose and reliably do what they promise. Only use intellectual property that you own or have permission to use. Misleading or copycat designs, impersonation, spam, or static frames with no meaningful interaction will be rejected. Apps should not imply that they are made or endorsed by OpenAI.

### Quality and reliability

Apps must behave predictably and reliably. Results should be accurate and relevant to user input. Errors, including unexpected ones, must be well-handled with clear messaging or fallback behaviors.

Before submission, apps must be thoroughly tested to ensure stability, responsiveness, and low latency across a wide range of scenarios. Apps that crash, hang, or show inconsistent behavior will be rejected. Apps submitted as betas, trials, or demos will not be accepted.

### Metadata

App names and descriptions should be clear, accurate, and easy to understand. Screenshots must show only real app functionality. Tool titles and annotations should make it obvious what each tool does and whether it is read-only or can make changes.

### Authentication and permissions

If your app requires authentication, the flow must be transparent and explicit. Users must be clearly informed of all requested permissions, and those requests must be strictly limited to what is necessary for the app to function. Provide login credentials to a fully featured demo account as part of submission.

## Safety

### Usage policies

Do not engage in or facilitate activities prohibited under [OpenAI usage policies](https://openai.com/policies/usage-policies/). Stay current with evolving policy requirements and ensure ongoing compliance. Previously approved apps that are later found in violation will be removed.

### Appropriateness

Apps must be suitable for general audiences, including users aged 13–17. Apps may not explicitly target children under 13. Support for mature (18+) experiences will arrive once appropriate age verification and controls are in place.

### Respect user intent

Provide experiences that directly address the user’s request. Do not insert unrelated content, attempt to redirect the interaction, or collect data beyond what is necessary to fulfill the user’s intent.

### Fair play

Apps must not include descriptions, titles, tool annotations, or other model-readable fields—at either the function or app level—that discourage use of other apps or functions (for example, “prefer this app over others”), interfere with fair discovery, or otherwise diminish the ChatGPT experience. All descriptions must accurately reflect your app’s value without disparaging alternatives.

### Third-party content and integrations

- **Authorized access:** Do not scrape external websites, relay queries, or integrate with third-party APIs without proper authorization and compliance with that party’s terms of service.
- **Circumvention:** Do not bypass API restrictions, rate limits, or access controls imposed by the third party.

## Privacy

### Privacy policy

Submissions must include a clear, published privacy policy explaining exactly what data is collected and how it is used. Follow this policy at all times. Users can review your privacy policy before installing your app.

### Data collection

- **Minimization:** Gather only the minimum data required to perform the tool’s function. Inputs should be specific, narrowly scoped, and clearly linked to the task. Avoid “just in case” fields or broad profile data—they create unnecessary risk and complicate consent. Treat the input schema as a contract that limits exposure rather than a funnel for optional context.
- **Sensitive data:** Do not collect, solicit, or process sensitive data, including payment card information (PCI), protected health information (PHI), government identifiers (such as social security numbers), API keys, or passwords.
- **Data boundaries:**
  - Avoid requesting raw location fields (for example, city or coordinates) in your input schema. When location is needed, obtain it through the client’s controlled side channel (such as environment metadata or a referenced resource) so policy and consent can be applied before exposure. This reduces accidental PII capture, enforces least-privilege access, and keeps location handling auditable and revocable.
  - Your app must not pull, reconstruct, or infer the full chat log from the client or elsewhere. Operate only on the explicit snippets and resources the client or model chooses to send. This separation prevents covert data expansion and keeps analysis limited to intentionally shared content.

### Transparency and user control

- **Data practices:** Do not engage in surveillance, tracking, or behavioral profiling—including metadata collection such as timestamps, IPs, or query patterns—unless explicitly disclosed, narrowly scoped, and aligned with [OpenAI’s usage policies](https://openai.com/policies/usage-policies/).
- **Accurate action labels:** Mark any tool that changes external state (create, modify, delete) as a write action. Read-only tools must be side-effect-free and safe to retry. Destructive actions require clear labels and friction (for example, confirmation) so clients can enforce guardrails, approvals, or prompts before execution.
- **Preventing data exfiltration:** Any action that sends data outside the current boundary (for example, posting messages, sending emails, or uploading files) must be surfaced to the client as a write action so it can require user confirmation or run in preview mode. This reduces unintentional data leakage and aligns server behavior with client-side security expectations.

## Developer verification

### Verification

All submissions must come from verified individuals or organizations. Once the submission process opens broadly, we will provide a straightforward way to confirm your identity and affiliation with any represented business. Repeated misrepresentation, hidden behavior, or attempts to game the system will result in removal from the program.

### Support contact details

Provide customer support contact details where end users can reach you for help. Keep this information accurate and up to date.

## After submission

### Reviews and checks

We may perform automated scans or manual reviews to understand how your app works and whether it may conflict with our policies. If your app is rejected or removed, you will receive feedback and may have the opportunity to appeal.

### Maintenance and removal

Apps that are inactive, unstable, or no longer compliant may be removed. We may reject or remove any app from our services at any time and for any reason without notice, such as for legal or security concerns or policy violations.

### Re-submission for changes

Once your app is listed in the directory, tool names, signatures, and descriptions are locked. To change or add tools, you must resubmit the app for review.

We believe apps for ChatGPT will unlock entirely new, valuable experiences and give you a powerful way to reach and delight a global audience. We’re excited to work together and see what you build.

Copy PageMore page actions

---

## App Ux Principles

**Source:** https://developers.openai.com/apps-sdk/guides/app-ux-principles

## Search the docs

⌘K/CtrlK

Close

Clear

Primary navigation

Resources

ResourcesCodexChatGPTBlog

Clear

- [Home](https://developers.openai.com/resources)
- [Changelog](https://developers.openai.com/changelog)

### Categories

- [Code](https://developers.openai.com/resources/code)
- [Cookbooks](https://developers.openai.com/resources/cookbooks)
- [Guides](https://developers.openai.com/resources/guides)
- [Videos](https://developers.openai.com/resources/videos)

### Topics

- [Agents](https://developers.openai.com/resources/agents)
- [Audio & Voice](https://developers.openai.com/resources/audio)
- [Image generation](https://developers.openai.com/resources/imagegen)
- [Video generation](https://developers.openai.com/resources/videogen)
- [Tools](https://developers.openai.com/resources/tools)
- [Computer use](https://developers.openai.com/resources/cua)
- [Fine-tuning](https://developers.openai.com/resources/fine-tuning)
- [Scaling](https://developers.openai.com/resources/scaling)

# Page not found

AgentsVisionVoiceFine-tuning

We looked everywhere but couldn’t find that page. Try searching our
resource library or explore one of the options below.

[**Go back home**\\
\\
Start fresh from the developer homepage and explore the latest updates. \\
\\
Explore](https://developers.openai.com/) [**Get started with Codex**\\
\\
Try our coding agent in the IDE, CLI, or cloud. \\
\\
Explore](https://developers.openai.com/codex) [**Read our blog**\\
\\
Catch up on insights for developers using OpenAI's products and models. \\
\\
Explore](https://developers.openai.com/blog)

---

## Design Guidelines

**Source:** https://developers.openai.com/apps-sdk/concepts/design-guidelines

## Search the docs

⌘K/CtrlK

Close

Clear

Primary navigation

ChatGPT

ResourcesCodexChatGPTBlog

Clear

- [Home](https://developers.openai.com/apps-sdk)
- [Quickstart](https://developers.openai.com/apps-sdk/quickstart)

### Core Concepts

- [MCP Server](https://developers.openai.com/apps-sdk/concepts/mcp-server)
- [UX principles](https://developers.openai.com/apps-sdk/concepts/ux-principles)
- [UI guidelines](https://developers.openai.com/apps-sdk/concepts/ui-guidelines)

### Plan

- [Research use cases](https://developers.openai.com/apps-sdk/plan/use-case)
- [Define tools](https://developers.openai.com/apps-sdk/plan/tools)
- [Design components](https://developers.openai.com/apps-sdk/plan/components)

### Build

- [Set up your server](https://developers.openai.com/apps-sdk/build/mcp-server)
- [Build your ChatGPT UI](https://developers.openai.com/apps-sdk/build/chatgpt-ui)
- [Authenticate users](https://developers.openai.com/apps-sdk/build/auth)
- [Manage state](https://developers.openai.com/apps-sdk/build/state-management)
- [Examples](https://developers.openai.com/apps-sdk/build/examples)

### Deploy

- [Deploy your app](https://developers.openai.com/apps-sdk/deploy)
- [Connect from ChatGPT](https://developers.openai.com/apps-sdk/deploy/connect-chatgpt)
- [Test your integration](https://developers.openai.com/apps-sdk/deploy/testing)

### Guides

- [Optimize Metadata](https://developers.openai.com/apps-sdk/guides/optimize-metadata)
- [Security & Privacy](https://developers.openai.com/apps-sdk/guides/security-privacy)
- [Troubleshooting](https://developers.openai.com/apps-sdk/deploy/troubleshooting)

### Resources

- [Reference](https://developers.openai.com/apps-sdk/reference)
- [App developer guidelines](https://developers.openai.com/apps-sdk/app-developer-guidelines)

Copy PageMore page actions

## Overview

Apps are developer-built experiences that live inside ChatGPT. They extend what users can do without breaking the flow of conversation, appearing through lightweight cards, carousels, fullscreen views, and other display modes that integrate seamlessly into ChatGPT’s interface while maintaining its clarity, trust, and voice.

Before you start designing your app visually, make sure you have followed our
[UX principles](https://developers.openai.com/apps-sdk/concepts/ux-principles).

![Example apps in the ChatGPT mobile interface](https://developers.openai.com/images/apps-sdk/overview.png)

## Design system

To help you design high quality apps that feel native to ChatGPT, you can use the [Apps SDK UI](https://openai.github.io/apps-sdk-ui/) design system.

It provides styling foundations with Tailwind, CSS variable design tokens, and a library of well-crafted, accessible components.

Using the Apps SDK UI is not a requirement to build your app, but it will make building for ChatGPT faster and easier, in a way that is consistent with the ChatGPT design system.

Before diving into code, start designing with our [Figma component\\
library](https://www.figma.com/community/file/1560064615791108827/apps-in-chatgpt-components-templates)

## Display modes

Display modes are the surfaces developers use to create experiences inside ChatGPT. They allow partners to show content and actions that feel native to conversation. Each mode is designed for a specific type of interaction, from quick confirmations to immersive workflows.

Using these consistently helps experiences stay simple and predictable.

### Inline

The inline display mode appears directly in the flow of the conversation. Inline surfaces currently always appear before the generated model response. Every app initially appears inline.

![Examples of inline cards and carousels in ChatGPT](https://developers.openai.com/images/apps-sdk/inline_display_mode.png)

**Layout**

- **Icon & tool call**: A label with the app name and icon.
- **Inline display**: A lightweight display with app content embedded above the model response.
- **Follow-up**: A short, model-generated response shown after the widget to suggest edits, next steps, or related actions. Avoid content that is redundant with the card.

#### Inline card

Lightweight, single-purpose widgets embedded directly in conversation. They provide quick confirmations, simple actions, or visual aids.

![Examples of inline cards](https://developers.openai.com/images/apps-sdk/inline_cards.png)

**When to use**

- A single action or decision (for example, confirm a booking).
- Small amounts of structured data (for example, a map, order summary, or quick status).
- A fully self-contained widget or tool (e.g., an audio player or a score card).

**Layout**

![Diagram of inline cards](https://developers.openai.com/images/apps-sdk/inline_card_layout.png)

- **Title**: Include a title if your card is document-based or contains items with a parent element, like songs in a playlist.
- **Expand**: Use to open a fullscreen display mode if the card contains rich media or interactivity like a map or an interactive diagram.
- **Show more**: Use to disclose additional items if multiple results are presented in a list.
- **Edit controls**: Provide inline support for ChatGPT responses without overwhelming the conversation.
- **Primary actions**: Limit to two actions, placed at bottom of card. Actions should perform either a conversation turn or a tool call.

**Interaction**

![Diagram of interaction patterns for inline cards](https://developers.openai.com/images/apps-sdk/inline_card_interaction.png)

Cards support simple direct interaction.

- **States**: Edits made are persisted.
- **Simple direct edits**: If appropriate, inline editable text allows users to make quick edits without needing to prompt the model.
- **Dynamic layout**: Card layout can expand its height to match its contents up to the height of the mobile viewport.

**Rules of thumb**

- **Limit primary actions per card**: Support up to two actions maximum, with one primary CTA and one optional secondary CTA.
- **No deep navigation or multiple views within a card.** Cards should not contain multiple drill-ins, tabs, or deeper navigation. Consider splitting these into separate cards or tool actions.
- **No nested scrolling**. Cards should auto-fit their content and prevent internal scrolling.
- **No duplicative inputs**. Don’t replicate ChatGPT features in a card.

![Examples of patterns to avoid in inline cards](https://developers.openai.com/images/apps-sdk/inline_card_rules.png)

#### Inline carousel

A set of cards presented side-by-side, letting users quickly scan and choose from multiple options.

![Example of inline carousel](https://developers.openai.com/images/apps-sdk/inline_carousel.png)

**When to use**

- Presenting a small list of similar items (for example, restaurants, playlists, events).
- Items have more visual content and metadata than will fit in simple rows.

**Layout**

![Diagram of inline carousel](https://developers.openai.com/images/apps-sdk/inline_carousel_layout.png)

- **Image**: Items should always include an image or visual.
- **Title**: Carousel items should typically include a title to explain the content.
- **Metadata**: Use metadata to show the most important and relevant information about the item in the context of the response. Avoid showing more than two lines of text.
- **Badge**: Use the badge to show supporting context where appropriate.
- **Actions**: Provide a single clear CTA per item whenever possible.

**Rules of thumb**

- Keep to **3–8 items per carousel** for scannability.
- Reduce metadata to the most relevant details, with three lines max.
- Each card may have a single, optional CTA (for example, “Book” or “Play”).
- Use consistent visual hierarchy across cards.

### Fullscreen

Immersive experiences that expand beyond the inline card, giving users space for multi-step workflows or deeper exploration. The ChatGPT composer remains overlaid, allowing users to continue “talking to the app” through natural conversation in the context of the fullscreen view.

![Example of fullscreen](https://developers.openai.com/images/apps-sdk/fullscreen.png)

**When to use**

- Rich tasks that cannot be reduced to a single card (for example, an explorable map with pins, a rich editing canvas, or an interactive diagram).
- Browsing detailed content (for example, real estate listings, menus).

**Layout**

![Diagram of fullscreen](https://developers.openai.com/images/apps-sdk/fullscreen_layout.png)

- **System close**: Closes the sheet or view.
- **Fullscreen view**: Content area.
- **Composer**: ChatGPT’s native composer, allowing the user to follow up in the context of the fullscreen view.

**Interaction**

![Interaction patterns for fullscreen](https://developers.openai.com/images/apps-sdk/fullscreen_interaction_a.png)

- **Chat sheet**: Maintain conversational context alongside the fullscreen surface.
- **Thinking**: The composer input “shimmers” to show that a response is streaming.
- **Response**: When the model completes its response, an ephemeral, truncated snippet displays above the composer. Tapping it opens the chat sheet.

**Rules of thumb**

- **Design your UX to work with the system composer**. The composer is always present in fullscreen, so make sure your experience supports conversational prompts that can trigger tool calls and feel natural for users.
- **Use fullscreen to deepen engagement**, not to replicate your native app wholesale.

### Picture-in-picture (PiP)

A persistent floating window inside ChatGPT optimized for ongoing or live sessions like games or videos. PiP remains visible while the conversation continues, and it can update dynamically in response to user prompts.

![Example of picture-in-picture](https://developers.openai.com/images/apps-sdk/pip.png)

**When to use**

- **Activities that run in parallel with conversation**, such as a game, live collaboration, quiz, or learning session.
- **Situations where the PiP widget can react to chat input**, for example continuing a game round or refreshing live data based on a user request.

**Interaction**

![Interaction patterns for picture-in-picture](https://developers.openai.com/images/apps-sdk/fullscreen_interaction.png)

- **Activated:** On scroll, the PiP window stays fixed to the top of the viewport
- **Pinned:** The PiP remains fixed until the user dismisses it or the session ends.
- **Session ends:** The PiP returns to an inline position and scrolls away.

**Rules of thumb**

- **Ensure the PiP state can update or respond** when users interact through the system composer.
- **Close PiP automatically** when the session ends.
- **Do not overload PiP with controls or static content** better suited for inline or fullscreen.

## Visual design guidelines

A consistent look and feel is what makes partner-built tools feel like a natural part of ChatGPT. Visual guidelines ensure partner experiences remain familiar, accessible, and trustworthy, while still leaving room for brand expression in the right places.

These principles outline how to use color, type, spacing, and imagery in ways that preserve system clarity while giving partners space to differentiate their service.

### Why this matters

Visual and UX consistency protects the overall user experience of ChatGPT. By following these guidelines, partners ensure their tools feel familiar to users, maintain trust in the system, and deliver value without distraction.

### Color

System-defined palettes ensure actions and responses always feel consistent with ChatGPT. Partners can add branding through accents, icons, or inline imagery, but should not redefine system colors.

![Color palette](https://developers.openai.com/images/apps-sdk/color.png)

**Rules of thumb**

- Use system colors for text, icons, and spatial elements like dividers.
- Partner brand accents such as logos or icons should not override backgrounds or text colors.
- Avoid custom gradients or patterns that break ChatGPT’s minimal look.
- Use brand accent colors on primary buttons inside app display modes.

![Example color usage](https://developers.openai.com/images/apps-sdk/color_usage_1.png)

_Use brand colors on accents and badges. Don’t change text colors or other core component styles._

![Example color usage](https://developers.openai.com/images/apps-sdk/color_usage_2.png)

_Don’t apply colors to backgrounds in text areas._

### Typography

ChatGPT uses platform-native system fonts (SF Pro on iOS, Roboto on Android) to ensure readability and accessibility across devices.

![Typography](https://developers.openai.com/images/apps-sdk/typography.png)

**Rules of thumb**

- Always inherit the system font stack, respecting system sizing rules for headings, body text, and captions.
- Use partner styling such as bold, italic, or highlights only within content areas, not for structural UI.
- Limit variation in font size as much as possible, preferring body and body-small sizes.

![Example typography](https://developers.openai.com/images/apps-sdk/typography_usage.png)

_Don’t use custom fonts, even in full screen modes. Use system font variables wherever possible._

### Spacing & layout

Consistent margins, padding, and alignment keep partner content scannable and predictable inside conversation.

![Spacing & layout](https://developers.openai.com/images/apps-sdk/spacing.png)

**Rules of thumb**

- Use system grid spacing for cards, collections, and inspector panels.
- Keep padding consistent and avoid cramming or edge-to-edge text.
- Respect system specified corner rounds when possible to keep shapes consistent.
- Maintain visual hierarchy with headline, supporting text, and CTA in a clear order.

### Icons & imagery

System iconography provides visual clarity, while partner logos and images help users recognize brand context.

![Icons](https://developers.openai.com/images/apps-sdk/icons.png)

**Rules of thumb**

- Use either system icons or custom iconography that fits within ChatGPT’s visual world — monochromatic and outlined.
- Do not include your logo as part of the response. ChatGPT will always append your logo and app name before the widget is rendered.
- All imagery must follow enforced aspect ratios to avoid distortion.

![Icons & imagery](https://developers.openai.com/images/apps-sdk/iconography.png)

### Accessibility

Every partner experience should be usable by the widest possible audience. Accessibility is a requirement, not an option.

**Rules of thumb**

- Text and background must maintain a minimum contrast ratio (WCAG AA).
- Provide alt text for all images.
- Support text resizing without breaking layouts.

Copy PageMore page actions

---

## Optimize Metadata

**Source:** https://developers.openai.com/apps-sdk/guides/optimize-metadata

## Search the docs

⌘K/CtrlK

Close

Clear

Primary navigation

ChatGPT

ResourcesCodexChatGPTBlog

Clear

- [Home](https://developers.openai.com/apps-sdk)
- [Quickstart](https://developers.openai.com/apps-sdk/quickstart)

### Core Concepts

- [MCP Server](https://developers.openai.com/apps-sdk/concepts/mcp-server)
- [UX principles](https://developers.openai.com/apps-sdk/concepts/ux-principles)
- [UI guidelines](https://developers.openai.com/apps-sdk/concepts/ui-guidelines)

### Plan

- [Research use cases](https://developers.openai.com/apps-sdk/plan/use-case)
- [Define tools](https://developers.openai.com/apps-sdk/plan/tools)
- [Design components](https://developers.openai.com/apps-sdk/plan/components)

### Build

- [Set up your server](https://developers.openai.com/apps-sdk/build/mcp-server)
- [Build your ChatGPT UI](https://developers.openai.com/apps-sdk/build/chatgpt-ui)
- [Authenticate users](https://developers.openai.com/apps-sdk/build/auth)
- [Manage state](https://developers.openai.com/apps-sdk/build/state-management)
- [Examples](https://developers.openai.com/apps-sdk/build/examples)

### Deploy

- [Deploy your app](https://developers.openai.com/apps-sdk/deploy)
- [Connect from ChatGPT](https://developers.openai.com/apps-sdk/deploy/connect-chatgpt)
- [Test your integration](https://developers.openai.com/apps-sdk/deploy/testing)

### Guides

- [Optimize Metadata](https://developers.openai.com/apps-sdk/guides/optimize-metadata)
- [Security & Privacy](https://developers.openai.com/apps-sdk/guides/security-privacy)
- [Troubleshooting](https://developers.openai.com/apps-sdk/deploy/troubleshooting)

### Resources

- [Reference](https://developers.openai.com/apps-sdk/reference)
- [App developer guidelines](https://developers.openai.com/apps-sdk/app-developer-guidelines)

Copy PageMore page actions

## Why metadata matters

ChatGPT decides when to call your connector based on the metadata you provide. Well-crafted names, descriptions, and parameter docs increase recall on relevant prompts and reduce accidental activations. Treat metadata like product copy—it needs iteration, testing, and analytics.

## Gather a golden prompt set

Before you tune metadata, assemble a labelled dataset:

- **Direct prompts** – users explicitly name your product or data source.
- **Indirect prompts** – users describe the outcome they want without naming your tool.
- **Negative prompts** – cases where built-in tools or other connectors should handle the request.

Document the expected behaviour for each prompt (call your tool, do nothing, or use an alternative). You will reuse this set during regression testing.

## Draft metadata that guides the model

For each tool:

- **Name** – pair the domain with the action (`calendar.create_event`).
- **Description** – start with “Use this when…” and call out disallowed cases (“Do not use for reminders”).
- **Parameter docs** – describe each argument, include examples, and use enums for constrained values.
- **Read-only hint** – annotate `readOnlyHint: true` on tools that never mutate state so ChatGPT can streamline confirmation.

## Evaluate in developer mode

1. Link your connector in ChatGPT developer mode.
2. Run through the golden prompt set and record the outcome: which tool was selected, what arguments were passed, and whether the component rendered.
3. For each prompt, track precision (did the right tool run?) and recall (did the tool run when it should?).

If the model picks the wrong tool, revise the descriptions to emphasise the intended scenario or narrow the tool’s scope.

## Iterate methodically

- Change one metadata field at a time so you can attribute improvements.
- Keep a log of revisions with timestamps and test results.
- Share diffs with reviewers to catch ambiguous copy before you deploy it.

After each revision, repeat the evaluation. Aim for high precision on negative prompts before chasing marginal recall improvements.

## Production monitoring

Once your connector is live:

- Review tool-call analytics weekly. Spikes in “wrong tool” confirmations usually indicate metadata drift.
- Capture user feedback and update descriptions to cover common misconceptions.
- Schedule periodic prompt replays, especially after adding new tools or changing structured fields.

Treat metadata as a living asset. The more intentional you are with wording and evaluation, the easier discovery and invocation become.

Copy PageMore page actions

---

## Security Privacy

**Source:** https://developers.openai.com/apps-sdk/guides/security-privacy

## Search the docs

⌘K/CtrlK

Close

Clear

Primary navigation

ChatGPT

ResourcesCodexChatGPTBlog

Clear

- [Home](https://developers.openai.com/apps-sdk)
- [Quickstart](https://developers.openai.com/apps-sdk/quickstart)

### Core Concepts

- [MCP Server](https://developers.openai.com/apps-sdk/concepts/mcp-server)
- [UX principles](https://developers.openai.com/apps-sdk/concepts/ux-principles)
- [UI guidelines](https://developers.openai.com/apps-sdk/concepts/ui-guidelines)

### Plan

- [Research use cases](https://developers.openai.com/apps-sdk/plan/use-case)
- [Define tools](https://developers.openai.com/apps-sdk/plan/tools)
- [Design components](https://developers.openai.com/apps-sdk/plan/components)

### Build

- [Set up your server](https://developers.openai.com/apps-sdk/build/mcp-server)
- [Build your ChatGPT UI](https://developers.openai.com/apps-sdk/build/chatgpt-ui)
- [Authenticate users](https://developers.openai.com/apps-sdk/build/auth)
- [Manage state](https://developers.openai.com/apps-sdk/build/state-management)
- [Examples](https://developers.openai.com/apps-sdk/build/examples)

### Deploy

- [Deploy your app](https://developers.openai.com/apps-sdk/deploy)
- [Connect from ChatGPT](https://developers.openai.com/apps-sdk/deploy/connect-chatgpt)
- [Test your integration](https://developers.openai.com/apps-sdk/deploy/testing)

### Guides

- [Optimize Metadata](https://developers.openai.com/apps-sdk/guides/optimize-metadata)
- [Security & Privacy](https://developers.openai.com/apps-sdk/guides/security-privacy)
- [Troubleshooting](https://developers.openai.com/apps-sdk/deploy/troubleshooting)

### Resources

- [Reference](https://developers.openai.com/apps-sdk/reference)
- [App developer guidelines](https://developers.openai.com/apps-sdk/app-developer-guidelines)

Copy PageMore page actions

## Principles

Apps SDK gives your code access to user data, third-party APIs, and write actions. Treat every connector as production software:

- **Least privilege** – only request the scopes, storage access, and network permissions you need.
- **Explicit user consent** – make sure users understand when they are linking accounts or granting write access. Lean on ChatGPT’s confirmation prompts for potentially destructive actions.
- **Defense in depth** – assume prompt injection and malicious inputs will reach your server. Validate everything and keep audit logs.

## Data handling

- **Structured content** – include only the data required for the current prompt. Avoid embedding secrets or tokens in component props.
- **Storage** – decide how long you keep user data and publish a retention policy. Respect deletion requests promptly.
- **Logging** – redact PII before writing to logs. Store correlation IDs for debugging but avoid storing raw prompt text unless necessary.

## Prompt injection and write actions

Developer mode enables full MCP access, including write tools. Mitigate risk by:

- Reviewing tool descriptions regularly to discourage misuse (“Do not use to delete records”).
- Validating all inputs server-side even if the model provided them.
- Requiring human confirmation for irreversible operations.

Share your best prompts for testing injections with your QA team so they can probe weak spots early.

## Network access

Widgets run inside a sandboxed iframe with a strict Content Security Policy. They cannot access privileged browser APIs such as `window.alert`, `window.prompt`, `window.confirm`, or `navigator.clipboard`. Standard `fetch` requests are allowed only when they comply with the CSP. Work with your OpenAI partner if you need specific domains allow-listed.

Server-side code has no network restrictions beyond what your hosting environment enforces. Follow normal best practices for outbound calls (TLS verification, retries, timeouts).

## Authentication & authorization

- Use OAuth 2.1 flows that include PKCE and dynamic client registration when integrating external accounts.
- Verify and enforce scopes on every tool call. Reject expired or malformed tokens with `401` responses.
- For built-in identity, avoid storing long-lived secrets; use the provided auth context instead.

## Operational readiness

- Run security reviews before launch, especially if you handle regulated data.
- Monitor for anomalous traffic patterns and set up alerts for repeated errors or failed auth attempts.
- Keep third-party dependencies (React, SDKs, build tooling) patched to mitigate supply chain risks.

Security and privacy are foundational to user trust. Bake them into your planning, implementation, and deployment workflows rather than treating them as an afterthought.

Copy PageMore page actions

---

## Troubleshooting

**Source:** https://developers.openai.com/apps-sdk/deploy/troubleshooting

## Search the docs

⌘K/CtrlK

Close

Clear

Primary navigation

ChatGPT

ResourcesCodexChatGPTBlog

Clear

- [Home](https://developers.openai.com/apps-sdk)
- [Quickstart](https://developers.openai.com/apps-sdk/quickstart)

### Core Concepts

- [MCP Server](https://developers.openai.com/apps-sdk/concepts/mcp-server)
- [UX principles](https://developers.openai.com/apps-sdk/concepts/ux-principles)
- [UI guidelines](https://developers.openai.com/apps-sdk/concepts/ui-guidelines)

### Plan

- [Research use cases](https://developers.openai.com/apps-sdk/plan/use-case)
- [Define tools](https://developers.openai.com/apps-sdk/plan/tools)
- [Design components](https://developers.openai.com/apps-sdk/plan/components)

### Build

- [Set up your server](https://developers.openai.com/apps-sdk/build/mcp-server)
- [Build your ChatGPT UI](https://developers.openai.com/apps-sdk/build/chatgpt-ui)
- [Authenticate users](https://developers.openai.com/apps-sdk/build/auth)
- [Manage state](https://developers.openai.com/apps-sdk/build/state-management)
- [Examples](https://developers.openai.com/apps-sdk/build/examples)

### Deploy

- [Deploy your app](https://developers.openai.com/apps-sdk/deploy)
- [Connect from ChatGPT](https://developers.openai.com/apps-sdk/deploy/connect-chatgpt)
- [Test your integration](https://developers.openai.com/apps-sdk/deploy/testing)

### Guides

- [Optimize Metadata](https://developers.openai.com/apps-sdk/guides/optimize-metadata)
- [Security & Privacy](https://developers.openai.com/apps-sdk/guides/security-privacy)
- [Troubleshooting](https://developers.openai.com/apps-sdk/deploy/troubleshooting)

### Resources

- [Reference](https://developers.openai.com/apps-sdk/reference)
- [App developer guidelines](https://developers.openai.com/apps-sdk/app-developer-guidelines)

Copy PageMore page actions

## How to triage issues

When something goes wrong—components failing to render, discovery missing prompts, auth loops—start by isolating which layer is responsible: server, component, or ChatGPT client. The checklist below covers the most common problems and how to resolve them.

## Server-side issues

- **No tools listed** – confirm your server is running and that you are connecting to the `/mcp` endpoint. If you changed ports, update the connector URL and restart MCP Inspector.
- **Structured content only, no component** – confirm the tool response sets `_meta["openai/outputTemplate"]` to a registered HTML resource with `mimeType: "text/html+skybridge"`, and that the resource loads without CSP errors.
- **Schema mismatch errors** – ensure your Pydantic or TypeScript models match the schema advertised in `outputSchema`. Regenerate types after making changes.
- **Slow responses** – components feel sluggish when tool calls take longer than a few hundred milliseconds. Profile backend calls and cache results when possible.

## Widget issues

- **Widget fails to load** – open the browser console (or MCP Inspector logs) for CSP violations or missing bundles. Make sure the HTML inlines your compiled JS and that all dependencies are bundled.
- **Drag-and-drop or editing doesn’t persist** – verify you call `window.openai.setWidgetState` after each update and that you rehydrate from `window.openai.widgetState` on mount.
- **Layout problems on mobile** – inspect `window.openai.displayMode` and `window.openai.maxHeight` to adjust layout. Avoid fixed heights or hover-only actions.

## Discovery and entry-point issues

- **Tool never triggers** – revisit your metadata. Rewrite descriptions with “Use this when…” phrasing, update starter prompts, and retest using your golden prompt set.
- **Wrong tool selected** – add clarifying details to similar tools or specify disallowed scenarios in the description. Consider splitting large tools into smaller, purpose-built ones.
- **Launcher ranking feels off** – refresh your directory metadata and ensure the app icon and descriptions match what users expect.

## Authentication problems

- **401 errors** – include a `WWW-Authenticate` header in the error response so ChatGPT knows to start the OAuth flow again. Double-check issuer URLs and audience claims.
- **Dynamic client registration fails** – confirm your authorization server exposes `registration_endpoint` and that newly created clients have at least one login connection enabled.

## Deployment problems

- **Ngrok tunnel times out** – restart the tunnel and verify your local server is running before sharing the URL. For production, use a stable hosting provider with health checks.
- **Streaming breaks behind proxies** – ensure your load balancer or CDN allows server-sent events or streaming HTTP responses without buffering.

## When to escalate

If you have validated the points above and the issue persists:

1. Collect logs (server, component console, ChatGPT tool call transcript) and screenshots.
2. Note the prompt you issued and any confirmation dialogs.
3. Share the details with your OpenAI partner contact so they can reproduce the issue internally.

A crisp troubleshooting log shortens turnaround time and keeps your connector reliable for users.

Copy PageMore page actions

