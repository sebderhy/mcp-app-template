"""
Tests for MCP tool handlers - Infrastructure tests.

These tests verify the FRAMEWORK behavior, not the specific business logic.
They check that:
1. Handlers return properly structured responses
2. Custom inputs are passed through correctly
3. structuredContent has the expected shape for each widget type
4. Handlers don't crash with empty or minimal input

Developers modifying the template should NOT need to modify these tests
unless they change the fundamental structure of a widget type.
"""

import pytest

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from main import (
    Widget,
    handle_card,
    handle_carousel,
    handle_list,
    handle_gallery,
    handle_dashboard,
    handle_solar_system,
    handle_todo,
    handle_shop,
)


@pytest.fixture
def mock_widget():
    """Create a mock widget for handler tests."""
    return Widget(
        identifier="test_widget",
        title="Test Widget",
        description="A test widget",
        template_uri="ui://widget/test.html",
        invoking="Loading...",
        invoked="Ready",
        html="<html></html>",
    )


class TestHandleCard:
    """Tests for handle_card handler structure."""

    @pytest.mark.asyncio
    async def test_returns_structured_content_with_required_keys(self, mock_widget):
        """handle_card returns structuredContent with required keys."""
        result = await handle_card(mock_widget, {})
        content = result.root.structuredContent

        assert content is not None
        # These keys define the card widget contract
        assert "title" in content
        assert "message" in content
        assert "accentColor" in content
        assert "items" in content

    @pytest.mark.asyncio
    async def test_items_is_a_list(self, mock_widget):
        """handle_card returns items as a list."""
        result = await handle_card(mock_widget, {})
        items = result.root.structuredContent["items"]

        assert isinstance(items, list)

    @pytest.mark.asyncio
    async def test_custom_title_passes_through(self, mock_widget):
        """handle_card uses provided title."""
        custom_title = "My Custom Card Title"
        result = await handle_card(mock_widget, {"title": custom_title})
        content = result.root.structuredContent

        assert content["title"] == custom_title

    @pytest.mark.asyncio
    async def test_custom_message_passes_through(self, mock_widget):
        """handle_card uses provided message."""
        custom_message = "Custom message content"
        result = await handle_card(mock_widget, {"message": custom_message})
        content = result.root.structuredContent

        assert content["message"] == custom_message

    @pytest.mark.asyncio
    async def test_custom_accent_color_passes_through(self, mock_widget):
        """handle_card uses provided accentColor."""
        result = await handle_card(mock_widget, {"accentColor": "#ff5500"})
        content = result.root.structuredContent

        assert content["accentColor"] == "#ff5500"

    @pytest.mark.asyncio
    async def test_returns_text_content(self, mock_widget):
        """handle_card returns text content."""
        result = await handle_card(mock_widget, {})

        assert len(result.root.content) >= 1
        assert result.root.content[0].text is not None

    @pytest.mark.asyncio
    async def test_handles_empty_arguments(self, mock_widget):
        """handle_card works with empty arguments (uses defaults)."""
        result = await handle_card(mock_widget, {})

        assert result.root.structuredContent is not None
        assert result.root.isError is not True


class TestHandleCarousel:
    """Tests for handle_carousel handler structure."""

    @pytest.mark.asyncio
    async def test_returns_structured_content_with_required_keys(self, mock_widget):
        """handle_carousel returns structuredContent with required keys."""
        result = await handle_carousel(mock_widget, {})
        content = result.root.structuredContent

        assert content is not None
        assert "title" in content
        assert "items" in content

    @pytest.mark.asyncio
    async def test_items_is_a_list(self, mock_widget):
        """handle_carousel returns items as a list."""
        result = await handle_carousel(mock_widget, {})
        items = result.root.structuredContent["items"]

        assert isinstance(items, list)

    @pytest.mark.asyncio
    async def test_custom_title_passes_through(self, mock_widget):
        """handle_carousel uses provided title."""
        custom_title = "My Recommendations"
        result = await handle_carousel(mock_widget, {"title": custom_title})
        content = result.root.structuredContent

        assert content["title"] == custom_title

    @pytest.mark.asyncio
    async def test_handles_empty_arguments(self, mock_widget):
        """handle_carousel works with empty arguments."""
        result = await handle_carousel(mock_widget, {})

        assert result.root.structuredContent is not None
        assert result.root.isError is not True


