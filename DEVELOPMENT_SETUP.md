# P2PP Development Setup

Simple, working development environment for P2PP.

## Quick Start

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create and activate virtual environment
uv venv
source .venv/bin/activate

# Install development dependencies
uv sync --extra dev --no-build

# Run tests
python3 scripts/dev.py test-unit

# Check architecture
python3 scripts/dev.py check-arch
```

## Development Commands

Use the development script for common tasks:

```bash
# Show all available commands
python3 scripts/dev.py

# Run unit tests
python3 scripts/dev.py test-unit

# Check code formatting
python3 scripts/dev.py check-format

# Format code
python3 scripts/dev.py format

# Sort imports
python3 scripts/dev.py sort-imports

# Check system architecture
python3 scripts/dev.py check-arch

# Run all checks
python3 scripts/dev.py all
```

## What Works

- **Virtual Environment**: `uv venv` and `source .venv/bin/activate`
- **Dependency Management**: `uv sync --extra dev --no-build`
- **Testing**: `pytest` with 18 passing unit tests
- **Code Formatting**: `black` for code formatting
- **Import Sorting**: `isort` for import organization
- **Architecture Detection**: `scripts/check_architecture.py`
- **Version Information**: `version.py` module
- **Development Script**: `scripts/dev.py` for common tasks

## Project Structure

```
P2PP/
├── .venv/                    # Virtual environment
├── pyproject.toml           # Tool configuration
├── scripts/
│   ├── dev.py              # Development script
│   └── check_architecture.py # Architecture detection
├── tests/
│   ├── conftest.py         # Test configuration
│   └── unit/
│       └── test_version.py # Unit tests
└── version.py              # Version information
```

## Dependencies

- **Python 3.9+**: Required for the project
- **uv**: Modern Python package manager
- **pytest**: Testing framework
- **black**: Code formatter
- **isort**: Import sorter
- **setuptools**: For existing build system

## Build System

The existing `setup.py` is kept for actual building:

```bash
# Check setup.py works
python3 setup.py --help-commands

# The build system supports architecture-specific builds
python3 setup.py py2app --arch=x86_64  # Intel
python3 setup.py py2app --arch=arm64   # ARM
```

## Architecture Support

The project supports architecture-specific builds:

- **macOS**: Separate Intel and ARM builds (no Universal2)
- **Windows**: Single MSI installer
- **Linux**: RPM and DEB packages

Use `python3 scripts/dev.py check-arch` to see what build you should download.

## Notes

- Python 3.13 is newer than the cx_Freeze version supports
- The project uses PyQt5 which doesn't work with Universal2 builds
- Virtual environment is required for development dependencies
- All tests should pass before making changes