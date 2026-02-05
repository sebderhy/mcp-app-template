"""Solar system widget."""

from __future__ import annotations

from typing import Any, Dict, Literal, Optional

import mcp.types as types
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from ._base import Widget, format_validation_error, get_invocation_meta

WIDGET = Widget(
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
)


PlanetName = Literal["Mercury", "Venus", "Earth", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune"]


class SolarSystemInput(BaseModel):
    """Input for solar system widget."""
    planet_name: Optional[PlanetName] = Field(
        default=None,
        description="Planet to focus on. Options: Mercury, Venus, Earth, Mars, Jupiter, Saturn, Uranus, Neptune"
    )
    title: str = Field(default="Solar System Explorer", description="Widget title")
    model_config = ConfigDict(populate_by_name=True, extra="forbid")


INPUT_MODEL = SolarSystemInput


async def handle(widget: Widget, arguments: Dict[str, Any]) -> types.ServerResult:
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
