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

import base64
import io
import math
import os
import platform
import socket
import time
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import mcp.types as types
import psutil
import qrcode
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from pydantic import BaseModel, ConfigDict, Field, ValidationError

# Load .env file at startup (for BASE_URL and other config)
_env_path = Path(__file__).parent / ".env"
if not _env_path.exists():
    _env_path = Path(__file__).parent.parent / ".env"
if _env_path.exists():
    load_dotenv(_env_path)

# =============================================================================
# CONFIGURATION
# =============================================================================

@dataclass(frozen=True)
class Widget:
    """Configuration for a widget that can be rendered in MCP Apps hosts."""
    identifier: str
    title: str
    description: str
    template_uri: str
    invoking: str
    invoked: str
    component_name: str


ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
# MCP Apps MIME type for UI resources
# The profile parameter signals this is an MCP App resource
MIME_TYPE = "text/html;profile=mcp-app"


# =============================================================================
# WIDGET HTML LOADING
# =============================================================================

_DEFAULT_BASE_URL = "http://localhost:8000/assets"

# Cache for loaded HTML with resolved URLs (keyed by component name)
_html_cache: Dict[str, str] = {}
_html_mtimes: Dict[str, float] = {}


def _clear_html_cache() -> None:
    """Clear the HTML cache. Used by tests."""
    _html_cache.clear()
    _html_mtimes.clear()


def get_base_url() -> str:
    """Get the base URL for assets from environment or use default."""
    return os.environ.get("BASE_URL", _DEFAULT_BASE_URL).rstrip("/")


def _resolve_html_path(component_name: str) -> Path:
    """Find the HTML file for a component, raising if not found."""
    html_path = ASSETS_DIR / f"{component_name}.html"
    if html_path.exists():
        return html_path

    fallback_candidates = sorted(ASSETS_DIR.glob(f"{component_name}-*.html"))
    if fallback_candidates:
        return fallback_candidates[-1]

    raise FileNotFoundError(
        f'Widget HTML for "{component_name}" not found in {ASSETS_DIR}. '
        "Run `pnpm run build` from the repo root to generate the assets."
    )


def load_widget_html(component_name: str) -> str:
    """Load the built widget HTML from the assets directory.

    Converts relative paths (./) to absolute URLs using BASE_URL env var.
    This is needed because widget HTML is injected into iframes via srcdoc,
    where relative paths don't resolve correctly.

    Results are cached per component name. The cache is automatically
    invalidated when the file's modification time changes, so rebuilding
    widgets takes effect without restarting the server.
    """
    html_path = _resolve_html_path(component_name)
    current_mtime = html_path.stat().st_mtime

    if component_name in _html_cache and _html_mtimes.get(component_name) == current_mtime:
        return _html_cache[component_name]

    html = html_path.read_text(encoding="utf8")

    # Convert relative paths to absolute URLs for srcdoc iframe compatibility
    # HTML files use "./" prefix which works for static serving but not srcdoc
    base_url = get_base_url()
    html = html.replace('src="./', f'src="{base_url}/')
    html = html.replace('href="./', f'href="{base_url}/')

    _html_cache[component_name] = html
    _html_mtimes[component_name] = current_mtime
    return html


# Add cache_clear method for test compatibility (mimics lru_cache interface)
load_widget_html.cache_clear = _clear_html_cache  # type: ignore[attr-defined]


# =============================================================================
# WIDGET DEFINITIONS
# =============================================================================

