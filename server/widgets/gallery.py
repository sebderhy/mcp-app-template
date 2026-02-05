"""Gallery widget."""

from __future__ import annotations

from typing import Any, Dict, Literal

import mcp.types as types
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from ._base import Widget, format_validation_error, get_invocation_meta

WIDGET = Widget(
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
)


CategoryType = Literal["nature", "architecture", "portraits", "travel"]


class GalleryInput(BaseModel):
    """Input for gallery widget."""
    title: str = Field(default="Photo Gallery", description="Gallery title")
    category: CategoryType = Field(
        default="nature",
        description="Category of images. Options: nature, architecture, portraits, travel"
    )
    model_config = ConfigDict(populate_by_name=True, extra="forbid")


INPUT_MODEL = GalleryInput

SAMPLE_GALLERY_IMAGES = [
    {"id": "1", "src": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&h=600&fit=crop", "thumbnail": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=400&h=300&fit=crop", "title": "Mountain Sunrise", "description": "Alps at dawn", "author": "John Doe"},
    {"id": "2", "src": "https://images.unsplash.com/photo-1469474968028-56623f02e42e?w=800&h=600&fit=crop", "thumbnail": "https://images.unsplash.com/photo-1469474968028-56623f02e42e?w=400&h=300&fit=crop", "title": "Forest Path", "description": "Sunlit forest", "author": "Jane Smith"},
    {"id": "3", "src": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800&h=600&fit=crop", "thumbnail": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=400&h=300&fit=crop", "title": "Tropical Beach", "description": "Crystal waters", "author": "Mike Johnson"},
    {"id": "4", "src": "https://images.unsplash.com/photo-1519681393784-d120267933ba?w=800&h=600&fit=crop", "thumbnail": "https://images.unsplash.com/photo-1519681393784-d120267933ba?w=400&h=300&fit=crop", "title": "Starry Night", "description": "Milky Way", "author": "Sarah Wilson"},
    {"id": "5", "src": "https://images.unsplash.com/photo-1518837695005-2083093ee35b?w=800&h=600&fit=crop", "thumbnail": "https://images.unsplash.com/photo-1518837695005-2083093ee35b?w=400&h=300&fit=crop", "title": "Ocean Waves", "description": "Crashing waves", "author": "Tom Brown"},
    {"id": "6", "src": "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=800&h=600&fit=crop", "thumbnail": "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=400&h=300&fit=crop", "title": "Misty Forest", "description": "Morning fog", "author": "Emily Davis"},
]


async def handle(widget: Widget, arguments: Dict[str, Any]) -> types.ServerResult:
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
