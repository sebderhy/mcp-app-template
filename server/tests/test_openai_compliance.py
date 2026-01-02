"""
Tests for OpenAI Apps SDK format compliance.

These tests verify that tool responses and resources comply with OpenAI's
Apps SDK requirements as documented at:
https://developers.openai.com/apps-sdk/build/mcp-server

Key requirements tested:
1. Tool responses include structuredContent (for widget data)
2. Tool responses include content with TextContent (for model narration)
3. Resources use mimeType "text/html+skybridge" (required for widgets)
4. Tools have required _meta fields for OpenAI integration
5. Template URIs follow the ui://widget/ convention

These tests help catch issues that would cause widgets to fail in ChatGPT
before you go through the manual testing process.
"""

import pytest

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import mcp.types as types


class TestToolResponseFormat:
    """Tests that tool responses comply with OpenAI format requirements."""

    @pytest.mark.asyncio
    async def test_all_tools_return_structured_content(self):
        """Every tool must return structuredContent for the widget to read."""
        from main import handle_call_tool, WIDGETS

        for widget in WIDGETS:
            request = types.CallToolRequest(
                method="tools/call",
                params=types.CallToolRequestParams(
                    name=widget.identifier,
                    arguments={},
                ),
            )

            result = await handle_call_tool(request)

            assert result.root.structuredContent is not None, (
                f"Tool '{widget.identifier}' must return structuredContent. "
                "The widget reads data from window.openai.toolOutput which comes from structuredContent."
            )

    @pytest.mark.asyncio
    async def test_all_tools_return_text_content(self):
        """Every tool must return content with TextContent for model narration."""
        from main import handle_call_tool, WIDGETS

        for widget in WIDGETS:
            request = types.CallToolRequest(
                method="tools/call",
                params=types.CallToolRequestParams(
                    name=widget.identifier,
                    arguments={},
                ),
            )

            result = await handle_call_tool(request)

            assert result.root.content is not None, (
                f"Tool '{widget.identifier}' must return content. "
                "This provides narration text for the model's response."
            )
            assert len(result.root.content) > 0, (
                f"Tool '{widget.identifier}' content list is empty."
            )
            # First content should be TextContent
            assert result.root.content[0].type == "text", (
                f"Tool '{widget.identifier}' first content item must be type 'text'."
            )

    @pytest.mark.asyncio
    async def test_structured_content_is_json_serializable(self):
        """structuredContent must be JSON-serializable (dict with basic types)."""
        import json
        from main import handle_call_tool, WIDGETS

        for widget in WIDGETS:
            request = types.CallToolRequest(
                method="tools/call",
                params=types.CallToolRequestParams(
                    name=widget.identifier,
                    arguments={},
                ),
            )

            result = await handle_call_tool(request)

            try:
                json.dumps(result.root.structuredContent)
            except (TypeError, ValueError) as e:
                pytest.fail(
                    f"Tool '{widget.identifier}' structuredContent is not JSON-serializable: {e}"
                )


class TestResourceMimeType:
    """Tests that resources use correct MIME type for ChatGPT widgets."""

    @pytest.mark.asyncio
    async def test_all_resources_use_skybridge_mime_type(self):
        """Resources must use 'text/html+skybridge' MIME type."""
        from main import list_resources

        resources = await list_resources()

        for resource in resources:
            assert resource.mimeType == "text/html+skybridge", (
                f"Resource '{resource.name}' uses mimeType '{resource.mimeType}'. "
                "ChatGPT widgets require 'text/html+skybridge' to enable the widget runtime."
            )

    @pytest.mark.asyncio
    async def test_read_resource_returns_correct_mime_type(self):
        """handle_read_resource must return content with correct MIME type."""
        from main import handle_read_resource, WIDGETS

        for widget in WIDGETS:
            request = types.ReadResourceRequest(
                method="resources/read",
                params=types.ReadResourceRequestParams(uri=widget.template_uri),
            )

            result = await handle_read_resource(request)

            assert len(result.root.contents) == 1, (
                f"Widget '{widget.identifier}' resource should return exactly one content item."
            )
            assert result.root.contents[0].mimeType == "text/html+skybridge", (
                f"Widget '{widget.identifier}' resource content must have mimeType 'text/html+skybridge'."
            )


class TestTemplateUriConvention:
    """Tests that template URIs follow OpenAI conventions."""

    def test_all_widgets_use_ui_widget_uri_scheme(self):
        """Widget template URIs should follow ui://widget/ convention."""
        from main import WIDGETS

        for widget in WIDGETS:
            assert widget.template_uri.startswith("ui://widget/"), (
                f"Widget '{widget.identifier}' template_uri '{widget.template_uri}' "
                "should start with 'ui://widget/' per OpenAI convention."
            )

    def test_template_uri_ends_with_html(self):
        """Widget template URIs should end with .html."""
        from main import WIDGETS

        for widget in WIDGETS:
            assert widget.template_uri.endswith(".html"), (
                f"Widget '{widget.identifier}' template_uri '{widget.template_uri}' "
                "should end with '.html'."
            )


