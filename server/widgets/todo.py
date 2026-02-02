"""Todo widget."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict

import mcp.types as types
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from ._base import Widget, format_validation_error, get_invocation_meta

WIDGET = Widget(
    identifier="show_todo",
    title="Show Todo List",
    description="""Display an interactive todo list manager with multiple lists.

Use this tool when:
- The user wants to organize tasks or create a todo list
- Managing multiple lists (work, personal, shopping)
- Tracking task completion and due dates

Args:
    title: Main title text (default: "My Tasks")

Returns:
    Todo manager interface with:
    - Multiple collapsible lists
    - Drag-and-drop reordering
    - Task completion checkboxes
    - Due date display
    - Add/edit/delete functionality

Example:
    show_todo(title="Today's Tasks")""",
    template_uri="ui://widget/todo.html",
    invoking="Loading todo list...",
    invoked="Todo list ready",
    component_name="todo",
)


class TodoInput(BaseModel):
    """Input for todo widget."""
    title: str = Field(default="My Tasks", description="Main title")
    model_config = ConfigDict(populate_by_name=True, extra="forbid")


INPUT_MODEL = TodoInput

SAMPLE_TODO_LISTS = [
    {
        "id": "work",
        "title": "Work Tasks",
        "isCurrentlyOpen": True,
        "todos": [
            {"id": "1", "title": "Review pull requests", "isComplete": False, "note": "Check the new feature branch"},
            {"id": "2", "title": "Update documentation", "isComplete": True},
            {"id": "3", "title": "Team standup meeting", "isComplete": False, "dueDate": "2025-01-15"},
        ],
    },
    {
        "id": "personal",
        "title": "Personal",
        "todos": [
            {"id": "4", "title": "Buy groceries", "isComplete": False},
            {"id": "5", "title": "Call mom", "isComplete": False, "dueDate": "2025-01-14"},
        ],
    },
    {
        "id": "shopping",
        "title": "Shopping List",
        "todos": [
            {"id": "6", "title": "Milk", "isComplete": False},
            {"id": "7", "title": "Bread", "isComplete": True},
            {"id": "8", "title": "Eggs", "isComplete": False},
        ],
    },
]


async def handle(widget: Widget, arguments: Dict[str, Any]) -> types.ServerResult:
    try:
        payload = TodoInput.model_validate(arguments)
    except ValidationError as e:
        error_msg = format_validation_error(e, TodoInput)
        return types.ServerResult(types.CallToolResult(
            content=[types.TextContent(type="text", text=error_msg)],
            isError=True,
        ))

    structured_content = {
        "lists": deepcopy(SAMPLE_TODO_LISTS),
    }

    total_todos = sum(len(lst["todos"]) for lst in SAMPLE_TODO_LISTS)
    return types.ServerResult(types.CallToolResult(
        content=[types.TextContent(type="text", text=f"Todo: {len(SAMPLE_TODO_LISTS)} lists, {total_todos} items")],
        structuredContent=structured_content,
        _meta=get_invocation_meta(widget),
    ))
