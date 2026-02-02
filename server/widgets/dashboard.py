"""Dashboard widget."""

from __future__ import annotations

from typing import Any, Dict

import mcp.types as types
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from ._base import Widget, format_validation_error, get_invocation_meta

WIDGET = Widget(
    identifier="show_dashboard",
    title="Show Dashboard",
    description="""Display a dashboard with stats, metrics, and activity feed.

Use this tool when:
- The user wants to see analytics or KPIs
- Showing account overview or status information
- Displaying numerical data with trends

Args:
    title: Dashboard header text (default: "Dashboard")
    period: Time period label (default: "Last 30 days")

Returns:
    Dashboard layout with:
    - Stat cards (value, change percentage, icon)
    - Activity feed (recent events with timestamps)
    - Period selector display

Example:
    show_dashboard(title="Sales Overview", period="This month")""",
    template_uri="ui://widget/dashboard.html",
    invoking="Loading dashboard...",
    invoked="Dashboard ready",
    component_name="dashboard",
)


class DashboardInput(BaseModel):
    """Input for dashboard widget."""
    title: str = Field(default="Dashboard", description="Dashboard title")
    period: str = Field(default="Last 30 days", description="Time period")
    model_config = ConfigDict(populate_by_name=True, extra="forbid")


INPUT_MODEL = DashboardInput

SAMPLE_DASHBOARD_STATS = [
    {"id": "revenue", "label": "Total Revenue", "value": "$45,231.89", "change": 20.1, "changeLabel": "from last month", "icon": "dollar"},
    {"id": "users", "label": "Active Users", "value": "2,350", "change": 15.3, "changeLabel": "from last month", "icon": "users"},
    {"id": "orders", "label": "Orders", "value": "1,247", "change": -5.2, "changeLabel": "from last month", "icon": "cart"},
    {"id": "views", "label": "Page Views", "value": "573,921", "change": 12.5, "changeLabel": "from last month", "icon": "eye"},
]

SAMPLE_ACTIVITIES = [
    {"id": "1", "title": "New user registered", "description": "john.doe@example.com signed up", "time": "2 min ago", "type": "success"},
    {"id": "2", "title": "Order completed", "description": "Order #12345 fulfilled", "time": "15 min ago", "type": "info"},
    {"id": "3", "title": "Payment failed", "description": "$99.00 declined", "time": "1 hour ago", "type": "error"},
    {"id": "4", "title": "Low stock alert", "description": "SKU-789 running low", "time": "3 hours ago", "type": "warning"},
]


async def handle(widget: Widget, arguments: Dict[str, Any]) -> types.ServerResult:
    try:
        payload = DashboardInput.model_validate(arguments)
    except ValidationError as e:
        error_msg = format_validation_error(e, DashboardInput)
        return types.ServerResult(types.CallToolResult(
            content=[types.TextContent(type="text", text=error_msg)],
            isError=True,
        ))

    structured_content = {
        "title": payload.title,
        "subtitle": "Your key metrics at a glance",
        "period": payload.period,
        "stats": SAMPLE_DASHBOARD_STATS,
        "activities": SAMPLE_ACTIVITIES,
    }

    return types.ServerResult(types.CallToolResult(
        content=[types.TextContent(type="text", text=f"Dashboard: {payload.title}")],
        structuredContent=structured_content,
        _meta=get_invocation_meta(widget),
    ))