class TestToolMetadataRequirements:
    """Tests that tools have required OpenAI metadata."""

    def test_get_tool_meta_includes_output_template(self):
        """Tool metadata must include openai/outputTemplate."""
        from main import get_tool_meta, WIDGETS

        for widget in WIDGETS:
            meta = get_tool_meta(widget)

            assert "openai/outputTemplate" in meta, (
                f"Widget '{widget.identifier}' metadata missing 'openai/outputTemplate'. "
                "This links the tool to its widget HTML template."
            )
            assert meta["openai/outputTemplate"] == widget.template_uri, (
                f"Widget '{widget.identifier}' outputTemplate doesn't match template_uri."
            )

    def test_get_tool_meta_includes_invocation_messages(self):
        """Tool metadata must include invoking/invoked messages."""
        from main import get_tool_meta, WIDGETS

        for widget in WIDGETS:
            meta = get_tool_meta(widget)

            assert "openai/toolInvocation/invoking" in meta, (
                f"Widget '{widget.identifier}' metadata missing 'openai/toolInvocation/invoking'. "
                "This message shows while the tool is loading."
            )
            assert "openai/toolInvocation/invoked" in meta, (
                f"Widget '{widget.identifier}' metadata missing 'openai/toolInvocation/invoked'. "
                "This message shows when the tool completes."
            )

    def test_get_tool_meta_includes_widget_flags(self):
        """Tool metadata should include widget capability flags."""
        from main import get_tool_meta, WIDGETS

        for widget in WIDGETS:
            meta = get_tool_meta(widget)

            assert "openai/widgetAccessible" in meta, (
                f"Widget '{widget.identifier}' metadata missing 'openai/widgetAccessible'. "
                "Set to true if widget should be able to call other tools."
            )
            assert "openai/resultCanProduceWidget" in meta, (
                f"Widget '{widget.identifier}' metadata missing 'openai/resultCanProduceWidget'. "
                "Set to true to indicate this tool renders a widget."
            )

    def test_invocation_messages_are_non_empty(self):
        """Invocation messages must be non-empty strings."""
        from main import WIDGETS

        for widget in WIDGETS:
            assert widget.invoking and len(widget.invoking.strip()) > 0, (
                f"Widget '{widget.identifier}' has empty 'invoking' message."
            )
            assert widget.invoked and len(widget.invoked.strip()) > 0, (
                f"Widget '{widget.identifier}' has empty 'invoked' message."
            )


class TestToolAnnotations:
    """Tests that tools have proper safety annotations."""

    @pytest.mark.asyncio
    async def test_widget_tools_are_read_only(self):
        """Widget display tools should be marked as read-only."""
        from main import list_tools

        tools = await list_tools()

        for tool in tools:
            # Widget tools that just display data should be read-only
            assert tool.annotations.readOnlyHint is True, (
                f"Tool '{tool.name}' should have readOnlyHint=True. "
                "Display-only widgets don't modify external state."
            )

    @pytest.mark.asyncio
    async def test_widget_tools_are_non_destructive(self):
        """Widget display tools should be marked as non-destructive."""
        from main import list_tools

        tools = await list_tools()

        for tool in tools:
            assert tool.annotations.destructiveHint is False, (
                f"Tool '{tool.name}' should have destructiveHint=False. "
                "Display-only widgets don't destroy data."
            )


class TestWidgetHtmlContent:
    """Tests that widget HTML content meets requirements."""

    def test_widget_html_is_non_empty(self):
        """Widget HTML must be non-empty."""
        from main import WIDGETS

        for widget in WIDGETS:
            assert widget.html and len(widget.html.strip()) > 0, (
                f"Widget '{widget.identifier}' has empty HTML content. "
                "Run 'pnpm run build' to generate widget assets."
            )

    def test_widget_html_is_valid_html(self):
        """Widget HTML should contain basic HTML structure."""
        from main import WIDGETS

        for widget in WIDGETS:
            html = widget.html.lower()
            # Should have at least a script tag (the widget JS)
            assert "<script" in html or "script" in html, (
                f"Widget '{widget.identifier}' HTML should include a script tag "
                "to load the widget JavaScript."
            )


class TestWidgetIdentifiers:
    """Tests that widget identifiers follow conventions."""

    def test_identifiers_are_valid_tool_names(self):
        """Widget identifiers should be valid MCP tool names."""
        from main import WIDGETS
        import re

        for widget in WIDGETS:
            # Tool names should be lowercase with underscores
            assert re.match(r'^[a-z][a-z0-9_]*$', widget.identifier), (
                f"Widget identifier '{widget.identifier}' should be lowercase "
                "letters, numbers, and underscores, starting with a letter."
            )

    def test_identifiers_are_unique(self):
        """Widget identifiers must be unique."""
        from main import WIDGETS

        identifiers = [w.identifier for w in WIDGETS]
        assert len(identifiers) == len(set(identifiers)), (
            "Widget identifiers must be unique. Found duplicates."
        )

    def test_template_uris_are_unique(self):
        """Widget template URIs must be unique."""
        from main import WIDGETS

        uris = [w.template_uri for w in WIDGETS]
        assert len(uris) == len(set(uris)), (
            "Widget template URIs must be unique. Found duplicates."
        )
