"""System monitor widget."""

from __future__ import annotations

import platform
import socket
import time
from typing import Any, Dict

import mcp.types as types
import psutil
from pydantic import BaseModel, ConfigDict, ValidationError

from ._base import Widget, format_validation_error, get_invocation_meta

WIDGET = Widget(
    identifier="get_system_info",
    title="System Monitor",
    description="""Display real-time system monitoring with CPU and memory usage charts.

Use this tool when:
- The user asks about system performance or resource usage
- Monitoring CPU load or memory consumption
- Viewing system information (hostname, platform, uptime)

Args:
    (No parameters required - automatically detects system info)

Returns:
    Interactive widget with:
    - Per-core CPU usage chart (updates every 2 seconds)
    - Memory usage bar with percentage
    - System info (hostname, platform, uptime)

Example:
    get_system_info()""",
    template_uri="ui://widget/system-monitor.html",
    invoking="Loading system monitor...",
    invoked="System monitor ready",
    component_name="system-monitor",
)


class SystemInfoInput(BaseModel):
    """Input for system monitor widget (no parameters needed)."""
    model_config = ConfigDict(extra="forbid")


INPUT_MODEL = SystemInfoInput


async def handle(widget: Widget, arguments: Dict[str, Any]) -> types.ServerResult:
    try:
        SystemInfoInput.model_validate(arguments)
    except ValidationError as e:
        error_msg = format_validation_error(e, SystemInfoInput)
        return types.ServerResult(types.CallToolResult(
            content=[types.TextContent(type="text", text=error_msg)],
            isError=True,
        ))

    info = {
        "hostname": socket.gethostname(),
        "platform": f"{platform.system()} {platform.machine()}",
        "cpu": {
            "model": platform.processor() or "Unknown",
            "count": psutil.cpu_count() or 1,
        },
        "memory": {
            "totalBytes": psutil.virtual_memory().total,
        },
    }

    return types.ServerResult(types.CallToolResult(
        content=[types.TextContent(type="text", text=f"System: {info['hostname']} ({info['platform']})")],
        structuredContent=info,
        _meta=get_invocation_meta(widget),
    ))


async def handle_poll_system_stats(arguments: Dict[str, Any]) -> types.ServerResult:
    """App-only handler: returns live CPU and memory stats for polling."""
    cpu_percents = psutil.cpu_percent(percpu=True)
    mem = psutil.virtual_memory()

    stats = {
        "cpuPercents": cpu_percents,
        "memoryPercent": mem.percent,
        "memoryUsedGB": round(mem.used / (1024 ** 3), 2),
        "memoryTotalGB": round(mem.total / (1024 ** 3), 2),
        "uptime": int(time.time() - psutil.boot_time()),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    return types.ServerResult(types.CallToolResult(
        content=[types.TextContent(type="text", text=f"CPU: {cpu_percents}, Memory: {mem.percent}%")],
        structuredContent=stats,
    ))


DATA_ONLY_TOOLS = {
    "poll_system_stats": handle_poll_system_stats,
}

DATA_ONLY_TOOL_DEFS = [
    {
        "name": "poll_system_stats",
        "title": "Poll System Stats",
        "description": "Returns live CPU and memory stats. Called by the system monitor widget for polling — not intended for direct LLM use.",
        "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
    },
]