def create_widgets() -> List[Widget]:
    """Create all widget configurations."""
    return [
        Widget(
            identifier="show_card",
            title="Show Card Widget",
            description="""Display an interactive card widget with items.

Use this tool when:
- The user wants a simple, clean display of a few items
- You need a basic interactive widget that doesn't fit other categories
- Displaying a single entity with details and actions

Args:
    title: Widget header text (default: "Card Widget")
    message: Main message displayed in the card (default: "Hello from the server!")
    accentColor: Hex color for accent styling (default: "#2563eb")

Returns:
    Interactive card with title, message, accent color, and sample items list.

Example:
    show_card(title="Welcome", message="Click items below", accentColor="#10b981")""",
            template_uri="ui://widget/boilerplate.html",
            invoking="Loading card widget...",
            invoked="Card widget ready",
            component_name="boilerplate",
        ),
        Widget(
            identifier="show_carousel",
            title="Show Carousel",
            description="""Display a horizontal carousel of cards for browsing multiple items.

Use this tool when:
- The user asks for recommendations (restaurants, hotels, products)
- Showing a collection where users want to browse horizontally
- Displaying options with images, ratings, and quick info

Args:
    title: Carousel header text (default: "Recommendations")
    category: Category of items to display (default: "restaurants")

Returns:
    Horizontal scrolling carousel with cards containing:
    - Image thumbnail
    - Title and subtitle
    - Rating (1-5 stars)
    - Location and price level
    - Optional badge (e.g., "Popular", "New")

Example:
    show_carousel(title="Top Restaurants Near You", category="restaurants")""",
            template_uri="ui://widget/carousel.html",
            invoking="Loading carousel...",
            invoked="Carousel ready",
            component_name="carousel",
        ),
        Widget(
            identifier="show_list",
            title="Show List",
            description="""Display a vertical list with thumbnails and metadata.

Use this tool when:
- The user wants ranked/ordered content (top 10, best of, search results)
- Showing items where order and comparison matter
- Displaying task lists or sequential items

Args:
    title: List header text (default: "Top Picks")
    subtitle: Secondary header text (default: "Curated recommendations")
    category: Category of items to display (default: "restaurants")

Returns:
    Vertical scrolling list with items containing:
    - Thumbnail image
    - Title and subtitle
    - Rating
    - Metadata (location, etc.)
    - Optional rank badge (#1, #2, etc.)

Example:
    show_list(title="Top 5 Coffee Shops", subtitle="Based on reviews", category="cafes")""",
            template_uri="ui://widget/list.html",
            invoking="Loading list...",
            invoked="List ready",
            component_name="list",
        ),
        Widget(
            identifier="show_gallery",
            title="Show Gallery",
            description="""Display an image gallery with grid layout and lightbox viewer.

Use this tool when:
- The user wants to see photos or images
- Displaying visual portfolios, albums, or collections
- Images are the primary content (not just thumbnails)

Args:
    title: Gallery header text (default: "Photo Gallery")
    category: Category of images to display (default: "nature")

Returns:
    Image grid with lightbox functionality containing:
    - Thumbnail grid view
    - Full-size lightbox on click
    - Image title and description
    - Author attribution

Example:
    show_gallery(title="Nature Photography", category="nature")""",
            template_uri="ui://widget/gallery.html",
            invoking="Loading gallery...",
            invoked="Gallery ready",
            component_name="gallery",
        ),
        Widget(
            identifier="show_dashboard",
            title="Show Dashboard",
            description="""Display a dashboard with stats, metrics, and activity feed.

Use this tool when:
- The user wants to see analytics or KPIs
- Showing account overview or status information
- Displaying numerical data with trends

Args:
    title: Dashboard header text (default: "Dashboard")
    period: Time period label (default: "Last 30 days")

Returns:
    Dashboard layout with:
    - Stat cards (value, change percentage, icon)
    - Activity feed (recent events with timestamps)
    - Period selector display

Example:
    show_dashboard(title="Sales Overview", period="This month")""",
            template_uri="ui://widget/dashboard.html",
            invoking="Loading dashboard...",
            invoked="Dashboard ready",
            component_name="dashboard",
        ),
        Widget(
            identifier="show_solar_system",
            title="Show Solar System",
            description="""Display an interactive 3D solar system visualization.

Use this tool when:
- The user asks about planets, astronomy, or the solar system
- Educational content about space
- Interactive learning experiences

Args:
    title: Widget header text (default: "Solar System Explorer")
    planet_name: Optional planet to focus on (Mercury, Venus, Earth, Mars, Jupiter, Saturn, Uranus, Neptune)

Returns:
    Interactive 3D visualization with:
    - Animated planet orbits
    - Clickable planets with info panels
    - Planet details (size, distance, facts)

Example:
    show_solar_system(title="Explore the Planets", planet_name="Mars")""",
            template_uri="ui://widget/solar-system.html",
            invoking="Loading solar system...",
            invoked="Solar system ready",
            component_name="solar-system",
        ),
        Widget(
            identifier="show_todo",
            title="Show Todo List",
            description="""Display an interactive todo list manager with multiple lists.

Use this tool when:
- The user wants to organize tasks or create a todo list
- Managing multiple lists (work, personal, shopping)
- Tracking task completion and due dates

Args:
    title: Main title text (default: "My Tasks")

Returns:
    Todo manager interface with:
    - Multiple collapsible lists
    - Drag-and-drop reordering
    - Task completion checkboxes
    - Due date display
    - Add/edit/delete functionality

Example:
    show_todo(title="Today's Tasks")""",
            template_uri="ui://widget/todo.html",
            invoking="Loading todo list...",
            invoked="Todo list ready",
            component_name="todo",
        ),
        Widget(
            identifier="show_shop",
            title="Show Shopping Cart",
            description="""Display a shopping cart with products and checkout flow.

Use this tool when:
- The user wants to manage a shopping cart
- E-commerce checkout experiences
- Product quantity and price management

Args:
    title: Cart header text (default: "Your Cart")

Returns:
    Shopping cart interface with:
    - Product list with images and descriptions
    - Quantity controls (+/-)
    - Price calculations
    - Product tags (vegan, spicy, etc.)
    - Checkout button

Example:
    show_shop(title="Your Shopping Cart")""",
            template_uri="ui://widget/shop.html",
            invoking="Loading shopping cart...",
            invoked="Shopping cart ready",
            component_name="shop",
        ),
        Widget(
            identifier="show_qr",
            title="Generate QR Code",
            description="""Generate a QR code from text or a URL.

Use this tool when:
- The user wants to create a QR code
- Encoding a URL, text, or data as a scannable image
- Sharing links or information visually

Args:
    text: The text or URL to encode (default: "https://modelcontextprotocol.io")
    fill_color: Foreground color name or hex (default: "black")
    back_color: Background color name or hex (default: "white")

Returns:
    A QR code image displayed in the widget.

Example:
    show_qr(text="https://example.com", fill_color="#1a1a2e", back_color="#eaeaea")""",
            template_uri="ui://widget/qr.html",
            invoking="Generating QR code...",
            invoked="QR code ready",
            component_name="qr",
        ),
        Widget(
            identifier="get_scenario_data",
            title="SaaS Scenario Modeler",
            description="""Interactive SaaS financial projection tool with scenario templates.

Use this tool when:
- The user wants to model SaaS business scenarios
- Projecting revenue, profit, and growth over 12 months
- Comparing different business strategies (bootstrapped, VC-funded, etc.)

Args:
    starting_mrr: Starting monthly recurring revenue in dollars (default: 50000)
    monthly_growth_rate: Monthly growth rate percentage (default: 5)
    monthly_churn_rate: Monthly churn rate percentage (default: 3)
    gross_margin: Gross margin percentage (default: 80)
    fixed_costs: Fixed monthly costs in dollars (default: 30000)

Returns:
    Interactive widget with sliders, 12-month projection chart, and comparison
    against 5 pre-built scenario templates (Bootstrapped, VC Rocketship, Cash Cow,
    Turnaround, Efficient Growth).

Example:
    get_scenario_data(starting_mrr=100000, monthly_growth_rate=15)""",
            template_uri="ui://widget/scenario-modeler.html",
            invoking="Loading scenario modeler...",
            invoked="Scenario modeler ready",
            component_name="scenario-modeler",
        ),
        Widget(
            identifier="get_system_info",
            title="System Monitor",
            description="""Display real-time system monitoring with CPU and memory usage charts.

Use this tool when:
- The user asks about system performance or resource usage
- Monitoring CPU load or memory consumption
- Viewing system information (hostname, platform, uptime)

Args:
    (No parameters required - automatically detects system info)

Returns:
    Interactive widget with:
    - Per-core CPU usage chart (updates every 2 seconds)
    - Memory usage bar with percentage
    - System info (hostname, platform, uptime)

Example:
    get_system_info()""",
            template_uri="ui://widget/system-monitor.html",
            invoking="Loading system monitor...",
            invoked="System monitor ready",
            component_name="system-monitor",
        ),
        Widget(
            identifier="show_map",
            title="Show Map",
            description="""Display an interactive 3D globe zoomed to a specific location.

Use this tool when:
- The user asks about a geographic location
- Showing a place on a map
- Exploring areas visually

Use the geocode tool first to find coordinates for a place name.

Args:
    west: Western longitude boundary (default: -0.5)
    south: Southern latitude boundary (default: 51.3)
    east: Eastern longitude boundary (default: 0.3)
    north: Northern latitude boundary (default: 51.7)

Returns:
    Interactive 3D globe with OpenStreetMap tiles, centered on the given bounding box.

Example:
    show_map(west=2.2, south=48.8, east=2.5, north=48.9)""",
            template_uri="ui://widget/map.html",
            invoking="Loading map...",
            invoked="Map ready",
            component_name="map",
        ),
    ]


