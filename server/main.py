"""
MCP App Template - Python MCP Server

This server provides multiple widget templates that work with any MCP Apps host
(Claude, ChatGPT, VS Code, Goose, etc.):

- Boilerplate: Basic interactive widget
- Carousel: Horizontal scrolling cards
- List: Vertical list with thumbnails
- Gallery: Image grid with lightbox
- Dashboard: Stats and metrics display
- Solar System: Interactive 3D solar system
- Todo: Multi-list todo manager
- Shop: E-commerce cart with checkout
- QR Code: Stateless QR code generator (from ext-apps)
- Scenario Modeler: Interactive SaaS financial projections (from ext-apps)
- System Monitor: Real-time CPU/memory polling (from ext-apps)
- Map: Interactive 3D globe with geocoding (from ext-apps)

Run with: uvicorn main:app --host 0.0.0.0 --port 8000 --reload
"""

from __future__ import annotations

import os
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse, parse_qs

import mcp.types as types
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from pydantic import BaseModel, ConfigDict

# Load .env file at startup (for BASE_URL and other config)
_env_path = Path(__file__).parent / ".env"
if not _env_path.exists():
    _env_path = Path(__file__).parent.parent / ".env"
if _env_path.exists():
    load_dotenv(_env_path)

# =============================================================================
# WIDGET REGISTRY (auto-discovered from widgets/ package)
# =============================================================================

from widgets import (
    WIDGETS, WIDGETS_BY_ID, WIDGETS_BY_URI,
    WIDGET_HANDLERS, WIDGET_INPUT_MODELS,
    DATA_ONLY_HANDLERS,
)
from widgets._base import (
    Widget, ASSETS_DIR, MIME_TYPE,
    load_widget_html, get_base_url, get_csp_domains,
    get_tool_meta, get_invocation_meta, get_tool_schema,
    format_validation_error,
    EXTERNAL_RESOURCE_DOMAINS, EXTERNAL_CONNECT_DOMAINS,
)

# Re-export sample data for backward compatibility with tests
from widgets.carousel import SAMPLE_CAROUSEL_ITEMS
from widgets.list import SAMPLE_LIST_ITEMS
from widgets.gallery import SAMPLE_GALLERY_IMAGES
from widgets.dashboard import SAMPLE_DASHBOARD_STATS, SAMPLE_ACTIVITIES
from widgets.todo import SAMPLE_TODO_LISTS
from widgets.shop import SAMPLE_CART_ITEMS
from widgets.map import SAMPLE_MAP_PLACES
from widgets.scenario_modeler import SCENARIO_TEMPLATES, SCENARIO_DEFAULT_INPUTS

# Re-export input models for backward compatibility with tests
from widgets.boilerplate import CardInput
from widgets.carousel import CarouselInput
from widgets.list import ListInput
from widgets.gallery import GalleryInput
from widgets.dashboard import DashboardInput
from widgets.solar_system import SolarSystemInput
from widgets.todo import TodoInput
from widgets.shop import ShopInput
from widgets.qr import QrInput
from widgets.scenario_modeler import ScenarioModelerInput
from widgets.system_monitor import SystemInfoInput
from widgets.map import ShowMapInput, GeocodeInput


# =============================================================================
# MCP SERVER SETUP
# =============================================================================

