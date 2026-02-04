#!/bin/bash

# MCP App Template - Setup Script
# This script sets up the repository for the first time
#
# Usage:
#   ./setup.sh              Full development setup (default)
#   ./setup.sh --minimal    Minimal setup to serve the app (skips Playwright & tests)

set -e  # Exit on any error

# Parse arguments
MODE="full"
for arg in "$@"; do
    case $arg in
        --minimal)
            MODE="minimal"
            shift
            ;;
        --help|-h)
            echo "Usage: ./setup.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  (no flag)     Full development setup including Playwright and tests"
            echo "  --minimal     Minimal setup to serve the app (skips Playwright & tests)"
            echo "  --help, -h    Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $arg"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo_step() {
    echo -e "\n${GREEN}==>${NC} $1"
}

echo_warn() {
    echo -e "${YELLOW}Warning:${NC} $1"
}

echo_error() {
    echo -e "${RED}Error:${NC} $1"
}

# Check for required commands
check_command() {
    if ! command -v "$1" &> /dev/null; then
        echo_error "$1 is required but not installed."
        return 1
    fi
}

echo_step "Checking prerequisites..."
echo "  Mode: $MODE"

# Check for pnpm
if ! check_command pnpm; then
    echo "Please install pnpm: https://pnpm.io/installation"
    exit 1
fi

# Check for Python 3.12+
if ! check_command python3; then
    echo "Please install Python 3.12 or later"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 12 ]); then
    echo_error "Python 3.12 or later is required. Found: Python $PYTHON_VERSION"
    exit 1
fi

echo "  pnpm: $(pnpm --version)"
echo "  python: $PYTHON_VERSION"

# Install Node.js dependencies
echo_step "Installing Node.js dependencies..."
pnpm install

# Set up Python virtual environment
echo_step "Setting up Python virtual environment..."
cd server

if [ -d ".venv" ]; then
    echo "  Virtual environment already exists, skipping creation"
else
    # Try uv first (faster and doesn't require python3-venv package)
    if command -v uv &> /dev/null; then
        echo "  Using uv to create virtual environment"
        uv venv .venv
        echo "  Created virtual environment with uv"
    else
        # Fall back to python3 -m venv
        if python3 -m venv .venv 2>/dev/null; then
            echo "  Created virtual environment"
        else
            echo_error "Failed to create virtual environment."
            echo ""
            echo "This usually means python3-venv is not installed. Fix options:"
            echo ""
            echo "  Option 1 (recommended): Install uv (fast Python package manager)"
            echo "    curl -LsSf https://astral.sh/uv/install.sh | sh"
            echo ""
            echo "  Option 2: Install python3-venv"
            echo "    Ubuntu/Debian: sudo apt install python3-venv"
            echo "    Fedora: sudo dnf install python3-venv"
            echo "    macOS: brew install python3 (includes venv)"
            echo ""
            echo "After installing, run ./setup.sh again."
            exit 1
        fi
    fi
fi

# Activate venv and install dependencies
echo_step "Installing Python dependencies..."

# Check if uv is available (faster), otherwise use pip
if command -v uv &> /dev/null; then
    echo "  Using uv for package installation"
    uv pip install -e ".[dev]" --python .venv/bin/python
else
    echo "  Using pip for package installation"
    .venv/bin/pip install --upgrade pip
    .venv/bin/pip install -e ".[dev]"
fi

cd ..

# Install Playwright for UI testing (skip in minimal mode)
if [ "$MODE" != "minimal" ]; then
    echo_step "Installing Playwright browser (Chromium)..."
    pnpm run setup:test
else
    echo_step "Skipping Playwright installation (minimal mode)"
fi

# Build the widgets
echo_step "Building widgets..."
pnpm run build

# Run tests (skip in minimal mode)
if [ "$MODE" != "minimal" ]; then
    echo_step "Running tests..."
    pnpm run test
else
    echo_step "Skipping tests (minimal mode)"
fi

echo -e "\n${GREEN}✓ Setup complete!${NC}"
echo ""

if [ "$MODE" = "minimal" ]; then
    echo "Next steps:"
    echo "  • Start the server:    pnpm run server"
    echo "  • Open the app tester: http://localhost:8000/assets/apptester.html"
    echo ""
    echo "To enable testing later, run:"
    echo "  • pnpm run setup:test           # Install Playwright browsers"
    echo "  • npx playwright install-deps   # Install system deps (may need sudo)"
    echo "  • pnpm run test                 # Run all tests"
else
    echo "Next steps:"
    echo "  • Start the server:    pnpm run server"
    echo "  • Open the app tester: http://localhost:8000/assets/apptester.html"
    echo "  • Test a widget:       pnpm run ui-test --tool show_<name>"
fi
echo ""
