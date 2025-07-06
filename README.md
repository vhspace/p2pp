# P2PP - **Palette2 Post Processing tool for PrusaSlicer/Slic3r PE**

P2PP is a post-processing tool that optimizes G-code files for Palette 2 multi-material printing, ensuring better print quality and reliability.

## Download & Installation

### Quick Architecture Check
Not sure which build to download? Run this script to find out:
```bash
# If you have Python/uv installed:
uv run check-arch

# Or download and run:
python scripts/check_architecture.py
```

### Available Builds

#### macOS
- **P2PP-intel.dmg** - For Intel-based Macs (x86_64)
- **P2PP-arm.dmg** - For Apple Silicon Macs (M1/M2/M3)

#### Windows
- **P2PP.msi** - Universal Windows installer

#### Linux
- **P2PP.rpm** - For RPM-based distributions (Fedora, RHEL, SUSE)
- **P2PP.deb** - For DEB-based distributions (Ubuntu, Debian, Mint)

📥 **[Download Latest Release](https://github.com/vhspace/p2pp/releases/latest)**

### Important: Architecture-Specific Builds

P2PP provides **separate builds for different architectures** to ensure maximum compatibility. Universal2 builds are **not supported** due to PyQt5/QtWebEngine limitations.

If you download the wrong architecture, you may see errors like:
```
ImportError: dlopen(...QtWebEngineWidgets.abi3.so, 0x0002): 
tried: '...' (mach-o file, but is an incompatible architecture 
(have (arm64), need (x86_64)))
```

📖 **[Architecture Build Guide](docs/ARCHITECTURE_BUILDS.md)**

## Development

P2PP uses modern Python tooling with **uv** for fast package management and testing.

### Quick Start

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Set up development environment
uv sync --dev
uv run dev-setup

# Run tests
uv run test

# Check your architecture
uv run check-arch
```

### Common Development Commands

```bash
# Testing
uv run test              # Run all tests
uv run test-unit         # Fast unit tests
uv run test-integration  # Integration tests
uv run test-e2e          # End-to-end tests
uv run test-coverage     # With coverage report

# Code Quality
uv run format           # Format code
uv run lint             # Run linting

# Building
uv run build-macos-intel  # Intel macOS
uv run build-macos-arm    # ARM macOS
uv run build-windows      # Windows MSI
uv run build-linux-rpm    # Linux RPM
```

📚 **[Complete Development Guide](DEVELOPMENT.md)**

## Features

- **Multi-material optimization** for Palette 2 printers
- **Architecture-aware builds** for maximum compatibility
- **Comprehensive testing** with unit, integration, and end-to-end tests
- **Cross-platform support** for macOS, Windows, and Linux
- **Modern development workflow** with uv and pytest

## Why uv?

This project uses [uv](https://docs.astral.sh/uv/) for several advantages:

- **⚡ Fast**: Incredibly fast dependency resolution and installation
- **🔧 Cross-platform**: Works identically on macOS, Windows, and Linux
- **🐍 Python-native**: No need to learn Make or other build tools
- **📦 Dependency management**: Handles virtual environments automatically
- **🚀 Modern**: Uses modern Python packaging standards

## Architecture Support

| Platform | Intel/x86_64 | ARM64/Apple Silicon | Universal2 |
|----------|-------------|-------------------|------------|
| macOS    | ✅ Supported | ✅ Supported      | ❌ Not supported* |
| Windows  | ✅ Supported | ⚠️ Future         | N/A |
| Linux    | ✅ Supported | ✅ Supported      | N/A |

*Universal2 is not supported due to PyQt5/QtWebEngine limitations.

## Contributing

We welcome contributions! Please see our [Development Guide](DEVELOPMENT.md) for details on:

- Setting up the development environment
- Running tests locally
- Architecture-specific building
- Code quality standards

## Support

- 📋 **Issues**: [GitHub Issues](https://github.com/vhspace/p2pp/issues)
- 🏗️ **Architecture Problems**: See [Architecture Build Guide](docs/ARCHITECTURE_BUILDS.md)
- 💻 **Development**: See [Development Guide](DEVELOPMENT.md)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

Thanks to:
- Tim Brookman for the co-development of this plugin
- Klaus, Khalil, Casey, Jermaul, Paul, Gideon (and all others) for the endless testing and valuable feedback and the ongoing P2PP support to the community...it's them driving the improvements
- Kurt for making the instructional video on setting up and using P2PP

## Make a Donation

If you like this software and want to support its development you can make a small donation to support further development of P2PP.

[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=t.vandeneede@pandora.be&lc=EU&item_name=Donation+to+P2PP+Developer&no_note=0&cn=&currency_code=EUR&bn=PP-DonationsBF:btn_donateCC_LG.gif:NonHosted)

## **Good luck & happy printing !!!**





