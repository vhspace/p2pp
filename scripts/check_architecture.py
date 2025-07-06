#!/usr/bin/env python3
"""
P2PP Architecture Check Tool

This script helps users determine which P2PP build to download for their system.
Simply run this script and it will tell you which installer to use.

Usage:
    python scripts/check_architecture.py
"""

import platform
import sys

def get_system_info():
    """Get system information."""
    system = platform.system()
    machine = platform.machine()
    processor = platform.processor()
    
    return {
        'system': system,
        'machine': machine,
        'processor': processor,
        'python_version': sys.version
    }

def determine_build():
    """Determine which P2PP build the user should download."""
    info = get_system_info()
    system = info['system'].lower()
    machine = info['machine'].lower()
    
    print("🔍 P2PP Architecture Check")
    print("=" * 30)
    print(f"Operating System: {info['system']}")
    print(f"Architecture: {info['machine']}")
    print(f"Processor: {info['processor']}")
    print()
    
    if system == "darwin":  # macOS
        print("🍎 macOS Detected")
        print()
        
        if machine == "x86_64":
            print("✅ You have an Intel Mac")
            print("📥 Download: P2PP-intel.dmg")
            print("💡 This build is optimized for Intel processors")
        elif machine == "arm64":
            print("✅ You have an Apple Silicon Mac (M1/M2/M3)")
            print("📥 Download: P2PP-arm.dmg")
            print("💡 This build is optimized for Apple Silicon")
        else:
            print(f"⚠️  Unknown Mac architecture: {machine}")
            print("📥 Try: P2PP-intel.dmg (most compatible)")
    
    elif system == "windows":
        print("🪟 Windows Detected")
        print()
        print("✅ You have a Windows system")
        print("📥 Download: P2PP.msi")
        print("💡 Standard Windows installer for all Windows versions")
    
    elif system == "linux":
        print("🐧 Linux Detected")
        print()
        print("✅ You have a Linux system")
        print("📥 Choose based on your distribution:")
        print("   • P2PP.rpm - For Fedora, RHEL, SUSE, CentOS, etc.")
        print("   • P2PP.deb - For Ubuntu, Debian, Mint, etc.")
        print()
        
        # Try to detect distribution
        try:
            with open('/etc/os-release', 'r') as f:
                os_release = f.read().lower()
                if any(distro in os_release for distro in ['ubuntu', 'debian', 'mint']):
                    print("💡 Detected Debian-based system → Use P2PP.deb")
                elif any(distro in os_release for distro in ['fedora', 'rhel', 'centos', 'suse']):
                    print("💡 Detected RPM-based system → Use P2PP.rpm")
        except:
            pass
    
    else:
        print(f"❌ Unsupported operating system: {system}")
        print("P2PP supports macOS, Windows, and Linux")
        return
    
    print()
    print("🔗 Download from: https://github.com/vhspace/p2pp/releases/latest")
    print()
    print("📚 Need help? See: docs/ARCHITECTURE_BUILDS.md")
    
    # Check for potential issues
    print()
    print("⚠️  Important Notes:")
    print("• Never use Universal2 builds - they cause crashes")
    print("• Always download the correct architecture for your system")
    print("• If upgrading, completely remove the old version first")

def main():
    """Main function."""
    try:
        determine_build()
    except Exception as e:
        print(f"❌ Error determining system information: {e}")
        print("Please check manually:")
        print("• macOS: Apple menu → About This Mac")
        print("• Windows: Any P2PP.msi will work")
        print("• Linux: Check your distribution package manager")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())