SERVER_INSTRUCTIONS = """
## MCP App Widget Server Usage Guide

This MCP server provides interactive widget tools for MCP Apps hosts. Each tool displays
a specific type of visual content in the chat interface.

### Tool Selection Guide

Choose the right tool based on user intent:

- **show_carousel**: Best for showcasing multiple items horizontally (restaurants,
  products, places). Use when the user asks for recommendations or wants to browse options.

- **show_list**: Best for ranked/ordered content (top 10 lists, search results,
  task lists). Use when order matters or items need detailed metadata.

- **show_gallery**: Best for image-focused content (photo albums, portfolios).
  Use when visuals are the primary content.

- **show_dashboard**: Best for metrics and analytics (KPIs, account overviews,
  stats). Use when showing numerical data or status information.

- **show_card**: Basic interactive widget. Use for simple single-item displays
  or when other widgets don't fit.

- **show_solar_system**: Educational 3D visualization. Use for astronomy topics
  or interactive learning experiences.

- **show_todo**: Task management interface. Use when the user wants to organize
  tasks, create lists, or track progress.

- **show_shop**: E-commerce cart interface. Use for shopping, checkout flows,
  or product quantity management.

- **show_qr**: Generate QR codes from text or URLs. Use for sharing links
  or encoding information as scannable images.

- **get_scenario_data**: SaaS financial projections. Use for modeling business
  scenarios with interactive sliders and chart comparison.

- **get_system_info**: Real-time system monitoring. Use for displaying CPU and
  memory usage with live polling charts.

- **show_map**: Interactive 3D globe. Use for geographic exploration. Pair with
  the **geocode** tool to find coordinates from place names.

- **geocode**: Search for places using OpenStreetMap (data-only, no widget).
  Returns coordinates and bounding boxes to use with show_map.

### Important Notes

- All widgets support both light and dark themes automatically
- Widgets are responsive and work on mobile and desktop
- Each tool returns sample data by default - in production, connect to real data sources
- Use the `title` parameter to customize the widget header
"""

mcp = FastMCP(
    name="boilerplate-server",
    instructions=SERVER_INSTRUCTIONS,
    stateless_http=True,
    # Disable DNS rebinding protection when tunneling (e.g. cloudflared).
    # The tunnel hostname is random and changes each session, so we can't
    # allowlist it statically.  Re-enable for production with a fixed domain.
    transport_security=TransportSecuritySettings(
        enable_dns_rebinding_protection=False,
    ),
)


# =============================================================================
# TOOL REGISTRATION
# =============================================================================

@mcp._mcp_server.list_tools()
async def list_tools() -> List[types.Tool]:
    tools = []

    for widget in WIDGETS:
        input_model = WIDGET_INPUT_MODELS.get(widget.identifier)
        schema = get_tool_schema(input_model)

        tools.append(types.Tool(
            name=widget.identifier,
            title=widget.title,
            description=widget.description,
            inputSchema=schema,
            _meta=get_tool_meta(widget),
            annotations={
                "destructiveHint": False,
                "openWorldHint": False,
                "readOnlyHint": True,
            },
        ))

    # Data-only tools: called by widgets via callTool, not intended for LLM use.
    # They must be registered so MCP hosts can route callTool invocations.
    tools.append(types.Tool(
        name="poll_system_stats",
        title="Poll System Stats",
        description="Returns live CPU and memory stats. Called by the system monitor widget for polling — not intended for direct LLM use.",
        inputSchema={"type": "object", "properties": {}, "additionalProperties": False},
        annotations={
            "destructiveHint": False,
            "openWorldHint": False,
            "readOnlyHint": True,
        },
    ))

    return tools


# =============================================================================
# RESOURCE REGISTRATION
# =============================================================================

@mcp._mcp_server.list_resources()
async def list_resources() -> List[types.Resource]:
    return [
        types.Resource(
            name=widget.title,
            title=widget.title,
            uri=widget.template_uri,
            description=f"{widget.title} widget markup",
            mimeType=MIME_TYPE,
            _meta=get_tool_meta(widget),
        )
        for widget in WIDGETS
    ]


@mcp._mcp_server.list_resource_templates()
async def list_resource_templates() -> List[types.ResourceTemplate]:
    return [
        types.ResourceTemplate(
            name=widget.title,
            title=widget.title,
            uriTemplate=widget.template_uri,
            description=f"{widget.title} widget markup",
            mimeType=MIME_TYPE,
            _meta=get_tool_meta(widget),
        )
        for widget in WIDGETS
    ]


# =============================================================================
# REQUEST HANDLERS
# =============================================================================

