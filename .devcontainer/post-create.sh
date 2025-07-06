#!/bin/bash

# P2PP Development Container Setup
set -e

echo "Setting up P2PP development environment..."
cd /workspace

# Start virtual display for GUI testing
echo "Starting virtual display for headless GUI testing..."
/usr/local/bin/start-xvfb

# Install uv if not available
if ! command -v uv &> /dev/null; then
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi

echo "uv version: $(uv --version)"

# Setup development environment
echo "Installing development dependencies..."
uv run setup

# Create necessary directories
echo "Creating directories..."
mkdir -p htmlcov .pytest_cache build dist

# Set up Git if needed
if [ ! -f ~/.gitconfig ]; then
    echo "Setting up Git configuration..."
    git config --global user.name "Dev Container User"
    git config --global user.email "dev@example.com"
    git config --global init.defaultBranch main
    git config --global pull.rebase false
fi

# Run quick test
echo "Running quick test..."
if uv run quick; then
    echo "Unit tests passed - environment ready"
else
    echo "Some tests failed, but environment is set up"
fi

# Check architecture
echo "System architecture:"
uv run check-arch

echo ""
echo "P2PP Development Environment Ready"
echo ""
echo "Quick commands:"
echo "  uv run test        # All tests"
echo "  uv run test-unit   # Unit tests"
echo "  uv run fix         # Fix formatting"
echo "  uv run build       # Build for platform"
echo ""
echo "See DEVELOPMENT.md for documentation"