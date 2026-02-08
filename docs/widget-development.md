# Widget Development Patterns

This document covers the project-specific patterns and hooks for building widgets in this MCP App Template.

---

## Basic Widget Structure

Every widget follows this pattern:

```tsx
// src/my-widget/index.tsx
import { createRoot } from "react-dom/client";
import { useWidgetProps } from "../use-widget-props";
import { useTheme } from "../use-theme";

interface MyWidgetProps {
  title: string;
  items: Item[];
}

function MyWidget() {
  const props = useWidgetProps<MyWidgetProps>();
  const theme = useTheme(); // "light" | "dark"

  if (!props) return <div className="p-4">Loading...</div>;

  return (
    <div className={`p-4 ${theme === "dark" ? "bg-gray-900 text-white" : "bg-white text-gray-900"}`}>
      <h1 className="text-xl font-bold">{props.title}</h1>
      {/* Widget content */}
    </div>
  );
}

createRoot(document.getElementById("my-widget-root")!).render(<MyWidget />);
```

---

## Core Hooks

### `useWidgetProps<T>()`

Retrieves the structured content passed from the MCP server via the host's `window.openai.toolOutput`.

```tsx
// Widget receives data via the host interface
const props = useWidgetProps<MyDataType>();

// Props structure matches structuredContent from server
// server/main.py returns:
structuredContent = {
    "title": "My Title",
    "items": [...]
}
// Widget receives: { title: "My Title", items: [...] }
```

**Important:** Always handle the `null` case while props are loading:

```tsx
if (!props) return <div className="p-4">Loading...</div>;
```

### `useTheme()`

Returns the current theme: `"light"` or `"dark"`. Widgets MUST support both themes.

```tsx
const theme = useTheme();
```

### `useWidgetState<T>()`

Persists widget state on the host and **syncs it to the model**. This is critical for interactive widgets where users select, navigate, or filter content.

```tsx
const [state, setState] = useWidgetState({ selectedId: null, viewMode: "grid" });

// When user selects an item:
const handleSelect = (item) => {
  setState({ selectedId: item.id, selectedName: item.name, viewMode: state.viewMode });
};
```

**Why this matters:** If a user clicks "Item 3" in your widget then asks "tell me more about this", the model needs to know what "this" refers to. `useWidgetState` syncs your UI selection to the model's context.

**When to use:**
- User can select from multiple items (lists, carousels, galleries)
- User can navigate between views (tabs, pages, detail views)
- Any state that affects what the user is "looking at"

### `useDisplayMode()`

Returns the current display mode: `"inline"`, `"fullscreen"`, or `"pip"` (picture-in-picture).

```tsx
const displayMode = useDisplayMode();

// Adapt layout to display mode
if (displayMode === "fullscreen") {
  return <ExpandedView {...props} />;
}
return <CompactView {...props} />;
```

**Display mode guidelines:**

| Mode | Size | When to Use |
|------|------|-------------|
| `inline` | Card in chat | Quick info, simple displays |
| `fullscreen` | Full viewport | Complex UIs, maps, editors |
| `pip` | Floating overlay | Persists during conversation follow-ups |

---

## Theme Support (REQUIRED)

All widgets MUST support both light and dark themes. Two approaches:

### Option 1: Tailwind dark mode classes

```tsx
<div className="bg-white dark:bg-gray-900 text-gray-900 dark:text-white">
```

### Option 2: Conditional styling with `useTheme()`

```tsx
const theme = useTheme();

<div className={theme === "dark" ? "bg-gray-900 text-white" : "bg-white text-gray-900"}>
```

### Theme-aware color palette

| Element | Light Mode | Dark Mode |
|---------|------------|-----------|
| Background | `bg-white` | `bg-gray-900` |
| Text | `text-gray-900` | `text-white` |
| Secondary text | `text-gray-600` | `text-gray-400` |
| Borders | `border-gray-200` | `border-gray-700` |
| Cards | `bg-gray-50` | `bg-gray-800` |

---

## Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│  MCP Server (server/main.py)                                    │
│                                                                 │
│  structuredContent = { "title": "...", "items": [...] }        │
│                          │                                      │
└──────────────────────────┼──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  MCP Apps Host (Claude, ChatGPT, VS Code, Goose)                │
│                                                                 │
│  window.openai.toolOutput = structuredContent                   │
│                          │                                      │
└──────────────────────────┼──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  Widget (src/my-widget/index.tsx)                               │
│                                                                 │
│  const props = useWidgetProps<MyWidgetProps>();                 │
│  // props = { title: "...", items: [...] }                      │
└─────────────────────────────────────────────────────────────────┘
```

---

## Common Patterns

### Handling empty states

```tsx
function MyWidget() {
  const props = useWidgetProps<MyWidgetProps>();

  if (!props) return <div className="p-4">Loading...</div>;
  if (props.items.length === 0) return <div className="p-4">No items found</div>;

  return (/* render items */);
}
```

### Responsive layouts

```tsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  {props.items.map(item => (
    <Card key={item.id} item={item} />
  ))}
