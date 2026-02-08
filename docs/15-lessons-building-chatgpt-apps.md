# 15 Lessons Building ChatGPT Apps

> Source: [15 lessons learned building ChatGPT Apps](https://developers.openai.com/blog/15-lessons-building-chatgpt-apps/) — OpenAI Developers Blog (by [Alpic](https://alpic.ai))

---

## 1. The Three Body Problem: Context Asymmetry

In traditional web apps, you have two actors: **user** and **UI**. In ChatGPT Apps, a third enters: the **model**. Each has partial knowledge — this is **context asymmetry**.

If a user clicks "Select" in your widget, the UI updates but the model remains unaware unless you explicitly surface that context. When the user then asks "tell me more about this," the model has no idea what "this" refers to.

### Not all context should be shared

Different parts of a ChatGPT App need intentionally different views of the same state:

- **Performance**: Widgets need images, pricing variants, preloaded options — sending all of this to the model wastes tokens and adds latency.
- **Logic**: Some asymmetry is by design (e.g., a game where the model knows the answer but the UI must not).

Use different tool output fields to control visibility:

| Field | Visible to | Purpose |
|-------|-----------|---------|
| `structuredContent` | Widget + Model | Semantic data both need |
| `_meta` | Widget only | Display config, layout hints |

### Front-load data, don't lazy-load

In web apps, lazy-loading reduces initial payload. In ChatGPT Apps, **tool calls take seconds** due to model reasoning. Front-load aggressively — send as much data as possible in the initial tool response.

### The model needs visibility into user selections

When a user interacts with a widget (selects a product, navigates a tab), sync that state to the model via `window.openai.setWidgetState(state)`. Without this, the model can't answer follow-up questions about what the user is looking at.

### Different interactions require different APIs

| Path | When to use |
|------|-------------|
| `structuredContent` → widget | Initial data hydration |
| `setWidgetState` → model | User selection/navigation state |
| `callTool` from widget | Widget-initiated server actions |
| Classic XHR from widget | Public API calls that don't need model awareness |

---

## 2. UI Design for AI

### Display modes and their constraints

| Mode | Behavior | When to use |
|------|----------|-------------|
| **Inline** | Card in conversation history | Quick interactions |
| **Fullscreen** | Full screen with chat bar | Complex UIs (maps, editors) |
| **Picture-in-Picture** | Floats on top of conversation | Widget stays relevant during follow-ups |

Account for device-specific safe zones (e.g., persistent close button on mobile) to avoid clipped content.

### UI consistency in an embedded environment

Widgets live inside an existing interface — visual inconsistencies stand out. Use the [OpenAI Apps SDK UI Kit](https://github.com/openai/apps-sdk-ui) (Tailwind-based) for components, icons, and design tokens that align with ChatGPT's design system.

### Language-first filtering (no sidebar filters)

In agentic UI, traditional filter sidebars are a regression. Users can express intent in natural language ("Sunny destinations in Europe for under $200") — forcing them through checkboxes adds friction.

Instead, provide the model with a **List of Values (LOV)** for tool parameters so it can map natural language directly to API requirements.

### Files unlock richer interactions

Files aren't secondary inputs — they can start entire flows. A user can upload a photo and have the model identify it, then continue into discovery in the widget.

- **Model side**: Tools consume uploaded files via `openai/fileParams`
- **Widget side**: `window.openai.uploadFile` and `window.openai.getFileDownloadUrl`

---

## 3. Production Considerations

### CSP: Content Security Policies

ChatGPT Apps run in double-nested iframes with strict CSP. Declare allowed domains carefully in the app manifest:

| Field | Purpose | Example |
|-------|---------|---------|
| `connectDomains` | API & XHR requests | `https://api.weather.com` |
| `resourceDomains` | Images, fonts, scripts | `https://cdn.jsdelivr.net` |
| `frameDomains` | Embedded iframes | `https://www.youtube.com` |
| `redirectDomains` | External links without warnings | `https://app.example.com` |

Treat CSP configuration as a first-class concern early — "works locally but breaks in production" is the most common issue.

### Widget flags with outsized impact

| Flag | Controls |
|------|----------|
| `widgetDomain` | Required for submission; defines "Open in App" URL and origin whitelisting |
| Tool annotations (`readOnly`, `destructiveHint`, `openWorldHint`) | Required for publishing; validated during submission |
| Private tools | Tools not callable by the model must be explicitly marked private |
| `widgetAccessible` | Whether the widget can call tools on its own via `callTool` |

---

## Quick Reference

```
┌──────────────────────────────────────────────────────────────┐
│              CHATGPT APP DEVELOPMENT LESSONS                  │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  CONTEXT ASYMMETRY:                                          │
│    • structuredContent → widget + model                      │
│    • _meta → widget only                                     │
│    • setWidgetState → syncs UI state to model                │
│    • Decide explicitly who needs to know what                │
│                                                              │
│  DATA STRATEGY:                                              │
│    • Front-load aggressively (tool calls are slow)           │
│    • Use XHR only for public APIs model doesn't need         │
│                                                              │
│  UI DESIGN:                                                  │
│    • Support inline, fullscreen, and PiP modes               │
│    • Use Apps SDK UI Kit for visual consistency               │
│    • Prefer language-first filtering over UI controls         │
│                                                              │
│  PRODUCTION:                                                 │
│    • Declare all external domains in CSP config              │
│    • Set tool annotations for publishing                     │
│    • Mark private tools explicitly                           │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```
