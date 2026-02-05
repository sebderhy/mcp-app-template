"""Carousel widget."""

from __future__ import annotations

from typing import Any, Dict, Literal

import mcp.types as types
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from ._base import Widget, format_validation_error, get_invocation_meta

WIDGET = Widget(
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
)


CategoryType = Literal["restaurants", "hotels", "products", "attractions"]


class CarouselInput(BaseModel):
    """Input for carousel widget."""
    title: str = Field(default="Recommendations", description="Carousel title")
    category: CategoryType = Field(
        default="restaurants",
        description="Category of items to show. Options: restaurants, hotels, products, attractions"
    )
    model_config = ConfigDict(populate_by_name=True, extra="forbid")


INPUT_MODEL = CarouselInput

SAMPLE_CAROUSEL_ITEMS = [
    {"id": "1", "title": "Golden Gate Bistro", "subtitle": "Modern American", "image": "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=400&h=300&fit=crop", "rating": 4.8, "location": "San Francisco", "price": "$$$", "badge": "Popular"},
    {"id": "2", "title": "Marina Bay Kitchen", "subtitle": "Fresh seafood", "image": "https://images.unsplash.com/photo-1552566626-52f8b828add9?w=400&h=300&fit=crop", "rating": 4.6, "location": "Oakland", "price": "$$"},
    {"id": "3", "title": "Sunset Terrace", "subtitle": "Rooftop dining", "image": "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=400&h=300&fit=crop", "rating": 4.9, "location": "Berkeley", "price": "$$$$", "badge": "New"},
    {"id": "4", "title": "The Local Table", "subtitle": "Farm-to-table", "image": "https://images.unsplash.com/photo-1466978913421-dad2ebd01d17?w=400&h=300&fit=crop", "rating": 4.5, "location": "Palo Alto", "price": "$$"},
    {"id": "5", "title": "Urban Spice", "subtitle": "Indian fusion", "image": "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=400&h=300&fit=crop", "rating": 4.7, "location": "San Jose", "price": "$$"},
]


async def handle(widget: Widget, arguments: Dict[str, Any]) -> types.ServerResult:
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
