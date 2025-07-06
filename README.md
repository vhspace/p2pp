# P2PP - **Palette2 Post Processing tool for PrusaSlicer/Slic3r PE**

P2PP is a post-processing tool that optimizes G-code files for Palette 2 multi-material printing, ensuring better print quality and reliability.

## Download & Installation

### Quick Architecture Check
Not sure which build to download? Run this script to find out:
```bash
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

### ⚠️ Important: Architecture Compatibility
- **Never use Universal2 builds** - they cause crashes with PyQt5
- Download the correct build for your system architecture
- See [Architecture Build Guide](docs/ARCHITECTURE_BUILDS.md) for detailed instructions

## Getting Started

Have a look at the [P2PP Wiki pages](https://github.com/tomvandeneede/p2pp/wiki/Home) to get you started.

## For Developers

### Local Development
```bash
# Clone the repository
git clone https://github.com/vhspace/p2pp.git
cd p2pp

# Set up virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies for your platform
pip install -r requirements-mac.txt     # macOS
pip install -r requirements-win.txt     # Windows
pip install -r requirements-linux.txt   # Linux
```

### Building Locally
```bash
# macOS - Intel
export ARCHFLAGS="-arch x86_64"
python setup.py py2app --arch=x86_64

# macOS - Apple Silicon
export ARCHFLAGS="-arch arm64"
python setup.py py2app --arch=arm64

# Windows
python setup.py bdist_msi

# Linux
python setup.py bdist_rpm
```

### Testing Builds
```bash
# Test your build works correctly
python scripts/test_architecture_builds.py
```

## Architecture & Build System

P2PP uses architecture-specific builds to ensure maximum compatibility and performance:

- **Separate Intel/ARM builds** prevent QtWebEngine compatibility issues
- **End-to-end testing** validates each build on target platforms  
- **Cross-compilation support** allows ARM Macs to build Intel binaries
- **Automated CI/CD** builds and tests all architectures on every release

See [Architecture Build Documentation](docs/ARCHITECTURE_BUILDS.md) for complete details.

## Acknowledgements

Thanks to:
- Tim Brookman for the co-development of this plugin
- Klaus, Khalil, Casey, Jermaul, Paul, Gideon (and all others) for the endless testing and valuable feedback and the ongoing P2PP support to the community...it's them driving the improvements
- Kurt for making the instructional video on setting up and using P2PP

## Make a Donation

If you like this software and want to support its development you can make a small donation to support further development of P2PP.

[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=t.vandeneede@pandora.be&lc=EU&item_name=Donation+to+P2PP+Developer&no_note=0&cn=&currency_code=EUR&bn=PP-DonationsBF:btn_donateCC_LG.gif:NonHosted)

## **Good luck & happy printing !!!**





