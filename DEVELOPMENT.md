# P2PP Development Guide

This guide covers how to develop P2PP using modern Python tooling with **uv** for fast package management and task running.

## Quick Start

1. **Install uv** (if not already installed):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Set up development environment**:
   ```bash
   uv sync --dev
   uv run dev-setup
   ```

3. **Run tests**:
   ```bash
   uv run test
   ```

4. **Check your architecture**:
   ```bash
   uv run check-arch
   ```

## Development Commands

All development tasks are managed through `uv run` commands defined in `pyproject.toml`:

### Testing
```bash
# Run all tests
uv run test

# Run specific test types
uv run test-unit           # Fast unit tests
uv run test-integration    # Integration tests
uv run test-e2e            # End-to-end tests

# Run tests with coverage
uv run test-coverage

# Quick test (unit tests only, exit on first failure)
uv run test-quick

# Platform-specific tests
uv run test-macos          # macOS only
uv run test-windows        # Windows only  
uv run test-linux          # Linux only
```

### Code Quality
```bash
# Format code
uv run format

# Run linting
uv run lint

# Development setup (install pre-commit hooks)
uv run dev-setup
```

### Architecture & Building
```bash
# Check system architecture
uv run check-arch

# Test architecture-specific builds
uv run test-arch

# Clean build artifacts
uv run clean

# Platform-specific builds
uv run build-macos-intel   # Intel macOS
uv run build-macos-arm     # ARM macOS
uv run build-windows       # Windows MSI
uv run build-linux-rpm     # Linux RPM
```

### Development Helpers
```bash
# Watch for changes and run tests
uv run watch-test

# CI test command
uv run ci-test
```

## Project Structure

```
p2pp/
├── pyproject.toml          # Project configuration and uv scripts
├── tests/
│   ├── conftest.py         # Pytest configuration and fixtures
│   ├── unit/               # Unit tests
│   ├── integration/        # Integration tests
│   └── e2e/                # End-to-end tests
├── scripts/
│   ├── check_architecture.py    # Architecture detection tool
│   └── test_architecture_builds.py  # Build testing tool
├── docs/
│   └── ARCHITECTURE_BUILDS.md      # Architecture documentation
└── .cursorrules           # Cursor AI rules
```

## Architecture-Specific Development

### Why No Universal2 Builds?

P2PP **cannot** use Universal2 builds because PyQt5/QtWebEngine doesn't support them properly. This causes crashes like:

```
ImportError: dlopen(...QtWebEngineWidgets.abi3.so, 0x0002): 
tried: '...' (mach-o file, but is an incompatible architecture 
(have (arm64), need (x86_64)))
```

### Building for Different Architectures

**macOS:**
```bash
# For Intel Macs
uv run build-macos-intel

# For Apple Silicon Macs
uv run build-macos-arm
```

**Windows:**
```bash
uv run build-windows
```

**Linux:**
```bash
uv run build-linux-rpm
```

### Testing Architecture Builds

```bash
# Test your system's architecture
uv run check-arch

# Test architecture-specific builds
uv run test-arch
```

## CI/CD Integration

The project uses GitHub Actions with uv for fast, reliable CI/CD:

```yaml
# Install uv in GitHub Actions
- name: Install uv
  run: |
    curl -LsSf https://astral.sh/uv/install.sh | sh
    echo "$HOME/.cargo/bin" >> $GITHUB_PATH

# Install dependencies
- name: Install dependencies
  run: uv sync --dev

# Run tests
- name: Run tests
  run: uv run ci-test
```

## Why uv Instead of Make?

uv provides several advantages over traditional Makefiles:

1. **Faster**: uv is incredibly fast at dependency resolution and installation
2. **Cross-platform**: Works identically on macOS, Windows, and Linux
3. **Python-native**: No need to learn Make syntax
4. **Dependency management**: Handles virtual environments automatically
5. **Caching**: Aggressive caching for faster repeated runs
6. **Modern**: Uses modern Python packaging standards

## Test Categories

Tests are organized by markers:

- `unit`: Fast unit tests for individual components
- `integration`: Integration tests for system components
- `e2e`: End-to-end tests for complete workflows
- `gui`: Tests requiring GUI (skipped in CI)
- `build`: Tests involving the build system
- `slow`: Tests that take longer to run
- `macos`/`windows`/`linux`: Platform-specific tests
- `intel`/`arm`: Architecture-specific tests

## Troubleshooting

### Common Issues

1. **PyQt5 import errors**: Make sure you're using the correct architecture build
2. **Build failures**: Run `uv run clean` then try building again
3. **Test failures**: Check if you have the right platform-specific dependencies

### Getting Help

```bash
# Check system info
uv run check-arch

# Run architecture tests
uv run test-arch

# Check project structure
uv run test-unit
```

## Contributing

1. Fork the repository
2. Set up development environment: `uv sync --dev && uv run dev-setup`
3. Make your changes
4. Run tests: `uv run test`
5. Format code: `uv run format`
6. Submit a pull request

All CI checks must pass, including:
- Unit tests on Python 3.8-3.12
- Integration tests on all platforms
- End-to-end tests for architecture-specific builds
- Code formatting and linting