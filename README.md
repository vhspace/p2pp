# P2PP - Palette2 Post Processing tool for PrusaSlicer/Slic3r PE

P2PP is a post-processing tool that optimizes G-code files for Palette 2 multi-material printing.

## Download & Installation

### Quick Architecture Check
```bash
# If you have uv installed:
uv run check-arch

# Or run directly:
python scripts/check_architecture.py
```

### Available Builds

#### macOS
- **P2PP-intel.dmg** - Intel-based Macs (x86_64)
- **P2PP-arm.dmg** - Apple Silicon Macs (M1/M2/M3)

#### Windows
- **P2PP.msi** - Universal Windows installer

#### Linux
- **P2PP.rpm** - RPM-based distributions (Fedora, RHEL, SUSE)
- **P2PP.deb** - DEB-based distributions (Ubuntu, Debian, Mint)

**[Download Latest Release](https://github.com/vhspace/p2pp/releases/latest)**

### Architecture-Specific Builds

P2PP provides separate builds for different architectures. Universal2 builds are not supported due to PyQt5/QtWebEngine limitations.

Downloading the wrong architecture causes errors like:
```
ImportError: dlopen(...QtWebEngineWidgets.abi3.so, 0x0002): 
tried: '...' (mach-o file, but is an incompatible architecture 
(have (arm64), need (x86_64)))
```

See [Architecture Build Guide](docs/ARCHITECTURE_BUILDS.md) for details.

## Development

P2PP uses modern Python tooling with **uv** for package management and testing.

### Quick Start

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Complete setup
uv run start

# Run tests
uv run test

# Check architecture
uv run check-arch
```

### Common Commands

```bash
# Testing
uv run test              # All tests
uv run test-unit         # Unit tests
uv run test-coverage     # With coverage

# Code Quality
uv run fix               # Auto-fix formatting
uv run lint              # Run linting

# Building
uv run build             # Platform-specific build
uv run build-macos-intel # Intel macOS
uv run build-macos-arm   # ARM macOS
```

See [Development Guide](DEVELOPMENT.md) for complete documentation.

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





