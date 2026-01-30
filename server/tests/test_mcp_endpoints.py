"""
Tests for MCP protocol endpoints - Infrastructure tests.

These tests verify that the MCP protocol INFRASTRUCTURE works correctly:
1. list_tools returns properly formatted Tool objects
2. list_resources returns properly formatted Resource objects
3. handle_call_tool routes requests correctly
4. Error handling works for unknown tools/resources

Developers can add/remove widgets without modifying these tests,
as long as they follow the established patterns.
"""

import pytest

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import mcp.types as types


class TestListTools:
    """Tests for list_tools endpoint infrastructure."""

    @pytest.mark.asyncio
    async def test_returns_list_of_tools(self):
        """list_tools returns a list of Tool objects."""
        from main import list_tools

        tools = await list_tools()

        assert isinstance(tools, list)
        assert all(isinstance(t, types.Tool) for t in tools)

    @pytest.mark.asyncio
    async def test_tools_have_required_fields(self):
        """Each tool has all required fields."""
        from main import list_tools

        tools = await list_tools()

        for tool in tools:
            assert tool.name is not None, "Tool must have a name"
            assert tool.title is not None, "Tool must have a title"
            assert tool.description is not None, "Tool must have a description"
            assert tool.inputSchema is not None, "Tool must have an inputSchema"

    @pytest.mark.asyncio
    async def test_get_tool_meta_is_used(self):
        """Verify that get_tool_meta produces correct metadata structure."""
        from main import get_tool_meta, WIDGETS

        # Test that get_tool_meta returns correct structure for each widget
        # MCP Apps uses _meta.ui.resourceUri to link tools to their UI
        for widget in WIDGETS:
            meta = get_tool_meta(widget)
            assert "ui" in meta, "Tool must have ui metadata section"
            assert "resourceUri" in meta["ui"], "Tool must have ui.resourceUri"
            assert meta["ui"]["resourceUri"] == widget.template_uri

    @pytest.mark.asyncio
    async def test_tools_have_correct_annotations(self):
        """Each tool has correct safety annotations."""
        from main import list_tools

        tools = await list_tools()

        for tool in tools:
            assert tool.annotations is not None
            # Widget tools should be read-only and non-destructive
            # Access as Pydantic model attributes
            assert tool.annotations.destructiveHint is False
            assert tool.annotations.readOnlyHint is True

    @pytest.mark.asyncio
    async def test_tool_count_includes_widgets_and_helpers(self):
        """Number of tools is at least the number of widgets (may include helper tools)."""
        from main import list_tools, WIDGETS

        tools = await list_tools()

        assert len(tools) >= len(WIDGETS)
        # Every widget must have a corresponding tool
        tool_names = {t.name for t in tools}
        for widget in WIDGETS:
            assert widget.identifier in tool_names, f"Widget '{widget.identifier}' has no tool"


class TestToolsHttpEndpoint:
    """Tests for the HTTP /tools endpoint used by the apptester.

    The HTTP /tools endpoint serves the apptester and Puter.js.
    It must ONLY return widget tools (tools that produce HTML).
    Helper tools (poll_system_stats, geocode, etc.) must NOT appear
    because the apptester will try to render them and crash.
    """

    @pytest.mark.asyncio
    async def test_http_tools_only_returns_widget_tools(self):
        """HTTP /tools must only return tools that have a corresponding widget with HTML."""
        from main import tools_list_endpoint, WIDGETS_BY_ID
        from starlette.testclient import TestClient

        response = await tools_list_endpoint(None)
        import json
        data = json.loads(response.body)
        tool_names = [t["function"]["name"] for t in data["tools"]]

        for name in tool_names:
            assert name in WIDGETS_BY_ID, (
                f"HTTP /tools includes '{name}' which is not a widget. "
                f"Non-widget tools must not appear in the HTTP /tools endpoint "
                f"because the apptester will try to render them and crash."
            )

    @pytest.mark.asyncio
    async def test_http_tools_count_matches_widgets(self):
        """HTTP /tools must return exactly the number of widgets."""
        from main import tools_list_endpoint, WIDGETS
        import json

        response = await tools_list_endpoint(None)
        data = json.loads(response.body)

        assert len(data["tools"]) == len(WIDGETS), (
            f"HTTP /tools returned {len(data['tools'])} tools but there are {len(WIDGETS)} widgets. "
            f"Helper tools should not be in the HTTP /tools response."
        )

    @pytest.mark.asyncio
    async def test_helper_tools_are_callable_via_handle_call_tool(self):
        """Helper tools (not in WIDGETS) must still be callable via handle_call_tool."""
        from main import list_tools, WIDGETS_BY_ID, handle_call_tool

        all_tools = await list_tools()
        helper_tools = [t for t in all_tools if t.name not in WIDGETS_BY_ID]

        for tool in helper_tools:
            request = types.CallToolRequest(
                method="tools/call",
                params=types.CallToolRequestParams(name=tool.name, arguments={}),
            )
            result = await handle_call_tool(request)
            assert result.root.isError is not True, (
                f"Helper tool '{tool.name}' is registered in list_tools() but "
                f"handle_call_tool returns an error"
            )