WIDGETS = create_widgets()

WIDGETS_BY_ID: Dict[str, Widget] = {w.identifier: w for w in WIDGETS}
WIDGETS_BY_URI: Dict[str, Widget] = {w.template_uri: w for w in WIDGETS}


# =============================================================================
# INPUT SCHEMAS
# =============================================================================

class CardInput(BaseModel):
    """Input for card widget."""
    title: str = Field(default="Card Widget", description="Widget title")
    message: str = Field(default="Hello from the server!", description="Main message")
    accent_color: str = Field(default="#2563eb", alias="accentColor", description="Accent color (hex)")
    model_config = ConfigDict(populate_by_name=True, extra="forbid")


class CarouselInput(BaseModel):
    """Input for carousel widget."""
    title: str = Field(default="Recommendations", description="Carousel title")
    category: str = Field(default="restaurants", description="Category of items to show")
    model_config = ConfigDict(populate_by_name=True, extra="forbid")


class ListInput(BaseModel):
    """Input for list widget."""
    title: str = Field(default="Top Picks", description="List title")
    subtitle: str = Field(default="Curated recommendations", description="List subtitle")
    category: str = Field(default="restaurants", description="Category of items")
    model_config = ConfigDict(populate_by_name=True, extra="forbid")


class GalleryInput(BaseModel):
    """Input for gallery widget."""
    title: str = Field(default="Photo Gallery", description="Gallery title")
    category: str = Field(default="nature", description="Category of images")
    model_config = ConfigDict(populate_by_name=True, extra="forbid")


class DashboardInput(BaseModel):
    """Input for dashboard widget."""
    title: str = Field(default="Dashboard", description="Dashboard title")
    period: str = Field(default="Last 30 days", description="Time period")
    model_config = ConfigDict(populate_by_name=True, extra="forbid")


class SolarSystemInput(BaseModel):
    """Input for solar system widget."""
    planet_name: Optional[str] = Field(default=None, description="Planet to focus on (Mercury, Venus, Earth, Mars, Jupiter, Saturn, Uranus, Neptune)")
    title: str = Field(default="Solar System Explorer", description="Widget title")
    model_config = ConfigDict(populate_by_name=True, extra="forbid")


class TodoInput(BaseModel):
    """Input for todo widget."""
    title: str = Field(default="My Tasks", description="Main title")
    model_config = ConfigDict(populate_by_name=True, extra="forbid")


class ShopInput(BaseModel):
    """Input for shop widget."""
    title: str = Field(default="Your Cart", description="Cart title")
    model_config = ConfigDict(populate_by_name=True, extra="forbid")


class QrInput(BaseModel):
    """Input for QR code widget."""
    text: str = Field(default="https://modelcontextprotocol.io", description="Text or URL to encode")
    box_size: int = Field(default=10, alias="boxSize", description="Box size in pixels")
    border: int = Field(default=4, description="Border size in boxes")
    error_correction: str = Field(default="M", alias="errorCorrection", description="Error correction: L(7%), M(15%), Q(25%), H(30%)")
    fill_color: str = Field(default="black", alias="fillColor", description="Foreground color (hex or name)")
    back_color: str = Field(default="white", alias="backColor", description="Background color (hex or name)")
    model_config = ConfigDict(populate_by_name=True, extra="forbid")


class ScenarioModelerInput(BaseModel):
    """Input for scenario modeler widget."""
    starting_mrr: float = Field(default=50000, alias="startingMRR", description="Starting MRR in dollars")
    monthly_growth_rate: float = Field(default=5, alias="monthlyGrowthRate", description="Monthly growth rate %")
    monthly_churn_rate: float = Field(default=3, alias="monthlyChurnRate", description="Monthly churn rate %")
    gross_margin: float = Field(default=80, alias="grossMargin", description="Gross margin %")
    fixed_costs: float = Field(default=30000, alias="fixedCosts", description="Fixed monthly costs")
    model_config = ConfigDict(populate_by_name=True, extra="forbid")


class SystemInfoInput(BaseModel):
    """Input for system monitor widget (no parameters needed)."""
    model_config = ConfigDict(extra="forbid")


class ShowMapInput(BaseModel):
    """Input for map widget."""
    west: float = Field(default=-0.5, description="Western longitude (-180 to 180)")
    south: float = Field(default=51.3, description="Southern latitude (-90 to 90)")
    east: float = Field(default=0.3, description="Eastern longitude (-180 to 180)")
    north: float = Field(default=51.7, description="Northern latitude (-90 to 90)")
    model_config = ConfigDict(populate_by_name=True, extra="forbid")


class GeocodeInput(BaseModel):
    """Input for geocode tool (data-only, no widget)."""
    query: str = Field(default="London", description="Place name or address to search for")
    model_config = ConfigDict(populate_by_name=True, extra="forbid")


# =============================================================================
# SAMPLE DATA
# =============================================================================

SAMPLE_CAROUSEL_ITEMS = [
    {"id": "1", "title": "Golden Gate Bistro", "subtitle": "Modern American", "image": "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=400&h=300&fit=crop", "rating": 4.8, "location": "San Francisco", "price": "$$$", "badge": "Popular"},
    {"id": "2", "title": "Marina Bay Kitchen", "subtitle": "Fresh seafood", "image": "https://images.unsplash.com/photo-1552566626-52f8b828add9?w=400&h=300&fit=crop", "rating": 4.6, "location": "Oakland", "price": "$$"},
    {"id": "3", "title": "Sunset Terrace", "subtitle": "Rooftop dining", "image": "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=400&h=300&fit=crop", "rating": 4.9, "location": "Berkeley", "price": "$$$$", "badge": "New"},
    {"id": "4", "title": "The Local Table", "subtitle": "Farm-to-table", "image": "https://images.unsplash.com/photo-1466978913421-dad2ebd01d17?w=400&h=300&fit=crop", "rating": 4.5, "location": "Palo Alto", "price": "$$"},
    {"id": "5", "title": "Urban Spice", "subtitle": "Indian fusion", "image": "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=400&h=300&fit=crop", "rating": 4.7, "location": "San Jose", "price": "$$"},
]