async def handle_read_resource(req: types.ReadResourceRequest) -> types.ServerResult:
    widget = WIDGETS_BY_URI.get(str(req.params.uri))
    if widget is None:
        return types.ServerResult(types.ReadResourceResult(contents=[], _meta={"error": f"Unknown resource: {req.params.uri}"}))

    return types.ServerResult(types.ReadResourceResult(contents=[
        types.TextResourceContents(uri=widget.template_uri, mimeType=MIME_TYPE, text=load_widget_html(widget.component_name), _meta=get_tool_meta(widget))
    ]))


async def handle_call_tool(req: types.CallToolRequest) -> types.ServerResult:
    tool_name = req.params.name
    arguments = req.params.arguments or {}

    # Handle data-only tools (no widget UI)
    data_handler = DATA_ONLY_HANDLERS.get(tool_name)
    if data_handler:
        return await data_handler(arguments)

    # Handle widget tools
    widget = WIDGETS_BY_ID.get(tool_name)
    if not widget:
        return types.ServerResult(types.CallToolResult(
            content=[types.TextContent(type="text", text=f"Unknown tool: {tool_name}")],
            isError=True,
        ))

    handler = WIDGET_HANDLERS.get(tool_name)
    if not handler:
        return types.ServerResult(types.CallToolResult(
            content=[types.TextContent(type="text", text=f"No handler for: {tool_name}")],
            isError=True,
        ))

    return await handler(widget, arguments)


# Register handlers
mcp._mcp_server.request_handlers[types.CallToolRequest] = handle_call_tool
mcp._mcp_server.request_handlers[types.ReadResourceRequest] = handle_read_resource


# =============================================================================
# HTTP APP SETUP
# =============================================================================

_inner_app = mcp.streamable_http_app()


async def app(scope, receive, send):
    """ASGI wrapper that starts the sandbox server on first request.

    We can't start the sandbox server at module import time because that would
    cause side effects when tests import this module. Instead, we start it
    lazily on the first ASGI lifespan/request event.
    """
    if scope["type"] == "lifespan":
        # Start sandbox server during ASGI lifespan startup
        async def _wrapped_receive():
            message = await receive()
            if message["type"] == "lifespan.startup":
                start_sandbox_server(8001)
            return message
        await _inner_app(scope, _wrapped_receive, send)
    else:
        await _inner_app(scope, receive, send)


# Expose the inner app's attributes so middleware/routes can be added
app.add_middleware = _inner_app.add_middleware  # type: ignore[attr-defined]
app.mount = _inner_app.mount  # type: ignore[attr-defined]
app.routes = _inner_app.routes  # type: ignore[attr-defined]

try:
    from starlette.middleware.cors import CORSMiddleware
    app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"], allow_credentials=False)
except Exception:
    pass

# Serve static assets (widget JS/CSS bundles)
try:
    from starlette.staticfiles import StaticFiles
    if ASSETS_DIR.exists():
        app.mount("/assets", StaticFiles(directory=ASSETS_DIR), name="assets")
except Exception:
    pass

# =============================================================================
# SIMULATOR CHAT API
# =============================================================================

from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
import json as json_module


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str
    conversation_id: Optional[str] = "default"
    model_config = ConfigDict(extra="forbid")


class WidgetData(BaseModel):
    """Widget data returned from chat."""
    tool_name: str
    html: str
    tool_output: Dict[str, Any]
    model_config = ConfigDict(extra="forbid")


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    message: str
    widget: Optional[WidgetData] = None
    conversation_id: str
    model_config = ConfigDict(extra="forbid")


