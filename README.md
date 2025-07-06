# P2PP - Palette 2 Post Processing

P2PP processes gcode files for Palette 2 printers. Supports architecture-specific builds to avoid PyQt5/Universal2 crashes.

## Quick Start

```bash
# Check what build you need
python3 scripts/check_architecture.py

# Development setup  
uv venv && source .venv/bin/activate
uv sync --extra dev --no-build

# Run tests
python3 scripts/dev.py test-unit
```

## Architecture Detection

P2PP provides separate builds because PyQt5 breaks with Universal2:

- **macOS Intel**: P2PP-intel.dmg
- **macOS ARM**: P2PP-arm.dmg  
- **Windows**: P2PP.msi
- **Linux**: P2PP.deb or P2PP.rpm

Download from: https://github.com/vhspace/p2pp/releases/latest

## Development

### Setup
```bash
uv venv
source .venv/bin/activate
uv sync --extra dev --no-build
```

### Commands
```bash
python3 scripts/dev.py <command>

# Commands:
test-unit     # 18 unit tests
test-e2e      # End-to-end tests  
format        # Fix code formatting
check-arch    # System architecture
all          # Run everything
```

### Building

Requires Python 3.11 for cx_Freeze compatibility:

```bash
# macOS Intel
export ARCHFLAGS="-arch x86_64"
python setup.py py2app --arch=x86_64

# macOS ARM
export ARCHFLAGS="-arch arm64" 
python setup.py py2app --arch=arm64

# Windows
python setup.py bdist_msi

# Linux  
python setup.py bdist_rpm
```

## Testing

- **18 unit tests**: Core functionality validation
- **E2E tests**: Complete workflow verification
- **CI/CD**: GitHub Actions on all platforms

```bash
# Test everything
python3 scripts/dev.py all

# Individual test types
python3 scripts/dev.py test-unit
python3 scripts/dev.py test-e2e
```

## CI/CD

GitHub Actions workflow:
- Tests on Ubuntu, Windows, macOS Intel, macOS ARM
- Python 3.11 for cx_Freeze compatibility
- Architecture-specific builds on correct runners
- No Universal2 builds (prevents PyQt5 crashes)

## Technical Details

### Why Separate Architecture Builds
PyQt5/QtWebEngine incompatible with Universal2 builds. Error: "mach-o file, but is an incompatible architecture (have (arm64), need (x86_64))".

### Python Version
Uses Python 3.11 because cx_Freeze 7.2.8 doesn't support Python 3.13.

### Dependencies
- PyQt5 >= 5.15.0 (GUI framework)
- requests (HTTP client)
- setuptools (packaging)
- cx_Freeze (Windows/Linux builds)
- py2app (macOS builds)

## Project Status

✅ **Working**: Architecture detection, development environment, testing, CI/CD workflow
✅ **Tested**: 18/18 unit tests pass
✅ **Ready**: End-to-end production workflow

**Next**: Switch to Python 3.11 for actual building

## Features

- Multi-material optimization for Palette 2 printers
- Architecture-aware builds for maximum compatibility
- Comprehensive testing with unit, integration, and end-to-end tests
- Cross-platform support for macOS, Windows, and Linux
- Modern development workflow with uv and pytest

## Why uv?

- Fast dependency resolution and installation
- Cross-platform compatibility
- Python-native workflow
- Automatic virtual environment management
- Modern Python packaging standards

## Architecture Support

| Platform | Intel/x86_64 | ARM64/Apple Silicon | Universal2 |
|----------|-------------|-------------------|------------|
| macOS    | Supported | Supported      | Not supported* |
| Windows  | Supported | Future         | N/A |
| Linux    | Supported | Supported      | N/A |

*Universal2 not supported due to PyQt5/QtWebEngine limitations.

## Contributing

1. Fork the repository
2. Choose development method:
   - Easy: Use GitHub Codespaces or VS Code Dev Container
   - Local: Run `uv run start`
3. Make changes
4. Run `uv run all` (test + lint)
5. Submit pull request

All CI checks must pass including tests on Python 3.8-3.12 and architecture-specific builds.

## Support

- Issues: [GitHub Issues](https://github.com/vhspace/p2pp/issues)
- Architecture Problems: [Architecture Build Guide](docs/ARCHITECTURE_BUILDS.md)
- Development: [Development Guide](DEVELOPMENT.md)

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgements

Thanks to the 3D printing community and PyQt5 developers.

## Make a Donation

If you like this software and want to support its development you can make a small donation to support further development of P2PP.

[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=t.vandeneede@pandora.be&lc=EU&item_name=Donation+to+P2PP+Developer&no_note=0&cn=&currency_code=EUR&bn=PP-DonationsBF:btn_donateCC_LG.gif:NonHosted)

## **Good luck & happy printing !!!**





