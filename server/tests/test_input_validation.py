"""
Tests for Pydantic input model validation - Infrastructure tests.

These tests verify that the Pydantic validation INFRASTRUCTURE works correctly:
1. Models accept valid inputs
2. Models use defaults when inputs are missing
3. Models reject extra fields (when configured to do so)
4. Alias fields work correctly

Developers can modify the specific defaults and field names in their models.
These tests focus on validation behavior, not specific default values.
"""

import pytest
from pydantic import ValidationError

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from main import (
    CardInput,
    CarouselInput,
    ListInput,
    GalleryInput,
    DashboardInput,
    SolarSystemInput,
    TodoInput,
    ShopInput,
)


class TestPydanticValidationInfrastructure:
    """Tests that Pydantic validation infrastructure works correctly."""

    def test_card_input_accepts_valid_input(self):
        """CardInput accepts valid input without raising."""
        model = CardInput(title="Test", message="Hello", accentColor="#fff")
        assert model.title == "Test"

    def test_card_input_uses_defaults(self):
        """CardInput uses defaults when no input provided."""
        model = CardInput()
        assert model.title is not None
        assert model.message is not None
        assert model.accent_color is not None

    def test_card_input_rejects_extra_fields(self):
        """CardInput rejects unknown fields."""
        with pytest.raises(ValidationError):
            CardInput(title="Test", unknown_field="value")

    def test_card_input_alias_works(self):
        """CardInput accepts both accent_color and accentColor."""
        model1 = CardInput(accentColor="#123456")
        model2 = CardInput(accent_color="#654321")
        assert model1.accent_color == "#123456"
        assert model2.accent_color == "#654321"

    def test_carousel_input_accepts_valid_input(self):
        """CarouselInput accepts valid input."""
        model = CarouselInput(title="My Carousel", category="products")
        assert model.title == "My Carousel"
        assert model.category == "products"

    def test_carousel_input_uses_defaults(self):
        """CarouselInput uses defaults when no input provided."""
        model = CarouselInput()
        assert model.title is not None
        assert model.category is not None

    def test_carousel_input_rejects_extra_fields(self):
        """CarouselInput rejects unknown fields."""
        with pytest.raises(ValidationError):
            CarouselInput(extra="not_allowed")

    def test_list_input_accepts_valid_input(self):
        """ListInput accepts valid input."""
        model = ListInput(title="My List", subtitle="Description", category="items")
        assert model.title == "My List"
        assert model.subtitle == "Description"

    def test_list_input_uses_defaults(self):
        """ListInput uses defaults when no input provided."""
        model = ListInput()
        assert model.title is not None
        assert model.subtitle is not None
        assert model.category is not None

    def test_gallery_input_accepts_valid_input(self):
        """GalleryInput accepts valid input."""
        model = GalleryInput(title="My Gallery", category="photos")
        assert model.title == "My Gallery"

    def test_gallery_input_uses_defaults(self):
        """GalleryInput uses defaults when no input provided."""
        model = GalleryInput()
        assert model.title is not None
        assert model.category is not None

    def test_dashboard_input_accepts_valid_input(self):
        """DashboardInput accepts valid input."""
        model = DashboardInput(title="Analytics", period="Last week")
        assert model.title == "Analytics"
        assert model.period == "Last week"

    def test_dashboard_input_uses_defaults(self):
        """DashboardInput uses defaults when no input provided."""
        model = DashboardInput()
        assert model.title is not None
        assert model.period is not None

    def test_solar_system_input_accepts_valid_input(self):
        """SolarSystemInput accepts valid input."""
        model = SolarSystemInput(title="Planets", planet_name="Mars")
        assert model.title == "Planets"
        assert model.planet_name == "Mars"

    def test_solar_system_input_optional_planet(self):
        """SolarSystemInput planet_name is optional."""
        model = SolarSystemInput(title="Space")
        assert model.planet_name is None

    def test_solar_system_input_uses_defaults(self):
        """SolarSystemInput uses defaults when no input provided."""
        model = SolarSystemInput()
        assert model.title is not None
        # planet_name should default to None
        assert model.planet_name is None

    def test_todo_input_accepts_valid_input(self):
        """TodoInput accepts valid input."""
        model = TodoInput(title="My Tasks")
        assert model.title == "My Tasks"

    def test_todo_input_uses_defaults(self):
        """TodoInput uses defaults when no input provided."""
        model = TodoInput()
        assert model.title is not None

    def test_shop_input_accepts_valid_input(self):
        """ShopInput accepts valid input."""
        model = ShopInput(title="My Cart")
        assert model.title == "My Cart"

    def test_shop_input_uses_defaults(self):
        """ShopInput uses defaults when no input provided."""
        model = ShopInput()
        assert model.title is not None


class TestPydanticTypeCoercion:
    """Tests that Pydantic handles type coercion correctly."""

    def test_string_fields_accept_strings(self):
        """String fields accept string values."""
        model = CardInput(title="Test Title")
        assert isinstance(model.title, str)

    def test_optional_field_accepts_none(self):
        """Optional fields accept None."""
        model = SolarSystemInput(planet_name=None)
        assert model.planet_name is None


class TestModelConfig:
    """Tests that model configuration is correct."""

    def test_all_models_forbid_extra(self):
        """All input models should forbid extra fields."""
        models_to_test = [
            (CardInput, {"unknown": "value"}),
            (CarouselInput, {"unknown": "value"}),
            (ListInput, {"unknown": "value"}),
            (GalleryInput, {"unknown": "value"}),
            (DashboardInput, {"unknown": "value"}),
            (SolarSystemInput, {"unknown": "value"}),
            (TodoInput, {"unknown": "value"}),
            (ShopInput, {"unknown": "value"}),
        ]

        for model_class, invalid_data in models_to_test:
            with pytest.raises(ValidationError):
                model_class(**invalid_data)