async def chat_endpoint(request: Request) -> JSONResponse:
    """
    Chat endpoint for the local simulator.
    Receives a message, runs it through the OpenAI agent with MCP tools,
    and returns the response with any widget data.
    """
    try:
        body = await request.json()
        chat_request = ChatRequest.model_validate(body)
    except Exception as e:
        return JSONResponse(
            {"error": f"Invalid request: {e}"},
            status_code=400
        )

    try:
        # Import here to avoid circular imports
        from agent_runner import run_agent, WidgetResult

        result = await run_agent(
            prompt=chat_request.message,
            conversation_id=chat_request.conversation_id or "default"
        )

        # Build response
        widget_data = None
        if result.widget:
            widget_data = WidgetData(
                tool_name=result.widget.tool_name,
                html=result.widget.html,
                tool_output=result.widget.tool_output
            )

        response = ChatResponse(
            message=result.message,
            widget=widget_data,
            conversation_id=chat_request.conversation_id or "default"
        )

        return JSONResponse(response.model_dump())

    except Exception as e:
        return JSONResponse(
            {"error": str(e), "message": f"Error processing request: {e}"},
            status_code=500
        )


async def reset_chat_endpoint(request: Request) -> JSONResponse:
    """Reset conversation history."""
    try:
        body = await request.json()
        conversation_id = body.get("conversation_id", "default")
    except Exception:
        conversation_id = "default"

    try:
        from agent_runner import clear_conversation
        clear_conversation(conversation_id)
        return JSONResponse({"status": "ok", "conversation_id": conversation_id})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


# =============================================================================
# SIMULATOR STATUS & TOOLS API (for Puter.js fallback)
# =============================================================================

async def chat_status_endpoint(request: Request) -> JSONResponse:
    """
    Check if OpenAI API key is configured.
    Used by frontend to decide whether to use backend agent or Puter.js fallback.
    """
    import os
    from pathlib import Path
    from dotenv import load_dotenv

    # Load .env file
    env_path = Path(__file__).parent / ".env"
    if not env_path.exists():
        env_path = Path(__file__).parent.parent / ".env"
    load_dotenv(env_path)

    has_api_key = bool(os.getenv("OPENAI_API_KEY"))

    return JSONResponse({
        "has_api_key": has_api_key,
        "fallback_available": True,  # Puter.js is always available
    })


async def tools_list_endpoint(request: Request) -> JSONResponse:
    """
    Return tool definitions in OpenAI function calling format.
    Used by Puter.js fallback and the apptester to get available tools.

    IMPORTANT: Only returns widget tools (tools that produce HTML).
    Helper tools (poll_system_stats, geocode, etc.) are excluded because
    the apptester renders tools as widgets — calling a non-widget tool
    would crash with 'Cannot read properties of undefined (reading replace)'.
    Helper tools are still callable via /tools/call and registered in
    the MCP list_tools() for MCP host routing.
    """
    tools = []

    for widget in WIDGETS:
        input_model = WIDGET_INPUT_MODELS.get(widget.identifier)
        schema = get_tool_schema(input_model)
        tools.append({
            "type": "function",
            "function": {
                "name": widget.identifier,
                "description": widget.description,
                "parameters": schema,
            }
        })

    return JSONResponse({"tools": tools})


async def tool_call_endpoint(request: Request) -> JSONResponse:
    """
    Execute a tool and return the result.
    Used by Puter.js fallback to call MCP tools.
    Handles both widget tools (with HTML) and data-only tools (no HTML).
    """
    try:
        body = await request.json()
        tool_name = body.get("name")
        arguments = body.get("arguments", {})

        if not tool_name:
            return JSONResponse({"error": "Missing tool name"}, status_code=400)

        # Create a mock request and call the handler
        import mcp.types as types
        mock_req = types.CallToolRequest(
            method="tools/call",
            params=types.CallToolRequestParams(name=tool_name, arguments=arguments)
        )

        result = await handle_call_tool(mock_req)

        # Check if the handler returned an error
        if hasattr(result, 'root') and getattr(result.root, 'isError', False):
            error_text = result.root.content[0].text if result.root.content else "Unknown error"
            return JSONResponse({"error": error_text}, status_code=404)

        # Extract structured content from result
        if hasattr(result, 'root') and hasattr(result.root, 'structuredContent'):
            structured_content = result.root.structuredContent
        else:
            structured_content = {}

        # Widget tools include HTML; data-only tools return just the output
        widget = WIDGETS_BY_ID.get(tool_name)
        response: Dict[str, Any] = {
            "tool_name": tool_name,
            "tool_output": structured_content,
        }
        if widget:
            response["html"] = load_widget_html(widget.component_name)

        return JSONResponse(response)

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


