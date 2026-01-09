"""
Agent Runner for Local ChatGPT Simulator

Uses OpenAI Agents SDK with MCP to connect prompts to widget tools.
https://openai.github.io/openai-agents-python/mcp/
"""

from __future__ import annotations

# Load .env file before anything else
import os
from pathlib import Path
from dotenv import load_dotenv

# Look for .env in server/ or parent directory
env_path = Path(__file__).parent / ".env"
if not env_path.exists():
    env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

import asyncio
import json
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from agents import Agent, Runner
from agents.mcp import MCPServerStreamableHttp
from agents.model_settings import ModelSettings


# =============================================================================
# CONFIGURATION
# =============================================================================

# Model to use - can be overridden via OPENAI_MODEL env var
DEFAULT_MODEL = "gpt-4o-mini"
MODEL = os.getenv("OPENAI_MODEL", DEFAULT_MODEL)

# MCP Server URL (the existing server)
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8000/mcp")


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class WidgetResult:
    """Result containing widget data for rendering."""
    tool_name: str
    html: str
    tool_output: Dict[str, Any]
    text_summary: str


@dataclass
class AgentResponse:
    """Response from the agent including message and optional widget."""
    message: str
    widget: Optional[WidgetResult] = None


# =============================================================================
# WIDGET DATA (imported from main.py at runtime)
# =============================================================================

def get_widget_html(tool_name: str) -> str:
    """Get the HTML for a widget by tool name."""
    try:
        from main import WIDGETS_BY_ID
        widget = WIDGETS_BY_ID.get(tool_name)
        if widget:
            return widget.html
    except ImportError:
        pass
    return ""


# =============================================================================
# MCP SERVER & AGENT
# =============================================================================

async def create_mcp_server() -> MCPServerStreamableHttp:
    """Create MCP server connection."""
    return MCPServerStreamableHttp(
        name="chatgpt-widgets",
        params={
            "url": MCP_SERVER_URL,
        },
        cache_tools_list=True,  # Cache tools for better performance
    )


def create_agent(mcp_server: MCPServerStreamableHttp) -> Agent:
    """Create an agent connected to the MCP server."""
    return Agent(
        name="Widget Assistant",
        model=MODEL,
        instructions="""You are a helpful assistant that can display interactive widgets.

When the user asks to see something visual, use the appropriate tool:
- show_card: For simple interactive card displays
- show_carousel: For horizontal scrolling cards (places, products, recommendations)
- show_list: For vertical lists with thumbnails (rankings, search results)
- show_gallery: For image galleries with lightbox
- show_dashboard: For stats and metrics displays
- show_solar_system: For interactive 3D solar system
- show_todo: For task/todo list management
- show_shop: For shopping cart and e-commerce

Always use a tool when the user asks to see, show, or display something visual.
After calling a tool, provide a brief helpful response about what you're showing.""",
        mcp_servers=[mcp_server],
        model_settings=ModelSettings(tool_choice="auto"),
    )


# =============================================================================
# CONVERSATION MANAGER
# =============================================================================

class ConversationManager:
    """Manages conversation history for context."""

    def __init__(self):
        self.conversations: Dict[str, List[Dict[str, str]]] = {}

    def get_history(self, conversation_id: str) -> List[Dict[str, str]]:
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = []
        return self.conversations[conversation_id]

    def add_message(self, conversation_id: str, role: str, content: str):
        history = self.get_history(conversation_id)
        history.append({"role": role, "content": content})
        # Keep last 20 messages to avoid token limits
        if len(history) > 20:
            self.conversations[conversation_id] = history[-20:]

    def clear(self, conversation_id: str):
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]


# Global conversation manager
conversation_manager = ConversationManager()


# =============================================================================
# AGENT RUNNER
# =============================================================================

async def run_agent(
    prompt: str,
    conversation_id: str = "default",
) -> AgentResponse:
    """
    Run the agent with a user prompt.

    Args:
        prompt: User's message
        conversation_id: ID for conversation context

    Returns:
        AgentResponse with message and optional widget
    """
    mcp_server = await create_mcp_server()
    agent = create_agent(mcp_server)

    async with mcp_server:
        # Run the agent
        result = await Runner.run(agent, prompt)

        # Extract the final output
        final_message = result.final_output or ""

        # Extract widget data from tool calls
        widget_result = None

        # Debug: print all items to understand structure
        for item in result.new_items:
            # Check for MCP tool call items
            item_type = type(item).__name__

            # Look for tool calls and their outputs
            if hasattr(item, 'raw_item'):
                raw = item.raw_item
                raw_type = getattr(raw, 'type', None)

                # Function call (tool invocation)
                if raw_type == 'function_call':
                    tool_name = getattr(raw, 'name', '')
                    tool_args_str = getattr(raw, 'arguments', '{}')
                    try:
                        tool_args = json.loads(tool_args_str) if tool_args_str else {}
                    except json.JSONDecodeError:
                        tool_args = {}

                    # Get widget HTML
                    html = get_widget_html(tool_name)
                    if html:
                        widget_result = WidgetResult(
                            tool_name=tool_name,
                            html=html,
                            tool_output=tool_args,
                            text_summary=f"Displaying {tool_name}"
                        )

                # Function call output (tool result)
                elif raw_type == 'function_call_output':
                    output = getattr(raw, 'output', '')
                    # Try to parse the output as JSON to get structured content
                    if output and widget_result:
                        try:
                            parsed = json.loads(output)
                            # MCP returns structuredContent in the response
                            if isinstance(parsed, dict):
                                # The output might contain the structured content directly
                                widget_result.tool_output = parsed
                        except (json.JSONDecodeError, TypeError):
                            pass

        # Update conversation history
        conversation_manager.add_message(conversation_id, "user", prompt)
        conversation_manager.add_message(conversation_id, "assistant", final_message)

        return AgentResponse(
            message=final_message,
            widget=widget_result
        )


def clear_conversation(conversation_id: str = "default"):
    """Clear conversation history."""
    conversation_manager.clear(conversation_id)


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    async def test():
        print("=" * 60)
        print("Testing Agent Runner")
        print("=" * 60)
        print(f"Model: {MODEL}")
        print(f"MCP Server: {MCP_SERVER_URL}")

        if not os.getenv("OPENAI_API_KEY"):
            print("\nERROR: Set OPENAI_API_KEY in .env file")
            return

        print("\nRunning test prompt: 'Show me a carousel of restaurants'")
        print("-" * 60)

        try:
            result = await run_agent("Show me a carousel of restaurants")
            print(f"\nAgent response: {result.message}")
            if result.widget:
                print(f"\nWidget loaded: {result.widget.tool_name}")
                print(f"Tool output keys: {list(result.widget.tool_output.keys())}")
            else:
                print("\nNo widget in response")
        except Exception as e:
            import traceback
            print(f"Error: {e}")
            traceback.print_exc()
            print("\nMake sure the MCP server is running: pnpm run server")

    asyncio.run(test())
