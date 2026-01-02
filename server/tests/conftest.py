"""
Shared fixtures for server tests.

These fixtures provide test infrastructure that is independent of
the specific business logic in the template.
"""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Add server directory to path for imports
SERVER_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SERVER_DIR))


@pytest.fixture
def mock_widget_html():
    """Mock widget HTML content for testing without built assets."""
    return "<html><body>Mock Widget</body></html>"


@pytest.fixture
def mock_load_widget_html(mock_widget_html):
    """Patch load_widget_html to return mock HTML."""
    with patch("main.load_widget_html", return_value=mock_widget_html):
        yield mock_widget_html