class TestHandleList:
    """Tests for handle_list handler structure."""

    @pytest.mark.asyncio
    async def test_returns_structured_content_with_required_keys(self, mock_widget):
        """handle_list returns structuredContent with required keys."""
        result = await handle_list(mock_widget, {})
        content = result.root.structuredContent

        assert content is not None
        assert "title" in content
        assert "subtitle" in content
        assert "items" in content

    @pytest.mark.asyncio
    async def test_items_is_a_list(self, mock_widget):
        """handle_list returns items as a list."""
        result = await handle_list(mock_widget, {})
        items = result.root.structuredContent["items"]

        assert isinstance(items, list)

    @pytest.mark.asyncio
    async def test_custom_title_passes_through(self, mock_widget):
        """handle_list uses provided title."""
        custom_title = "My Top Picks"
        result = await handle_list(mock_widget, {"title": custom_title})
        content = result.root.structuredContent

        assert content["title"] == custom_title

    @pytest.mark.asyncio
    async def test_custom_subtitle_passes_through(self, mock_widget):
        """handle_list uses provided subtitle."""
        custom_subtitle = "Hand-picked for you"
        result = await handle_list(mock_widget, {"subtitle": custom_subtitle})
        content = result.root.structuredContent

        assert content["subtitle"] == custom_subtitle

    @pytest.mark.asyncio
    async def test_handles_empty_arguments(self, mock_widget):
        """handle_list works with empty arguments."""
        result = await handle_list(mock_widget, {})

        assert result.root.structuredContent is not None
        assert result.root.isError is not True


class TestHandleGallery:
    """Tests for handle_gallery handler structure."""

    @pytest.mark.asyncio
    async def test_returns_structured_content_with_required_keys(self, mock_widget):
        """handle_gallery returns structuredContent with required keys."""
        result = await handle_gallery(mock_widget, {})
        content = result.root.structuredContent

        assert content is not None
        assert "title" in content
        assert "images" in content

    @pytest.mark.asyncio
    async def test_images_is_a_list(self, mock_widget):
        """handle_gallery returns images as a list."""
        result = await handle_gallery(mock_widget, {})
        images = result.root.structuredContent["images"]

        assert isinstance(images, list)

    @pytest.mark.asyncio
    async def test_custom_title_passes_through(self, mock_widget):
        """handle_gallery uses provided title."""
        custom_title = "Vacation Photos"
        result = await handle_gallery(mock_widget, {"title": custom_title})
        content = result.root.structuredContent

        assert content["title"] == custom_title

    @pytest.mark.asyncio
    async def test_handles_empty_arguments(self, mock_widget):
        """handle_gallery works with empty arguments."""
        result = await handle_gallery(mock_widget, {})

        assert result.root.structuredContent is not None
        assert result.root.isError is not True


class TestHandleDashboard:
    """Tests for handle_dashboard handler structure."""

    @pytest.mark.asyncio
    async def test_returns_structured_content_with_required_keys(self, mock_widget):
        """handle_dashboard returns structuredContent with required keys."""
        result = await handle_dashboard(mock_widget, {})
        content = result.root.structuredContent

        assert content is not None
        assert "title" in content
        assert "period" in content
        assert "stats" in content
        assert "activities" in content

    @pytest.mark.asyncio
    async def test_stats_is_a_list(self, mock_widget):
        """handle_dashboard returns stats as a list."""
        result = await handle_dashboard(mock_widget, {})
        stats = result.root.structuredContent["stats"]

        assert isinstance(stats, list)

    @pytest.mark.asyncio
    async def test_activities_is_a_list(self, mock_widget):
        """handle_dashboard returns activities as a list."""
        result = await handle_dashboard(mock_widget, {})
        activities = result.root.structuredContent["activities"]

        assert isinstance(activities, list)

    @pytest.mark.asyncio
    async def test_custom_title_passes_through(self, mock_widget):
        """handle_dashboard uses provided title."""
        custom_title = "Sales Dashboard"
        result = await handle_dashboard(mock_widget, {"title": custom_title})
        content = result.root.structuredContent

        assert content["title"] == custom_title

    @pytest.mark.asyncio
    async def test_custom_period_passes_through(self, mock_widget):
        """handle_dashboard uses provided period."""
        custom_period = "Last 7 days"
        result = await handle_dashboard(mock_widget, {"period": custom_period})
        content = result.root.structuredContent

        assert content["period"] == custom_period

    @pytest.mark.asyncio
    async def test_handles_empty_arguments(self, mock_widget):
        """handle_dashboard works with empty arguments."""
        result = await handle_dashboard(mock_widget, {})

        assert result.root.structuredContent is not None
        assert result.root.isError is not True


