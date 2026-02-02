"""Boilerplate card widget."""

from __future__ import annotations

from typing import Any, Dict

import mcp.types as types
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from ._base import Widget, format_validation_error, get_invocation_meta

WIDGET = Widget(
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
)


class CardInput(BaseModel):
    """Input for card widget."""
    title: str = Field(default="Card Widget", description="Widget title")
    message: str = Field(default="Hello from the server!", description="Main message")
    accent_color: str = Field(default="#2563eb", alias="accentColor", description="Accent color (hex)")
    model_config = ConfigDict(populate_by_name=True, extra="forbid")


INPUT_MODEL = CardInput


async def handle(widget: Widget, arguments: Dict[str, Any]) -> types.ServerResult:
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