</div>
```

### Calling tools from widgets

```tsx
async function handleClick(itemId: string) {
  const result = await window.openai.callTool("get_item_details", { id: itemId });
  console.log("Result:", result);
}
```

---

## Project Structure

```
src/
├── my-widget/
│   └── index.tsx        # Widget entry point
├── use-widget-props.ts  # Shared hook for reading tool output
├── use-theme.ts         # Shared hook for theme detection
├── use-host-global.ts   # Low-level hook for host globals
└── index.css            # Shared Tailwind styles
```

Each widget:
1. Lives in its own directory under `src/`
2. Has a single `index.tsx` entry point
3. Imports shared hooks from parent directory
4. Gets built to `assets/{widget-name}.html` by `build-all.mts`

---

## The Three Body Problem: Context Management

In traditional web apps, you have two actors: **user** and **UI**. In MCP Apps, there's a third: the **model**. Each has partial knowledge:

- **Model** sees: `structuredContent`, widget state (via `setWidgetState`)
- **Widget** sees: `structuredContent`, `_meta`, local React state
- **User** sees: The rendered widget

This creates **context asymmetry**. Good apps explicitly decide what each actor needs to know.

### What goes where?

| Data Type | Where to Put It | Why |
|-----------|-----------------|-----|
| Semantic data (items, titles, statuses) | `structuredContent` | Model can reason about it, widget can display it |
| Display config (layout hints, animation flags) | `_meta` | Widget needs it, model doesn't |
| User selection state | `useWidgetState` | Model needs to know what user is looking at |
| Transient UI state (hover, scroll position) | React `useState` | Neither model nor persistence needed |

### Example: Carousel with selection

```python
# Server: server/widgets/carousel.py
return types.ServerResult(types.CallToolResult(
    content=[types.TextContent(type="text", text="5 restaurants found")],
    structuredContent={
        "title": "Restaurants Near You",
        "items": [{"id": "1", "name": "..."}, ...]  # Model sees this
    },
    _meta={
        **get_invocation_meta(widget),
        "autoScroll": True,  # Widget-only config
    },
))
```

```tsx
// Widget: src/carousel/App.tsx
const props = useWidgetProps<CarouselProps>();
const [state, setState] = useWidgetState({ selectedId: null });

const handleSelect = (item) => {
  // Now when user asks "book this one", model knows which item
  setState({ selectedId: item.id, selectedName: item.name });
};
```

### Front-load data, don't lazy-load

In web apps, lazy-loading reduces initial payload. In MCP Apps, **tool calls take seconds** due to model reasoning. Front-load aggressively:

```python
# Good: Return real data immediately
structuredContent = {
    "items": SAMPLE_ITEMS[:10],  # Real data, not placeholders
    "totalCount": len(ALL_ITEMS),
}

# Bad: Return empty, expect widget to fetch
structuredContent = {
    "items": [],  # Widget will need another tool call
    "loadMoreUrl": "/api/items",
}
```

---

## Content Security Policy (CSP)

MCP Apps run in sandboxed iframes with strict CSP. If your widget loads external resources, declare them in `server/widgets/_base.py`:

### Resource types and where to declare them

| Resource Type | CSP Directive | Declare In |
|--------------|---------------|------------|
| Images, fonts, scripts | `resourceDomains` | `EXTERNAL_RESOURCE_DOMAINS` |
| API calls (fetch/XHR) | `connectDomains` | `EXTERNAL_CONNECT_DOMAINS` |
| Embedded iframes | `frameDomains` | Not yet supported in template |

### Example: Adding a new CDN

```python
# server/widgets/_base.py

EXTERNAL_RESOURCE_DOMAINS: List[str] = [
    "https://cdn.openai.com",           # Fonts from @openai/apps-sdk-ui
    "https://images.unsplash.com",      # Sample images
    "https://my-cdn.example.com",       # ADD YOUR CDN HERE
]

EXTERNAL_CONNECT_DOMAINS: List[str] = [
    "https://api.myservice.com",        # ADD YOUR API HERE
]
```

### Common CSP issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| Images don't load | CDN not in `resourceDomains` | Add CDN to `EXTERNAL_RESOURCE_DOMAINS` |
| API calls fail | Domain not in `connectDomains` | Add API domain to `EXTERNAL_CONNECT_DOMAINS` |
| Fonts missing | Font CDN not whitelisted | Add font CDN to `EXTERNAL_RESOURCE_DOMAINS` |
| Works locally, fails in production | CSP only enforced by real hosts | Test with real MCP host (Claude, ChatGPT) |

---

## Further Reading

- [15-lessons-building-chatgpt-apps.md](./15-lessons-building-chatgpt-apps.md) - Deep dive on context asymmetry, front-loading, and agentic UX patterns
- [what-makes-a-great-chatgpt-app.md](./what-makes-a-great-chatgpt-app.md) - Know/Do/Show framework from OpenAI