class TestHandleSolarSystem:
    """Tests for handle_solar_system handler structure."""

    @pytest.mark.asyncio
    async def test_returns_structured_content_with_required_keys(self, mock_widget):
        """handle_solar_system returns structuredContent with required keys."""
        result = await handle_solar_system(mock_widget, {})
        content = result.root.structuredContent

        assert content is not None
        assert "title" in content
        assert "planet_name" in content

    @pytest.mark.asyncio
    async def test_custom_title_passes_through(self, mock_widget):
        """handle_solar_system uses provided title."""
        custom_title = "Mars Explorer"
        result = await handle_solar_system(mock_widget, {"title": custom_title})
        content = result.root.structuredContent

        assert content["title"] == custom_title

    @pytest.mark.asyncio
    async def test_planet_name_passes_through(self, mock_widget):
        """handle_solar_system uses provided planet_name."""
        result = await handle_solar_system(mock_widget, {"planet_name": "Jupiter"})
        content = result.root.structuredContent

        assert content["planet_name"] == "Jupiter"

    @pytest.mark.asyncio
    async def test_default_planet_is_none(self, mock_widget):
        """handle_solar_system defaults planet_name to None."""
        result = await handle_solar_system(mock_widget, {})
        content = result.root.structuredContent

        assert content["planet_name"] is None

    @pytest.mark.asyncio
    async def test_handles_empty_arguments(self, mock_widget):
        """handle_solar_system works with empty arguments."""
        result = await handle_solar_system(mock_widget, {})

        assert result.root.structuredContent is not None
        assert result.root.isError is not True


class TestHandleTodo:
    """Tests for handle_todo handler structure."""

    @pytest.mark.asyncio
    async def test_returns_structured_content_with_required_keys(self, mock_widget):
        """handle_todo returns structuredContent with required keys."""
        result = await handle_todo(mock_widget, {})
        content = result.root.structuredContent

        assert content is not None
        assert "lists" in content

    @pytest.mark.asyncio
    async def test_lists_is_a_list(self, mock_widget):
        """handle_todo returns lists as a list."""
        result = await handle_todo(mock_widget, {})
        lists = result.root.structuredContent["lists"]

        assert isinstance(lists, list)

    @pytest.mark.asyncio
    async def test_handles_empty_arguments(self, mock_widget):
        """handle_todo works with empty arguments."""
        result = await handle_todo(mock_widget, {})

        assert result.root.structuredContent is not None
        assert result.root.isError is not True


class TestHandleShop:
    """Tests for handle_shop handler structure."""

    @pytest.mark.asyncio
    async def test_returns_structured_content_with_required_keys(self, mock_widget):
        """handle_shop returns structuredContent with required keys."""
        result = await handle_shop(mock_widget, {})
        content = result.root.structuredContent

        assert content is not None
        assert "title" in content
        assert "cartItems" in content

    @pytest.mark.asyncio
    async def test_cart_items_is_a_list(self, mock_widget):
        """handle_shop returns cartItems as a list."""
        result = await handle_shop(mock_widget, {})
        items = result.root.structuredContent["cartItems"]

        assert isinstance(items, list)

    @pytest.mark.asyncio
    async def test_custom_title_passes_through(self, mock_widget):
        """handle_shop uses provided title."""
        custom_title = "Shopping Cart"
        result = await handle_shop(mock_widget, {"title": custom_title})
        content = result.root.structuredContent

        assert content["title"] == custom_title

    @pytest.mark.asyncio
    async def test_handles_empty_arguments(self, mock_widget):
        """handle_shop works with empty arguments."""
        result = await handle_shop(mock_widget, {})

        assert result.root.structuredContent is not None
        assert result.root.isError is not True
