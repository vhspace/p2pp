# P2PP Development Guide

Modern Python development with **uv** for package management and testing.

## Development Options

### Option 1: Development Container (Recommended)

**GitHub Codespaces:**
1. Click **Code** → **Create codespace**
2. Wait 2-3 minutes for setup
3. Start coding

**VS Code Dev Containers:**
1. Install [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
2. Open project in VS Code
3. `Ctrl+Shift+P` → "Dev Containers: Reopen in Container"

Includes: Python 3.12, uv, PyQt5, testing tools, GUI support
See [Dev Container Documentation](.devcontainer/README.md)

### Option 2: Local Development

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Complete setup
uv run start

# Verify setup
uv run check-arch
```

## Essential Commands

### New Developer Workflow
```bash
uv run start             # Complete setup (sync + dev-setup)
uv run quick             # Run unit tests
uv run check-arch        # Check system architecture
```

### Daily Development
```bash
uv run test              # All tests
uv run test-unit         # Unit tests only
uv run fix               # Auto-fix formatting
uv run all               # Test + lint everything
```

### Before Commits
```bash
uv run pre-commit        # Run pre-commit hooks
uv run ci-check          # Check CI compliance
```

### Building
```bash
uv run build             # Platform-specific build
uv run build-macos-intel # Intel macOS
uv run build-macos-arm   # ARM macOS
uv run build-windows     # Windows MSI
uv run build-linux-rpm   # Linux RPM
```

## Project Structure

```
p2pp/
├── pyproject.toml          # Project config + uv scripts
├── .devcontainer/          # Development container
├── tests/
│   ├── conftest.py         # Pytest config + fixtures
│   ├── unit/               # Unit tests
│   ├── integration/        # Integration tests
│   └── e2e/                # End-to-end tests
├── scripts/
│   ├── check_architecture.py    # Architecture detection
│   └── test_architecture_builds.py  # Build testing
└── docs/
    └── ARCHITECTURE_BUILDS.md      # Architecture docs
```

## Architecture Development

### Critical Rules
- **NEVER use Universal2 builds** - PyQt5/QtWebEngine breaks
- Always build separate Intel (x86_64) and ARM (arm64) for macOS
- Error: "mach-o file, but is an incompatible architecture"

### Build Commands
```bash
# macOS
uv run build-macos-intel   # Intel build
uv run build-macos-arm     # ARM build

# Other platforms
uv run build-windows       # Windows MSI
uv run build-linux-rpm     # Linux RPM
```

### Testing
```bash
uv run check-arch          # Check system
uv run test-arch           # Test builds
```

## Test Categories

Use pytest markers:
- `@pytest.mark.unit` - Fast unit tests
- `@pytest.mark.integration` - System tests
- `@pytest.mark.e2e` - End-to-end tests
- `@pytest.mark.gui` - GUI tests (skip in CI)
- `@pytest.mark.macos/.windows/.linux` - Platform-specific
- `@pytest.mark.intel/.arm` - Architecture-specific

## CI/CD Integration

```yaml
# GitHub Actions
- name: Install uv
  run: curl -LsSf https://astral.sh/uv/install.sh | sh

- name: Setup
  run: uv run setup

- name: Test
  run: uv run ci-test
```

## Why uv?

- Fast dependency resolution
- Cross-platform compatibility
- Python-native workflow
- Automatic virtual environments
- Modern packaging standards

## Troubleshooting

### Common Issues
1. **PyQt5 import errors**: Use correct architecture build
2. **Build failures**: Run `uv run clean` first
3. **Test failures**: Check platform dependencies

### Development Container Issues
```bash
# Restart virtual display
/usr/local/bin/start-xvfb

# Check environment
echo $DISPLAY
echo $QT_QPA_PLATFORM

# Test GUI support
xvfb-run -a uv run test-unit
```

## Contributing

1. Fork repository
2. Choose method:
   - Easy: GitHub Codespaces or VS Code Dev Container
   - Local: `uv run start`
3. Make changes
4. Run `uv run all`
5. Submit pull request

CI checks: Python 3.8-3.12, all platforms, architecture builds.