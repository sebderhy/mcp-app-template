"""Shop widget."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict

import mcp.types as types
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from ._base import Widget, format_validation_error, get_invocation_meta

WIDGET = Widget(
    identifier="show_shop",
    title="Show Shopping Cart",
    description="""Display a shopping cart with products and checkout flow.

Use this tool when:
- The user wants to manage a shopping cart
- E-commerce checkout experiences
- Product quantity and price management

Args:
    title: Cart header text (default: "Your Cart")

Returns:
    Shopping cart interface with:
    - Product list with images and descriptions
    - Quantity controls (+/-)
    - Price calculations
    - Product tags (vegan, spicy, etc.)
    - Checkout button

Example:
    show_shop(title="Your Shopping Cart")""",
    template_uri="ui://widget/shop.html",
    invoking="Loading shopping cart...",
    invoked="Shopping cart ready",
    component_name="shop",
)


class ShopInput(BaseModel):
    """Input for shop widget."""
    title: str = Field(default="Your Cart", description="Cart title")
    model_config = ConfigDict(populate_by_name=True, extra="forbid")


INPUT_MODEL = ShopInput

SAMPLE_CART_ITEMS = [
    {
        "id": "marys-chicken",
        "name": "Mary's Chicken",
        "price": 19.48,
        "description": "Tender organic chicken breasts trimmed for easy cooking.",
        "shortDescription": "Organic chicken breasts",
        "detailSummary": "4 lbs - $3.99/lb",
        "quantity": 2,
        "image": "https://persistent.oaistatic.com/pizzaz-cart-xl/chicken.png",
        "tags": ["size"],
    },
    {
        "id": "avocados",
        "name": "Avocados",
        "price": 1.00,
        "description": "Creamy Hass avocados picked at peak ripeness.",
        "shortDescription": "Creamy Hass avocados",
        "quantity": 2,
        "image": "https://persistent.oaistatic.com/pizzaz-cart-xl/avocado.png",
        "tags": ["vegan"],
    },
    {
        "id": "hojicha-pizza",
        "name": "Hojicha Pizza",
        "price": 15.50,
        "description": "Wood-fired crust with smoky hojicha tea sauce and honey.",
        "shortDescription": "Smoky hojicha sauce & honey",
        "quantity": 1,
        "image": "https://persistent.oaistatic.com/pizzaz-cart-xl/hojicha-pizza.png",
        "tags": ["vegetarian", "spicy"],
    },
    {
        "id": "chicken-pizza",
        "name": "Chicken Pizza",
        "price": 7.00,
        "description": "Classic thin-crust pizza with roasted chicken and herb pesto.",
        "shortDescription": "Roasted chicken & pesto",
        "quantity": 1,
        "image": "https://persistent.oaistatic.com/pizzaz-cart-xl/chicken-pizza.png",
        "tags": [],
    },
    {
        "id": "matcha-pizza",
        "name": "Matcha Pizza",
        "price": 5.00,
        "description": "Crisp dough with velvety matcha cream and mascarpone.",
        "shortDescription": "Velvety matcha cream",
        "quantity": 1,
        "image": "https://persistent.oaistatic.com/pizzaz-cart-xl/matcha-pizza.png",
        "tags": ["vegetarian"],
    },
]


async def handle(widget: Widget, arguments: Dict[str, Any]) -> types.ServerResult:
    try:
        payload = ShopInput.model_validate(arguments)
    except ValidationError as e:
        error_msg = format_validation_error(e, ShopInput)
        return types.ServerResult(types.CallToolResult(
            content=[types.TextContent(type="text", text=error_msg)],
            isError=True,
        ))

    structured_content = {
        "title": payload.title,
        "cartItems": deepcopy(SAMPLE_CART_ITEMS),
    }

    total_items = sum(item["quantity"] for item in SAMPLE_CART_ITEMS)
    return types.ServerResult(types.CallToolResult(
        content=[types.TextContent(type="text", text=f"Shopping Cart: {total_items} items")],
        structuredContent=structured_content,
        _meta=get_invocation_meta(widget),
    ))