SAMPLE_LIST_ITEMS = [
    {"id": "1", "title": "The Modern Kitchen", "subtitle": "Contemporary American", "image": "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=100&h=100&fit=crop", "rating": 4.9, "meta": "San Francisco", "badge": "#1"},
    {"id": "2", "title": "Bella Italia", "subtitle": "Authentic Italian", "image": "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=100&h=100&fit=crop", "rating": 4.8, "meta": "Oakland", "badge": "#2"},
    {"id": "3", "title": "Sakura Japanese", "subtitle": "Sushi & Izakaya", "image": "https://images.unsplash.com/photo-1579871494447-9811cf80d66c?w=100&h=100&fit=crop", "rating": 4.7, "meta": "Berkeley", "badge": "#3"},
    {"id": "4", "title": "Taco Loco", "subtitle": "Mexican Street Food", "image": "https://images.unsplash.com/photo-1565299585323-38d6b0865b47?w=100&h=100&fit=crop", "rating": 4.6, "meta": "San Jose"},
    {"id": "5", "title": "Golden Dragon", "subtitle": "Cantonese Cuisine", "image": "https://images.unsplash.com/photo-1552566626-52f8b828add9?w=100&h=100&fit=crop", "rating": 4.5, "meta": "Palo Alto"},
]

SAMPLE_GALLERY_IMAGES = [
    {"id": "1", "src": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&h=600&fit=crop", "thumbnail": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=400&h=300&fit=crop", "title": "Mountain Sunrise", "description": "Alps at dawn", "author": "John Doe"},
    {"id": "2", "src": "https://images.unsplash.com/photo-1469474968028-56623f02e42e?w=800&h=600&fit=crop", "thumbnail": "https://images.unsplash.com/photo-1469474968028-56623f02e42e?w=400&h=300&fit=crop", "title": "Forest Path", "description": "Sunlit forest", "author": "Jane Smith"},
    {"id": "3", "src": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800&h=600&fit=crop", "thumbnail": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=400&h=300&fit=crop", "title": "Tropical Beach", "description": "Crystal waters", "author": "Mike Johnson"},
    {"id": "4", "src": "https://images.unsplash.com/photo-1519681393784-d120267933ba?w=800&h=600&fit=crop", "thumbnail": "https://images.unsplash.com/photo-1519681393784-d120267933ba?w=400&h=300&fit=crop", "title": "Starry Night", "description": "Milky Way", "author": "Sarah Wilson"},
    {"id": "5", "src": "https://images.unsplash.com/photo-1518837695005-2083093ee35b?w=800&h=600&fit=crop", "thumbnail": "https://images.unsplash.com/photo-1518837695005-2083093ee35b?w=400&h=300&fit=crop", "title": "Ocean Waves", "description": "Crashing waves", "author": "Tom Brown"},
    {"id": "6", "src": "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=800&h=600&fit=crop", "thumbnail": "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=400&h=300&fit=crop", "title": "Misty Forest", "description": "Morning fog", "author": "Emily Davis"},
]

SAMPLE_DASHBOARD_STATS = [
    {"id": "revenue", "label": "Total Revenue", "value": "$45,231.89", "change": 20.1, "changeLabel": "from last month", "icon": "dollar"},
    {"id": "users", "label": "Active Users", "value": "2,350", "change": 15.3, "changeLabel": "from last month", "icon": "users"},
    {"id": "orders", "label": "Orders", "value": "1,247", "change": -5.2, "changeLabel": "from last month", "icon": "cart"},
    {"id": "views", "label": "Page Views", "value": "573,921", "change": 12.5, "changeLabel": "from last month", "icon": "eye"},
]

SAMPLE_ACTIVITIES = [
    {"id": "1", "title": "New user registered", "description": "john.doe@example.com signed up", "time": "2 min ago", "type": "success"},
    {"id": "2", "title": "Order completed", "description": "Order #12345 fulfilled", "time": "15 min ago", "type": "info"},
    {"id": "3", "title": "Payment failed", "description": "$99.00 declined", "time": "1 hour ago", "type": "error"},
    {"id": "4", "title": "Low stock alert", "description": "SKU-789 running low", "time": "3 hours ago", "type": "warning"},
]

SAMPLE_TODO_LISTS = [
    {
        "id": "work",
        "title": "Work Tasks",
        "isCurrentlyOpen": True,
        "todos": [
            {"id": "1", "title": "Review pull requests", "isComplete": False, "note": "Check the new feature branch"},
            {"id": "2", "title": "Update documentation", "isComplete": True},
            {"id": "3", "title": "Team standup meeting", "isComplete": False, "dueDate": "2025-01-15"},
        ],
    },
    {
        "id": "personal",
        "title": "Personal",
        "todos": [
            {"id": "4", "title": "Buy groceries", "isComplete": False},
            {"id": "5", "title": "Call mom", "isComplete": False, "dueDate": "2025-01-14"},
        ],
    },
    {
        "id": "shopping",
        "title": "Shopping List",
        "todos": [
            {"id": "6", "title": "Milk", "isComplete": False},
            {"id": "7", "title": "Bread", "isComplete": True},
            {"id": "8", "title": "Eggs", "isComplete": False},
        ],
    },
]

