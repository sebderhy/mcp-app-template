"""QR code widget."""

from __future__ import annotations

import base64
import io
from typing import Any, Dict

import mcp.types as types
import qrcode
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from ._base import Widget, format_validation_error, get_invocation_meta

WIDGET = Widget(
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
)


class QrInput(BaseModel):
    """Input for QR code widget."""
    text: str = Field(default="https://modelcontextprotocol.io", description="Text or URL to encode")
    box_size: int = Field(default=10, alias="boxSize", description="Box size in pixels")
    border: int = Field(default=4, description="Border size in boxes")
    error_correction: str = Field(default="M", alias="errorCorrection", description="Error correction: L(7%), M(15%), Q(25%), H(30%)")
    fill_color: str = Field(default="black", alias="fillColor", description="Foreground color (hex or name)")
    back_color: str = Field(default="white", alias="backColor", description="Background color (hex or name)")
    model_config = ConfigDict(populate_by_name=True, extra="forbid")


INPUT_MODEL = QrInput


async def handle(widget: Widget, arguments: Dict[str, Any]) -> types.ServerResult:
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
