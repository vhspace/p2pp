#!/bin/bash

# P2PP Development Container Post-Create Setup Script
# This script sets up the complete development environment using uv

set -e

echo "🚀 Setting up P2PP development environment..."

# Ensure we're in the workspace directory
cd /workspace

# Start virtual display for GUI testing
echo "🖥️  Starting virtual display for headless GUI testing..."
/usr/local/bin/start-xvfb

# Install uv if not already available
if ! command -v uv &> /dev/null; then
    echo "📦 Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi

# Verify uv installation
echo "📋 uv version: $(uv --version)"

# Sync development dependencies
echo "📦 Installing development dependencies with uv..."
uv sync --dev --extra test-linux

# Run development setup
echo "🔧 Running development setup..."
uv run dev-setup || echo "ℹ️  Pre-commit hooks setup skipped (optional)"

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p htmlcov
mkdir -p .pytest_cache
mkdir -p build
mkdir -p dist

# Set up Git configuration (if not already configured)
if [ ! -f ~/.gitconfig ]; then
    echo "⚙️  Setting up basic Git configuration..."
    git config --global user.name "Dev Container User"
    git config --global user.email "dev@example.com"
    git config --global init.defaultBranch main
    git config --global pull.rebase false
fi

# Run a quick test to verify everything works
echo "🧪 Running quick test to verify setup..."
if uv run test-unit --tb=line -x -q; then
    echo "✅ Unit tests passed - environment is ready!"
else
    echo "⚠️  Some tests failed, but environment is set up. Check individual test files."
fi

# Check architecture
echo "🔍 Checking system architecture..."
uv run check-arch

# Display helpful information
echo ""
echo "🎉 P2PP Development Environment Ready!"
echo ""
echo "📚 Quick commands to get started:"
echo "  uv run test              # Run all tests"
echo "  uv run test-unit         # Run unit tests only"
echo "  uv run test-coverage     # Run tests with coverage"
echo "  uv run format            # Format code"
echo "  uv run lint              # Run linting"
echo "  uv run check-arch        # Check system architecture"
echo ""
echo "📖 See DEVELOPMENT.md for complete documentation"
echo ""
echo "🐛 Debugging GUI issues:"
echo "  export DISPLAY=:1        # Set display for GUI apps"
echo "  xvfb-run -a <command>    # Run command with virtual display"
echo ""
echo "Happy coding! 🐍✨"