SAMPLE_CART_ITEMS = [
    {
        "id": "marys-chicken",
        "name": "Mary's Chicken",
        "price": 19.48,
        "description": "Tender organic chicken breasts trimmed for easy cooking.",
        "shortDescription": "Organic chicken breasts",
        "detailSummary": "4 lbs - $3.99/lb",
        "quantity": 2,
        "image": "https://persistent.oaistatic.com/pizzaz-cart-xl/chicken.png",
        "tags": ["size"],
    },
    {
        "id": "avocados",
        "name": "Avocados",
        "price": 1.00,
        "description": "Creamy Hass avocados picked at peak ripeness.",
        "shortDescription": "Creamy Hass avocados",
        "quantity": 2,
        "image": "https://persistent.oaistatic.com/pizzaz-cart-xl/avocado.png",
        "tags": ["vegan"],
    },
    {
        "id": "hojicha-pizza",
        "name": "Hojicha Pizza",
        "price": 15.50,
        "description": "Wood-fired crust with smoky hojicha tea sauce and honey.",
        "shortDescription": "Smoky hojicha sauce & honey",
        "quantity": 1,
        "image": "https://persistent.oaistatic.com/pizzaz-cart-xl/hojicha-pizza.png",
        "tags": ["vegetarian", "spicy"],
    },
    {
        "id": "chicken-pizza",
        "name": "Chicken Pizza",
        "price": 7.00,
        "description": "Classic thin-crust pizza with roasted chicken and herb pesto.",
        "shortDescription": "Roasted chicken & pesto",
        "quantity": 1,
        "image": "https://persistent.oaistatic.com/pizzaz-cart-xl/chicken-pizza.png",
        "tags": [],
    },
    {
        "id": "matcha-pizza",
        "name": "Matcha Pizza",
        "price": 5.00,
        "description": "Crisp dough with velvety matcha cream and mascarpone.",
        "shortDescription": "Velvety matcha cream",
        "quantity": 1,
        "image": "https://persistent.oaistatic.com/pizzaz-cart-xl/matcha-pizza.png",
        "tags": ["vegetarian"],
    },
]

# No sample places data needed (map widget uses bounding box coordinates)
SAMPLE_MAP_PLACES: List[Dict[str, Any]] = []


# =============================================================================
# SCENARIO MODELER DATA
# =============================================================================

def _calculate_projections(starting_mrr: float, monthly_growth_rate: float,
                           monthly_churn_rate: float, gross_margin: float,
                           fixed_costs: float) -> List[Dict[str, Any]]:
    """Calculate 12-month SaaS projections."""
    net_growth_rate = (monthly_growth_rate - monthly_churn_rate) / 100
    projections = []
    cumulative_revenue = 0.0
    for month in range(1, 13):
        mrr = starting_mrr * math.pow(1 + net_growth_rate, month)
        gross_profit = mrr * (gross_margin / 100)
        net_profit = gross_profit - fixed_costs
        cumulative_revenue += mrr
        projections.append({
            "month": month, "mrr": mrr, "grossProfit": gross_profit,
            "netProfit": net_profit, "cumulativeRevenue": cumulative_revenue,
        })
    return projections


def _calculate_summary(projections: List[Dict[str, Any]], starting_mrr: float) -> Dict[str, Any]:
    """Calculate summary metrics from projections."""
    ending_mrr = projections[11]["mrr"]
    total_revenue = sum(p["mrr"] for p in projections)
    total_profit = sum(p["netProfit"] for p in projections)
    mrr_growth_pct = ((ending_mrr - starting_mrr) / starting_mrr) * 100
    avg_margin = (total_profit / total_revenue) * 100 if total_revenue else 0
    break_even = next((p["month"] for p in projections if p["netProfit"] >= 0), 0)
    return {
        "endingMRR": ending_mrr, "arr": ending_mrr * 12,
        "totalRevenue": total_revenue, "totalProfit": total_profit,
        "mrrGrowthPct": mrr_growth_pct, "avgMargin": avg_margin,
        "breakEvenMonth": break_even,
    }


def _build_scenario_template(id: str, name: str, description: str, icon: str,
                              params: Dict[str, Any], key_insight: str) -> Dict[str, Any]:
    """Build a complete scenario template with projections and summary."""
    projections = _calculate_projections(**params)
    summary = _calculate_summary(projections, params["starting_mrr"])
    return {
        "id": id, "name": name, "description": description, "icon": icon,
        "parameters": {
            "startingMRR": params["starting_mrr"],
            "monthlyGrowthRate": params["monthly_growth_rate"],
            "monthlyChurnRate": params["monthly_churn_rate"],
            "grossMargin": params["gross_margin"],
            "fixedCosts": params["fixed_costs"],
        },
        "projections": projections, "summary": summary, "keyInsight": key_insight,
    }


SCENARIO_TEMPLATES = [
    _build_scenario_template("bootstrapped", "Bootstrapped Growth",
        "Low burn, steady growth, path to profitability", "🌱",
        {"starting_mrr": 30000, "monthly_growth_rate": 4, "monthly_churn_rate": 2,
         "gross_margin": 85, "fixed_costs": 20000},
        "Profitable by month 1, but slower scale"),
    _build_scenario_template("vc-rocketship", "VC Rocketship",
        "High burn, explosive growth, raise more later", "🚀",
        {"starting_mrr": 100000, "monthly_growth_rate": 15, "monthly_churn_rate": 5,
         "gross_margin": 70, "fixed_costs": 150000},
        "Loses money early but ends at 3x MRR"),
    _build_scenario_template("cash-cow", "Cash Cow",
        "Mature product, high margin, stable revenue", "🐄",
        {"starting_mrr": 80000, "monthly_growth_rate": 2, "monthly_churn_rate": 1,
         "gross_margin": 90, "fixed_costs": 40000},
        "Consistent profitability, low risk"),
    _build_scenario_template("turnaround", "Turnaround",
        "Fighting churn, rebuilding product-market fit", "🔄",
        {"starting_mrr": 60000, "monthly_growth_rate": 6, "monthly_churn_rate": 8,
         "gross_margin": 75, "fixed_costs": 50000},
        "Negative net growth requires urgent action"),
    _build_scenario_template("efficient-growth", "Efficient Growth",
        "Balanced approach with sustainable economics", "⚖️",
        {"starting_mrr": 50000, "monthly_growth_rate": 8, "monthly_churn_rate": 3,
         "gross_margin": 80, "fixed_costs": 35000},
        "Good growth with path to profitability"),
]

SCENARIO_DEFAULT_INPUTS = {
    "startingMRR": 50000, "monthlyGrowthRate": 5, "monthlyChurnRate": 3,
    "grossMargin": 80, "fixedCosts": 30000,
}


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


# External CDN domains used by the template widgets
# Add any external domains your widgets need for images, fonts, or API calls
EXTERNAL_RESOURCE_DOMAINS: List[str] = [
    "https://cdn.openai.com",           # Fonts from @openai/apps-sdk-ui
    "https://images.unsplash.com",      # Sample images in demo widgets
    "https://persistent.oaistatic.com", # Sample images in demo widgets
    "https://cesium.com",               # CesiumJS CDN for map widget
    "https://tile.openstreetmap.org",   # OpenStreetMap tiles for map widget
]

