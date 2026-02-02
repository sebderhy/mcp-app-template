"""List widget."""

from __future__ import annotations

from typing import Any, Dict

import mcp.types as types
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from ._base import Widget, format_validation_error, get_invocation_meta

WIDGET = Widget(
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
)


class ListInput(BaseModel):
    """Input for list widget."""
    title: str = Field(default="Top Picks", description="List title")
    subtitle: str = Field(default="Curated recommendations", description="List subtitle")
    category: str = Field(default="restaurants", description="Category of items")
    model_config = ConfigDict(populate_by_name=True, extra="forbid")


INPUT_MODEL = ListInput

SAMPLE_LIST_ITEMS = [
    {"id": "1", "title": "The Modern Kitchen", "subtitle": "Contemporary American", "image": "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=100&h=100&fit=crop", "rating": 4.9, "meta": "San Francisco", "badge": "#1"},
    {"id": "2", "title": "Bella Italia", "subtitle": "Authentic Italian", "image": "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=100&h=100&fit=crop", "rating": 4.8, "meta": "Oakland", "badge": "#2"},
    {"id": "3", "title": "Sakura Japanese", "subtitle": "Sushi & Izakaya", "image": "https://images.unsplash.com/photo-1579871494447-9811cf80d66c?w=100&h=100&fit=crop", "rating": 4.7, "meta": "Berkeley", "badge": "#3"},
    {"id": "4", "title": "Taco Loco", "subtitle": "Mexican Street Food", "image": "https://images.unsplash.com/photo-1565299585323-38d6b0865b47?w=100&h=100&fit=crop", "rating": 4.6, "meta": "San Jose"},
    {"id": "5", "title": "Golden Dragon", "subtitle": "Cantonese Cuisine", "image": "https://images.unsplash.com/photo-1552566626-52f8b828add9?w=100&h=100&fit=crop", "rating": 4.5, "meta": "Palo Alto"},
]


async def handle(widget: Widget, arguments: Dict[str, Any]) -> types.ServerResult:
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
