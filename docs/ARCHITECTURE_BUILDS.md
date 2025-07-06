# Architecture-Specific Builds for P2PP

## Overview

P2PP now provides separate builds for different computer architectures to ensure maximum compatibility and performance. This document explains why this change was necessary and how to choose the right build for your system.

## The Problem: Universal2 Build Issues

Previously, P2PP attempted to use macOS Universal2 builds that would work on both Intel and Apple Silicon Macs. However, this approach caused crashes due to compatibility issues with PyQt5 and QtWebEngine libraries.

### Error Symptoms

If you downloaded the wrong architecture build, you might see errors like:

```
ImportError: dlopen(.../QtWebEngineWidgets.abi3.so, 0x0002): 
tried: '...' (mach-o file, but is an incompatible architecture 
(have (arm64), need (x86_64)))
```

This error occurs when:
- Running an ARM64 build on an Intel Mac
- Running an Intel build on an Apple Silicon Mac
- Libraries were compiled for the wrong architecture

## The Solution: Architecture-Specific Builds

P2PP now provides separate, optimized builds for each architecture:

### macOS Builds
- **P2PP-intel.dmg**: For Intel-based Macs (x86_64)
- **P2PP-arm.dmg**: For Apple Silicon Macs (ARM64/M1/M2/M3)

### Windows Builds
- **P2PP.msi**: For Windows systems (x86_64)

### Linux Builds
- **P2PP.rpm**: RPM package for RPM-based distributions
- **P2PP.deb**: DEB package for Debian-based distributions

## How to Choose the Right Build

### For macOS Users

#### Check Your Mac Type
1. Click the Apple menu → "About This Mac"
2. Look at the "Processor" or "Chip" line:
   - **Intel**: Download `P2PP-intel.dmg`
   - **Apple M1/M2/M3**: Download `P2PP-arm.dmg`

#### Command Line Check
```bash
uname -m
# x86_64 = Intel Mac → use P2PP-intel.dmg
# arm64 = Apple Silicon → use P2PP-arm.dmg
```

### For Windows Users
Download the standard `P2PP.msi` installer.

### For Linux Users
Choose the package format for your distribution:
- **RPM**: Fedora, RHEL, SUSE, etc.
- **DEB**: Ubuntu, Debian, Mint, etc.

## Installation Instructions

### macOS
1. Download the correct DMG for your architecture
2. Open the DMG file
3. Drag P2PP.app to your Applications folder
4. If you see a security warning, go to System Preferences → Security & Privacy and click "Open Anyway"

### Windows
1. Download the MSI installer
2. Run the installer as Administrator
3. Follow the installation wizard

### Linux
```bash
# For RPM-based systems
sudo rpm -i P2PP.rpm

# For DEB-based systems
sudo dpkg -i P2PP.deb
sudo apt-get install -f  # Fix any dependency issues
```

## Troubleshooting

### "App is damaged and can't be opened" (macOS)
This may happen with downloaded apps. Try:
```bash
xattr -d com.apple.quarantine /Applications/P2PP.app
```

### Architecture Mismatch Error
If you get an architecture error:
1. Check your system architecture (see above)
2. Download the correct build for your architecture
3. Completely remove the old version before installing

### Performance Issues
- Intel builds running on Apple Silicon may be slower (Rosetta translation)
- Always use native ARM builds on Apple Silicon for best performance

## For Developers

### Building Locally

#### macOS
```bash
# For Intel
export ARCHFLAGS="-arch x86_64"
python setup.py py2app --arch=x86_64

# For Apple Silicon
export ARCHFLAGS="-arch arm64"
python setup.py py2app --arch=arm64
```

#### Windows
```bash
python setup.py bdist_msi
```

#### Linux
```bash
python setup.py bdist_rpm
```

### Testing Builds
Use the provided test script to verify builds work correctly:
```bash
python scripts/test_architecture_builds.py
```

This script will:
- Build for your current architecture
- Test app launch and basic functionality
- Verify library compatibility
- Check for common issues

### Cross-Compilation
- **Apple Silicon Macs** can build Intel binaries (with proper setup)
- **Intel Macs** cannot reliably build ARM binaries
- Always test builds on target architecture when possible

## Continuous Integration

The project uses GitHub Actions to automatically build for all architectures:
- **macos-13**: Intel builds
- **macos-14**: ARM builds  
- **windows-latest**: Windows builds
- **ubuntu-latest**: Linux builds

Each build includes end-to-end testing to ensure:
- Package creation succeeds
- Architecture is correct
- App launches properly
- Dependencies load correctly

## Benefits of Architecture-Specific Builds

1. **Reliability**: No more architecture compatibility crashes
2. **Performance**: Native code runs faster than emulated
3. **Size**: Smaller downloads (no unused architecture code)
4. **Testing**: Each build is thoroughly tested on target platform

## Migration from Universal2

If you previously used a universal2 build:
1. Uninstall the old version completely
2. Download the correct architecture-specific build
3. Install normally

Your settings and data will be preserved.

## Support

If you're unsure which build to download or encounter issues:
1. Check your system architecture using the methods above
2. Try the architecture test script if you're building locally
3. Report issues on GitHub with your system information