# Domains that need fetch/XHR access (connect-src).
# CesiumJS loads assets (JSON, textures, workers) and OSM tiles via fetch.
EXTERNAL_CONNECT_DOMAINS: List[str] = [
    "https://cesium.com",               # CesiumJS assets (JSON, textures, workers)
    "https://tile.openstreetmap.org",   # OpenStreetMap tile images loaded via XHR
]


def get_csp_domains() -> Dict[str, List[str]]:
    """Return CSP domains based on the current BASE_URL.

    This allows the MCP App sandbox to load external assets (JS, CSS, images)
    from our server and from external CDNs.
    """
    base_url = get_base_url()
    # Extract origin from base URL (e.g., "http://localhost:8000" from "http://localhost:8000/assets")
    from urllib.parse import urlparse
    parsed = urlparse(base_url)
    origin = f"{parsed.scheme}://{parsed.netloc}"

    # Combine server origin with external CDN domains
    resource_domains = [origin] + EXTERNAL_RESOURCE_DOMAINS
    connect_domains = [origin] + EXTERNAL_CONNECT_DOMAINS

    return {
        "resourceDomains": resource_domains,  # For scripts, styles, images, fonts
        "connectDomains": connect_domains,    # For fetch/XHR requests
    }


def get_tool_meta(widget: Widget) -> Dict[str, Any]:
    """Return MCP Apps metadata for a tool.

    The key field is `ui.resourceUri` which links the tool to its UI resource.
    The `csp` field specifies Content Security Policy domains for the sandbox.
    This follows the MCP Apps protocol specification.
    """
    return {
        "ui": {
            "resourceUri": widget.template_uri,
            "csp": get_csp_domains(),
        },
    }


def get_invocation_meta(widget: Widget) -> Dict[str, Any]:
    """Return metadata for tool invocation results."""
    return {
        "ui": {
            "resourceUri": widget.template_uri,
            "csp": get_csp_domains(),
        },
    }


# =============================================================================
# TOOL REGISTRATION
# =============================================================================

# Map widget identifiers to their input models for proper schema generation
WIDGET_INPUT_MODELS: Dict[str, type] = {
    "show_card": CardInput,
    "show_carousel": CarouselInput,
    "show_list": ListInput,
    "show_gallery": GalleryInput,
    "show_dashboard": DashboardInput,
    "show_solar_system": SolarSystemInput,
    "show_todo": TodoInput,
    "show_shop": ShopInput,
    "show_qr": QrInput,
    "get_scenario_data": ScenarioModelerInput,
    "get_system_info": SystemInfoInput,
    "show_map": ShowMapInput,
}


def get_tool_schema(widget_id: str) -> Dict[str, Any]:
    """Generate JSON Schema from the Pydantic model for a widget."""
    model_class = WIDGET_INPUT_MODELS.get(widget_id)
    if not model_class:
        return {"type": "object", "properties": {}, "additionalProperties": False}

    # Generate schema from Pydantic model
    pydantic_schema = model_class.model_json_schema()

    # Convert to MCP-compatible format (remove $defs and other extras)
    properties = {}
    for field_name, field_info in pydantic_schema.get("properties", {}).items():
        prop = {"type": field_info.get("type", "string")}
        if "description" in field_info:
            prop["description"] = field_info["description"]
        if "default" in field_info:
            prop["default"] = field_info["default"]
        properties[field_name] = prop

    return {
        "type": "object",
        "properties": properties,
        "additionalProperties": False,
    }


@mcp._mcp_server.list_tools()
async def list_tools() -> List[types.Tool]:
    tools = []

    for widget in WIDGETS:
        schema = get_tool_schema(widget.identifier)

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

    # Handle data-only tools first (no widget UI)
    if tool_name == "poll_system_stats":
        return await handle_poll_system_stats(arguments)
    elif tool_name == "geocode":
        return await handle_geocode(arguments)

    widget = WIDGETS_BY_ID.get(tool_name)
    if not widget:
        return types.ServerResult(types.CallToolResult(
            content=[types.TextContent(type="text", text=f"Unknown tool: {tool_name}")],
            isError=True,
        ))

    # Route to appropriate handler based on tool name
    if tool_name == "show_card":
        return await handle_card(widget, arguments)
    elif tool_name == "show_carousel":
        return await handle_carousel(widget, arguments)
    elif tool_name == "show_list":
        return await handle_list(widget, arguments)
    elif tool_name == "show_gallery":
        return await handle_gallery(widget, arguments)
    elif tool_name == "show_dashboard":
        return await handle_dashboard(widget, arguments)
    elif tool_name == "show_solar_system":
        return await handle_solar_system(widget, arguments)
    elif tool_name == "show_todo":
        return await handle_todo(widget, arguments)
    elif tool_name == "show_shop":
        return await handle_shop(widget, arguments)
    elif tool_name == "show_qr":
        return await handle_qr(widget, arguments)
    elif tool_name == "get_scenario_data":
        return await handle_scenario_modeler(widget, arguments)
    elif tool_name == "get_system_info":
        return await handle_system_info(widget, arguments)
    elif tool_name == "show_map":
        return await handle_show_map(widget, arguments)
    else:
        return types.ServerResult(types.CallToolResult(
            content=[types.TextContent(type="text", text=f"No handler for: {tool_name}")],
            isError=True,
        ))


def format_validation_error(e: ValidationError, input_class: type) -> str:
    """Format Pydantic validation errors into actionable messages."""
    errors = e.errors()
    field_errors = []
    for err in errors:
        field = ".".join(str(x) for x in err["loc"]) if err["loc"] else "input"
        msg = err["msg"]
        field_errors.append(f"  - {field}: {msg}")

    # Get valid field names from the model
    valid_fields = list(input_class.model_fields.keys())

    error_msg = f"Validation error. Issues:\n"
    error_msg += "\n".join(field_errors)
    error_msg += f"\n\nValid fields: {', '.join(valid_fields)}"
    return error_msg


async def handle_card(widget: Widget, arguments: Dict[str, Any]) -> types.ServerResult:
    try:
        payload = CardInput.model_validate(arguments)
    except ValidationError as e:
        error_msg = format_validation_error(e, CardInput)
        return types.ServerResult(types.CallToolResult(
            content=[types.TextContent(type="text", text=error_msg)],
            isError=True,
        ))

    structured_content = {
        "title": payload.title,
        "message": payload.message,
        "accentColor": payload.accent_color,
        "items": [
            {"id": "1", "name": "First Item", "description": "Sample item description"},
            {"id": "2", "name": "Second Item", "description": "Another sample item"},
            {"id": "3", "name": "Third Item", "description": "One more item"},
        ],
    }

    return types.ServerResult(types.CallToolResult(
        content=[types.TextContent(type="text", text=f"Card widget: {payload.title}")],
        structuredContent=structured_content,
        _meta=get_invocation_meta(widget),
    ))