# Add chat routes to the app
app.routes.append(Route("/chat", chat_endpoint, methods=["POST"]))
app.routes.append(Route("/chat/reset", reset_chat_endpoint, methods=["POST"]))
app.routes.append(Route("/chat/status", chat_status_endpoint, methods=["GET"]))
app.routes.append(Route("/tools", tools_list_endpoint, methods=["GET"]))
app.routes.append(Route("/tools/call", tool_call_endpoint, methods=["POST"]))


# =============================================================================
# SANDBOX PROXY SERVER (Port 8001)
# =============================================================================

class SandboxProxyHandler(SimpleHTTPRequestHandler):
    """HTTP handler that serves sandbox proxy with CSP headers.

    This runs on a different port (8001) to provide origin isolation.
    The CSP headers are applied based on query parameters or defaults.
    """

    def __init__(self, *args, **kwargs):
        # Serve from assets directory
        super().__init__(*args, directory=str(ASSETS_DIR), **kwargs)

    def end_headers(self):
        # Parse CSP from query params
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)

        # Build CSP directives
        resource_domains = query.get("resourceDomains", [])
        connect_domains = query.get("connectDomains", [])

        # Default domains if not specified
        csp_domains = get_csp_domains()
        if not resource_domains:
            resource_domains = csp_domains.get("resourceDomains", [])
        if not connect_domains:
            connect_domains = csp_domains.get("connectDomains", [])

        # Build CSP string
        resource_src = " ".join(resource_domains) if resource_domains else "'self'"
        connect_src = " ".join(connect_domains) if connect_domains else "'self'"

        csp = (
            f"default-src 'self'; "
            f"script-src 'self' 'unsafe-inline' 'unsafe-eval' blob: {resource_src}; "
            f"style-src 'self' 'unsafe-inline' {resource_src}; "
            f"img-src 'self' data: blob: {resource_src}; "
            f"font-src 'self' data: {resource_src}; "
            f"connect-src 'self' {connect_src}; "
            f"frame-src 'self' blob:; "
            f"worker-src 'self' blob: {resource_src};"
        )

        self.send_header("Content-Security-Policy", csp)
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        super().end_headers()

    def do_OPTIONS(self):
        """Handle CORS preflight requests."""
        self.send_response(200)
        self.end_headers()

    def log_message(self, format, *args):
        """Prefix log messages to distinguish from main server."""
        print(f"[Sandbox:8001] {args[0]}")


def start_sandbox_server(port: int = 8001) -> HTTPServer:
    """Start the sandbox proxy server on a separate port.

    This provides origin isolation for the MCP Apps sandbox.
    Raises OSError if the port is already in use.
    """
    server = HTTPServer(("0.0.0.0", port), SandboxProxyHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    print(f"Sandbox proxy server listening on http://0.0.0.0:{port}")
    return server


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    import uvicorn

    print("\n" + "=" * 60)
    print("MCP App Template - MCP Server")
    print("=" * 60)
    print("\nAvailable widgets:")
    for w in WIDGETS:
        print(f"  - {w.identifier}: {w.description[:50]}...")
    print("\nMake sure to run `pnpm run build` to build widgets first.")
    print("\nServer: http://0.0.0.0:8000")
    print("MCP endpoint: http://0.0.0.0:8000/mcp")
    print("Assets: http://0.0.0.0:8000/assets/")
    print("Sandbox: http://0.0.0.0:8001 (origin isolation)")
    print("=" * 60 + "\n")

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
