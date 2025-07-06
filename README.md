# P2PP - Palette 2 Post Processing

P2PP processes gcode files for Palette 2 printers. Architecture-specific builds avoid PyQt5/Universal2 crashes.

## Quick Start

```bash
python3 scripts/check_architecture.py  # Check build needed
uv venv && source .venv/bin/activate
uv sync --extra dev --no-build
python3 scripts/dev.py test-unit
```

## Downloads

- macOS Intel: P2PP-intel.dmg
- macOS ARM: P2PP-arm.dmg  
- Windows: P2PP.msi
- Linux: P2PP.deb or P2PP.rpm

Download: https://github.com/vhspace/p2pp/releases/latest

## Development

```bash
# Setup
uv venv
source .venv/bin/activate
uv sync --extra dev --no-build

# Commands
python3 scripts/dev.py test-unit     # Unit tests
python3 scripts/dev.py test-e2e-fast # E2E tests  
python3 scripts/dev.py check-arch    # Architecture
python3 scripts/dev.py all           # All checks
```

## Building

Python 3.11 required for cx_Freeze compatibility.

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

## Architecture Issue

PyQt5/QtWebEngine incompatible with Universal2 builds. Error: "mach-o file, but is an incompatible architecture".

## Features

- Multi-material optimization for Palette 2 printers
- Automatic splice point calculation
- Purge tower generation
- Support for multiple slicer formats
- Real-time processing feedback