async def handle_carousel(widget: Widget, arguments: Dict[str, Any]) -> types.ServerResult:
    try:
        payload = CarouselInput.model_validate(arguments)
    except ValidationError as e:
        error_msg = format_validation_error(e, CarouselInput)
        return types.ServerResult(types.CallToolResult(
            content=[types.TextContent(type="text", text=error_msg)],
            isError=True,
        ))

    structured_content = {
        "title": payload.title,
        "items": SAMPLE_CAROUSEL_ITEMS,
    }

    return types.ServerResult(types.CallToolResult(
        content=[types.TextContent(type="text", text=f"Carousel: {payload.title} ({len(SAMPLE_CAROUSEL_ITEMS)} items)")],
        structuredContent=structured_content,
        _meta=get_invocation_meta(widget),
    ))


async def handle_list(widget: Widget, arguments: Dict[str, Any]) -> types.ServerResult:
    try:
        payload = ListInput.model_validate(arguments)
    except ValidationError as e:
        error_msg = format_validation_error(e, ListInput)
        return types.ServerResult(types.CallToolResult(
            content=[types.TextContent(type="text", text=error_msg)],
            isError=True,
        ))

    structured_content = {
        "title": payload.title,
        "subtitle": payload.subtitle,
        "headerImage": "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=200&h=200&fit=crop",
        "actionLabel": "Save List",
        "items": SAMPLE_LIST_ITEMS,
    }

    return types.ServerResult(types.CallToolResult(
        content=[types.TextContent(type="text", text=f"List: {payload.title} ({len(SAMPLE_LIST_ITEMS)} items)")],
        structuredContent=structured_content,
        _meta=get_invocation_meta(widget),
    ))


async def handle_gallery(widget: Widget, arguments: Dict[str, Any]) -> types.ServerResult:
    try:
        payload = GalleryInput.model_validate(arguments)
    except ValidationError as e:
        error_msg = format_validation_error(e, GalleryInput)
        return types.ServerResult(types.CallToolResult(
            content=[types.TextContent(type="text", text=error_msg)],
            isError=True,
        ))

    structured_content = {
        "title": payload.title,
        "images": SAMPLE_GALLERY_IMAGES,
    }

    return types.ServerResult(types.CallToolResult(
        content=[types.TextContent(type="text", text=f"Gallery: {payload.title} ({len(SAMPLE_GALLERY_IMAGES)} photos)")],
        structuredContent=structured_content,
        _meta=get_invocation_meta(widget),
    ))


async def handle_dashboard(widget: Widget, arguments: Dict[str, Any]) -> types.ServerResult:
    try:
        payload = DashboardInput.model_validate(arguments)
    except ValidationError as e:
        error_msg = format_validation_error(e, DashboardInput)
        return types.ServerResult(types.CallToolResult(
            content=[types.TextContent(type="text", text=error_msg)],
            isError=True,
        ))

    structured_content = {
        "title": payload.title,
        "subtitle": "Your key metrics at a glance",
        "period": payload.period,
        "stats": SAMPLE_DASHBOARD_STATS,
        "activities": SAMPLE_ACTIVITIES,
    }

    return types.ServerResult(types.CallToolResult(
        content=[types.TextContent(type="text", text=f"Dashboard: {payload.title}")],
        structuredContent=structured_content,
        _meta=get_invocation_meta(widget),
    ))


async def handle_solar_system(widget: Widget, arguments: Dict[str, Any]) -> types.ServerResult:
    try:
        payload = SolarSystemInput.model_validate(arguments)
    except ValidationError as e:
        error_msg = format_validation_error(e, SolarSystemInput)
        return types.ServerResult(types.CallToolResult(
            content=[types.TextContent(type="text", text=error_msg)],
            isError=True,
        ))

    structured_content = {
        "title": payload.title,
        "planet_name": payload.planet_name or "",  # Empty string instead of null
    }

    planet_msg = f" (focusing on {payload.planet_name})" if payload.planet_name else ""
    return types.ServerResult(types.CallToolResult(
        content=[types.TextContent(type="text", text=f"Solar System{planet_msg}")],
        structuredContent=structured_content,
        _meta=get_invocation_meta(widget),
    ))


async def handle_todo(widget: Widget, arguments: Dict[str, Any]) -> types.ServerResult:
    try:
        payload = TodoInput.model_validate(arguments)
    except ValidationError as e:
        error_msg = format_validation_error(e, TodoInput)
        return types.ServerResult(types.CallToolResult(
            content=[types.TextContent(type="text", text=error_msg)],
            isError=True,
        ))

    structured_content = {
        "lists": deepcopy(SAMPLE_TODO_LISTS),
    }

    total_todos = sum(len(lst["todos"]) for lst in SAMPLE_TODO_LISTS)
    return types.ServerResult(types.CallToolResult(
        content=[types.TextContent(type="text", text=f"Todo: {len(SAMPLE_TODO_LISTS)} lists, {total_todos} items")],
        structuredContent=structured_content,
        _meta=get_invocation_meta(widget),
    ))


async def handle_shop(widget: Widget, arguments: Dict[str, Any]) -> types.ServerResult:
    try:
        payload = ShopInput.model_validate(arguments)
    except ValidationError as e:
        error_msg = format_validation_error(e, ShopInput)
        return types.ServerResult(types.CallToolResult(
            content=[types.TextContent(type="text", text=error_msg)],
            isError=True,
        ))

    structured_content = {
        "title": payload.title,
        "cartItems": deepcopy(SAMPLE_CART_ITEMS),
    }

    total_items = sum(item["quantity"] for item in SAMPLE_CART_ITEMS)
    return types.ServerResult(types.CallToolResult(
        content=[types.TextContent(type="text", text=f"Shopping Cart: {total_items} items")],
        structuredContent=structured_content,
        _meta=get_invocation_meta(widget),
    ))