class TestListResources:
    """Tests for list_resources endpoint infrastructure."""

    @pytest.mark.asyncio
    async def test_returns_list_of_resources(self):
        """list_resources returns a list of Resource objects."""
        from main import list_resources

        resources = await list_resources()

        assert isinstance(resources, list)
        assert all(isinstance(r, types.Resource) for r in resources)

    @pytest.mark.asyncio
    async def test_resources_have_required_fields(self):
        """Each resource has all required fields."""
        from main import list_resources

        resources = await list_resources()

        for resource in resources:
            assert resource.name is not None, "Resource must have a name"
            assert resource.uri is not None, "Resource must have a URI"
            assert resource.mimeType is not None, "Resource must have a mimeType"

    @pytest.mark.asyncio
    async def test_resources_have_correct_mime_type(self):
        """Resources have correct MIME type for ChatGPT widgets."""
        from main import list_resources, MIME_TYPE

        resources = await list_resources()

        for resource in resources:
            assert resource.mimeType == MIME_TYPE

    @pytest.mark.asyncio
    async def test_resource_count_matches_widgets(self):
        """Number of resources matches number of widgets."""
        from main import list_resources, WIDGETS

        resources = await list_resources()

        assert len(resources) == len(WIDGETS)


class TestHandleCallTool:
    """Tests for handle_call_tool dispatcher infrastructure."""

    @pytest.mark.asyncio
    async def test_unknown_tool_returns_error(self):
        """handle_call_tool returns error for unknown tool."""
        from main import handle_call_tool

        request = types.CallToolRequest(
            method="tools/call",
            params=types.CallToolRequestParams(
                name="completely_unknown_tool_that_does_not_exist",
                arguments={},
            ),
        )

        result = await handle_call_tool(request)

        assert result.root.isError is True
        assert "Unknown tool" in result.root.content[0].text

    @pytest.mark.asyncio
    async def test_known_tool_returns_success(self):
        """handle_call_tool returns success for known tools."""
        from main import handle_call_tool, WIDGETS

        if not WIDGETS:
            pytest.skip("No widgets loaded")

        # Use the first widget's identifier
        widget = WIDGETS[0]
        request = types.CallToolRequest(
            method="tools/call",
            params=types.CallToolRequestParams(
                name=widget.identifier,
                arguments={},
            ),
        )

        result = await handle_call_tool(request)

        assert result.root.isError is not True
        assert result.root.structuredContent is not None

    @pytest.mark.asyncio
    async def test_handles_none_arguments(self):
        """handle_call_tool handles None arguments gracefully."""
        from main import handle_call_tool, WIDGETS

        if not WIDGETS:
            pytest.skip("No widgets loaded")

        widget = WIDGETS[0]
        request = types.CallToolRequest(
            method="tools/call",
            params=types.CallToolRequestParams(
                name=widget.identifier,
                arguments=None,
            ),
        )

        result = await handle_call_tool(request)

        # Should use defaults, not crash
        assert result.root.isError is not True

    @pytest.mark.asyncio
    async def test_all_widgets_are_routable(self):
        """All registered widgets can be called."""
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

            assert result.root.isError is not True, f"Widget {widget.identifier} failed"
            assert result.root.structuredContent is not None, f"Widget {widget.identifier} missing structuredContent"


class TestHandleReadResource:
    """Tests for handle_read_resource infrastructure."""

    @pytest.mark.asyncio
    async def test_known_resource_returns_content(self):
        """handle_read_resource returns content for known resource."""
        from main import handle_read_resource, WIDGETS

        if not WIDGETS:
            pytest.skip("No widgets loaded")

        widget = WIDGETS[0]
        request = types.ReadResourceRequest(
            method="resources/read",
            params=types.ReadResourceRequestParams(uri=widget.template_uri),
        )

        result = await handle_read_resource(request)

        assert len(result.root.contents) == 1
        content = result.root.contents[0]
        assert content.text is not None
        assert len(content.text) > 0

    @pytest.mark.asyncio
    async def test_unknown_resource_returns_empty(self):
        """handle_read_resource returns empty for unknown resource."""
        from main import handle_read_resource

        request = types.ReadResourceRequest(
            method="resources/read",
            params=types.ReadResourceRequestParams(uri="ui://widget/unknown_widget.html"),
        )

        result = await handle_read_resource(request)

        assert len(result.root.contents) == 0

    @pytest.mark.asyncio
    async def test_all_widgets_resources_readable(self):
        """All registered widget resources can be read."""
        from main import handle_read_resource, WIDGETS

        for widget in WIDGETS:
            request = types.ReadResourceRequest(
                method="resources/read",
                params=types.ReadResourceRequestParams(uri=widget.template_uri),
            )

            result = await handle_read_resource(request)

            assert len(result.root.contents) == 1, f"Widget {widget.identifier} resource not readable"


class TestMetadataHelpers:
    """Tests for metadata helper functions."""

    def test_get_tool_meta_returns_required_keys(self):
        """get_tool_meta returns all required metadata keys."""
        from main import get_tool_meta, Widget

        widget = Widget(
            identifier="test",
            title="Test Widget",
            description="Test",
            template_uri="ui://widget/test.html",
            invoking="Loading...",
            invoked="Ready",
            html="<html></html>",
        )

        meta = get_tool_meta(widget)

        # MCP Apps uses ui.resourceUri to link tools to UI resources
        assert "ui" in meta
        assert "resourceUri" in meta["ui"]
        assert meta["ui"]["resourceUri"] == widget.template_uri

    def test_get_invocation_meta_returns_ui_metadata(self):
        """get_invocation_meta returns UI metadata."""
        from main import get_invocation_meta, Widget

        widget = Widget(
            identifier="test",
            title="Test Widget",
            description="Test",
            template_uri="ui://widget/test.html",
            invoking="Loading widget...",
            invoked="Widget ready",
            html="<html></html>",
        )

        meta = get_invocation_meta(widget)

        # MCP Apps uses ui.resourceUri for all UI-related metadata
        assert "ui" in meta
        assert "resourceUri" in meta["ui"]
