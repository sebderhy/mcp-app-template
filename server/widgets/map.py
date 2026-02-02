"""Map widget."""

from __future__ import annotations

from typing import Any, Dict, List

import mcp.types as types
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from ._base import Widget, format_validation_error, get_invocation_meta

WIDGET = Widget(
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
)


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


INPUT_MODEL = ShowMapInput

# No sample places data needed (map widget uses bounding box coordinates)
SAMPLE_MAP_PLACES: List[Dict[str, Any]] = []


async def handle(widget: Widget, arguments: Dict[str, Any]) -> types.ServerResult:
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


DATA_ONLY_TOOLS = {
    "geocode": handle_geocode,
}