async def handle_qr(widget: Widget, arguments: Dict[str, Any]) -> types.ServerResult:
    try:
        payload = QrInput.model_validate(arguments)
    except ValidationError as e:
        error_msg = format_validation_error(e, QrInput)
        return types.ServerResult(types.CallToolResult(
            content=[types.TextContent(type="text", text=error_msg)],
            isError=True,
        ))

    error_levels = {
        "L": qrcode.constants.ERROR_CORRECT_L,
        "M": qrcode.constants.ERROR_CORRECT_M,
        "Q": qrcode.constants.ERROR_CORRECT_Q,
        "H": qrcode.constants.ERROR_CORRECT_H,
    }

    # Clamp/default to valid values
    text = payload.text or "https://modelcontextprotocol.io"
    box_size = max(1, payload.box_size)
    border = max(0, payload.border)
    fill_color = payload.fill_color or "black"
    back_color = payload.back_color or "white"
    ec_key = (payload.error_correction or "M").upper()

    qr = qrcode.QRCode(
        version=1,
        error_correction=error_levels.get(ec_key, qrcode.constants.ERROR_CORRECT_M),
        box_size=box_size,
        border=border,
    )
    qr.add_data(text)
    qr.make(fit=True)

    img = qr.make_image(fill_color=fill_color, back_color=back_color)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    b64 = base64.b64encode(buffer.getvalue()).decode()

    structured_content = {
        "imageData": b64,
        "mimeType": "image/png",
    }

    return types.ServerResult(types.CallToolResult(
        content=[
            types.TextContent(type="text", text=f"QR code generated for: {text}"),
            types.ImageContent(type="image", data=b64, mimeType="image/png"),
        ],
        structuredContent=structured_content,
        _meta=get_invocation_meta(widget),
    ))


async def handle_scenario_modeler(widget: Widget, arguments: Dict[str, Any]) -> types.ServerResult:
    try:
        payload = ScenarioModelerInput.model_validate(arguments)
    except ValidationError as e:
        error_msg = format_validation_error(e, ScenarioModelerInput)
        return types.ServerResult(types.CallToolResult(
            content=[types.TextContent(type="text", text=error_msg)],
            isError=True,
        ))

    structured_content = {
        "templates": deepcopy(SCENARIO_TEMPLATES),
        "defaultInputs": SCENARIO_DEFAULT_INPUTS,
    }

    return types.ServerResult(types.CallToolResult(
        content=[types.TextContent(type="text", text=f"SaaS Scenario Modeler ({len(SCENARIO_TEMPLATES)} templates)")],
        structuredContent=structured_content,
        _meta=get_invocation_meta(widget),
    ))


async def handle_system_info(widget: Widget, arguments: Dict[str, Any]) -> types.ServerResult:
    try:
        SystemInfoInput.model_validate(arguments)
    except ValidationError as e:
        error_msg = format_validation_error(e, SystemInfoInput)
        return types.ServerResult(types.CallToolResult(
            content=[types.TextContent(type="text", text=error_msg)],
            isError=True,
        ))

    info = {
        "hostname": socket.gethostname(),
        "platform": f"{platform.system()} {platform.machine()}",
        "cpu": {
            "model": platform.processor() or "Unknown",
            "count": psutil.cpu_count() or 1,
        },
        "memory": {
            "totalBytes": psutil.virtual_memory().total,
        },
    }

    return types.ServerResult(types.CallToolResult(
        content=[types.TextContent(type="text", text=f"System: {info['hostname']} ({info['platform']})")],
        structuredContent=info,
        _meta=get_invocation_meta(widget),
    ))


async def handle_poll_system_stats(arguments: Dict[str, Any]) -> types.ServerResult:
    """App-only handler: returns live CPU and memory stats for polling."""
    cpu_percents = psutil.cpu_percent(percpu=True)
    mem = psutil.virtual_memory()

    stats = {
        "cpuPercents": cpu_percents,
        "memoryPercent": mem.percent,
        "memoryUsedGB": round(mem.used / (1024 ** 3), 2),
        "memoryTotalGB": round(mem.total / (1024 ** 3), 2),
        "uptime": int(time.time() - psutil.boot_time()),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    return types.ServerResult(types.CallToolResult(
        content=[types.TextContent(type="text", text=f"CPU: {cpu_percents}, Memory: {mem.percent}%")],
        structuredContent=stats,
    ))


async def handle_show_map(widget: Widget, arguments: Dict[str, Any]) -> types.ServerResult:
    try:
        payload = ShowMapInput.model_validate(arguments)
    except ValidationError as e:
        error_msg = format_validation_error(e, ShowMapInput)
        return types.ServerResult(types.CallToolResult(
            content=[types.TextContent(type="text", text=error_msg)],
            isError=True,
        ))

    structured_content = {
        "west": payload.west,
        "south": payload.south,
        "east": payload.east,
        "north": payload.north,
    }

    return types.ServerResult(types.CallToolResult(
        content=[types.TextContent(type="text", text=f"Map: W:{payload.west:.4f} S:{payload.south:.4f} E:{payload.east:.4f} N:{payload.north:.4f}")],
        structuredContent=structured_content,
        _meta=get_invocation_meta(widget),
    ))


async def handle_geocode(arguments: Dict[str, Any]) -> types.ServerResult:
    """Data-only handler: geocodes a location using OpenStreetMap Nominatim."""
    import httpx

    try:
        payload = GeocodeInput.model_validate(arguments)
    except ValidationError as e:
        error_msg = format_validation_error(e, GeocodeInput)
        return types.ServerResult(types.CallToolResult(
            content=[types.TextContent(type="text", text=error_msg)],
            isError=True,
        ))

    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": payload.query, "format": "json", "limit": "5"},
            headers={"User-Agent": "MCP-App-Template/1.0"},
        )
        response.raise_for_status()
        results = response.json()

    if not results:
        return types.ServerResult(types.CallToolResult(
            content=[types.TextContent(type="text", text=f'No results found for "{payload.query}"')],
        ))

    formatted = []
    for r in results:
        bb = r.get("boundingbox", ["0", "0", "0", "0"])
        formatted.append(
            f"{r['display_name']}\n"
            f"  Coordinates: {r['lat']}, {r['lon']}\n"
            f"  Bounding box: W:{bb[2]}, S:{bb[0]}, E:{bb[3]}, N:{bb[1]}"
        )

    return types.ServerResult(types.CallToolResult(
        content=[types.TextContent(type="text", text="\n\n".join(formatted))],
    ))


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
        schema = get_tool_schema(widget.identifier)
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

import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs


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
