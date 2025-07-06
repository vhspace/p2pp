# P2PP Development Container

This development container provides a complete, ready-to-use environment for P2PP development with all necessary tools pre-installed.

## What's Included

### Core Tools
- **Python 3.12** - Latest stable Python version
- **uv** - Fast Python package manager and task runner
- **Git** - Version control
- **VS Code Extensions** - Pre-configured for Python development

### Testing & Quality Tools
- **pytest** - Testing framework with coverage support
- **black** - Code formatter
- **isort** - Import sorter
- **flake8** - Linting
- **mypy** - Type checking
- **pre-commit** - Git hooks for code quality

### GUI Development
- **PyQt5** - GUI framework (system packages)
- **Xvfb** - Virtual display for headless GUI testing
- **Qt development tools** - For building Qt applications

### Build Tools
- **RPM tools** - For Linux RPM package building
- **DEB tools** - For Linux DEB package building
- **Build essentials** - Compilers and build tools

## Quick Start

1. **Open in Dev Container**
   - VS Code: `Ctrl+Shift+P` → "Dev Containers: Reopen in Container"
   - GitHub Codespaces: Click "Code" → "Create codespace"

2. **Wait for Setup**
   - The container will automatically run `post-create.sh`
   - This installs all dependencies and runs initial tests
   - Takes ~2-3 minutes on first run

3. **Start Developing**
   ```bash
   # Run tests
   uv run test
   
   # Check your architecture
   uv run check-arch
   
   # Format code
   uv run format
   ```

## Environment Features

### Pre-configured VS Code Settings
- Python testing with pytest enabled
- Auto-formatting on save with black
- Import sorting with isort
- Linting with flake8 and mypy
- Integrated terminal with uv aliases

### Virtual Display Setup
For GUI testing without a physical display:
```bash
export DISPLAY=:1
# Or run commands with xvfb-run:
xvfb-run -a uv run test-e2e
```

### uv Cache Optimization
- UV cache is mounted to `.uv-cache/` for fast rebuilds
- Dependencies are cached between container rebuilds
- Significantly faster setup on subsequent starts

## Available Commands

All commands use uv for consistency and speed:

```bash
# Testing
uv run test              # All tests
uv run test-unit         # Unit tests only
uv run test-integration  # Integration tests
uv run test-e2e          # End-to-end tests
uv run test-coverage     # With coverage report

# Code Quality
uv run format           # Format with black + isort
uv run lint             # Lint with flake8 + mypy

# Architecture & Building
uv run check-arch       # Check system architecture
uv run test-arch        # Test architecture builds
uv run clean            # Clean build artifacts

# Development
uv run dev-setup        # Install pre-commit hooks
```

## Troubleshooting

### GUI Applications
If you get display-related errors:
```bash
export DISPLAY=:1
/usr/local/bin/start-xvfb  # Restart virtual display
```

### Permission Issues
The container runs as the `vscode` user (UID 1000):
```bash
sudo chown -R vscode:vscode /workspace
```

### uv Not Found
If uv commands don't work:
```bash
export PATH="$HOME/.cargo/bin:$PATH"
source ~/.bashrc
```

### PyQt5 Import Errors
For PyQt5 issues in headless mode:
```bash
export QT_QPA_PLATFORM=xcb
export DISPLAY=:1
```

## Container Specifications

| Component | Version/Source |
|-----------|---------------|
| Base Image | `mcr.microsoft.com/devcontainers/python:3.12` |
| Python | 3.12 |
| uv | Latest (installed from official script) |
| Operating System | Debian-based |
| Architecture | x86_64 (Intel/AMD64) |

## Performance Optimizations

1. **uv Caching**: Dependencies cached in mounted volume
2. **System Packages**: PyQt5 installed via apt for speed
3. **Multi-stage Setup**: Base dependencies in Dockerfile, dev tools in post-create
4. **Non-root User**: Better security and file permissions

## Extending the Container

To add new tools or dependencies:

1. **System packages**: Add to `Dockerfile`
2. **Python packages**: Add to `pyproject.toml`
3. **VS Code extensions**: Add to `devcontainer.json`
4. **Setup scripts**: Modify `post-create.sh`

## Related Documentation

- [Development Guide](../DEVELOPMENT.md) - Complete development workflow
- [Architecture Guide](../docs/ARCHITECTURE_BUILDS.md) - Architecture-specific builds
- [Project README](../README.md) - Main project documentation

---

💡 **Tip**: The dev container is optimized for P2PP's architecture-specific build requirements. It includes tools for testing both Intel and ARM compatibility, even on x86_64 hosts.