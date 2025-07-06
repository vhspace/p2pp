#!/usr/bin/env python3
"""
Simple architecture detection for P2PP downloads.
Uses Python's built-in platform module.
"""

import platform


def get_download_info():
    """Get download recommendation based on current system."""
    system = platform.system()
    machine = platform.machine()
    
    if system == "Darwin":  # macOS
        if machine in ["x86_64", "AMD64"]:
            return {
                "platform": "macOS Intel", 
                "file": "P2PP-intel.dmg",
                "arch": "x86_64"
            }
        elif machine in ["arm64", "aarch64"]:
            return {
                "platform": "macOS Apple Silicon", 
                "file": "P2PP-arm.dmg",
                "arch": "arm64"
            }
    
    elif system == "Windows":
        return {
            "platform": "Windows", 
            "file": "P2PP.msi",
            "arch": machine
        }
    
    elif system == "Linux":
        # Simple distribution detection
        try:
            with open("/etc/os-release") as f:
                content = f.read().lower()
                if any(x in content for x in ["ubuntu", "debian", "mint"]):
                    return {
                        "platform": "Linux (Debian-based)", 
                        "file": "P2PP.deb",
                        "arch": machine
                    }
                elif any(x in content for x in ["fedora", "rhel", "centos", "suse"]):
                    return {
                        "platform": "Linux (RPM-based)", 
                        "file": "P2PP.rpm", 
                        "arch": machine
                    }
        except FileNotFoundError:
            pass
        
        return {
            "platform": "Linux", 
            "file": "P2PP.rpm or P2PP.deb",
            "arch": machine
        }
    
    return {
        "platform": f"Unknown ({system})", 
        "file": "Source build required",
        "arch": machine
    }


def main():
    """Main function."""
    info = get_download_info()
    
    print("P2PP Architecture Check")
    print("=" * 30)
    print(f"System: {platform.system()}")
    print(f"Architecture: {platform.machine()}")
    print(f"Platform: {info['platform']}")
    print()
    print(f"Recommended download: {info['file']}")
    print()
    print("Download from: https://github.com/vhspace/p2pp/releases/latest")
    print()
    print("Important: Never use Universal2 builds - they cause crashes with PyQt5")


if __name__ == "__main__":
    main()