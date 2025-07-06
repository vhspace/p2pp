#!/usr/bin/env python3
"""
P2PP Architecture Check Tool

This script helps users determine which P2PP build to download for their system.
Run this script and it will tell you which installer to use.

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
    
    if system == 'darwin':  # macOS
        if machine in ['x86_64', 'amd64']:
            return {
                'platform': 'macOS',
                'recommended': 'P2PP-intel.dmg',
                'reason': 'Intel-based Mac detected'
            }
        elif machine in ['arm64', 'aarch64']:
            return {
                'platform': 'macOS',
                'recommended': 'P2PP-arm.dmg', 
                'reason': 'Apple Silicon Mac detected'
            }
        else:
            return {
                'platform': 'macOS',
                'recommended': 'Check machine type manually',
                'reason': f'Unknown architecture: {machine}'
            }
    
    elif system == 'windows':  # Windows
        return {
            'platform': 'Windows',
            'recommended': 'P2PP.msi',
            'reason': 'Windows system detected'
        }
    
    elif system == 'linux':  # Linux
        # Try to detect distribution
        try:
            with open('/etc/os-release', 'r') as f:
                content = f.read().lower()
                if any(distro in content for distro in ['ubuntu', 'debian', 'mint']):
                    dist_type = 'DEB-based'
                    recommended = 'P2PP.deb'
                elif any(distro in content for distro in ['fedora', 'rhel', 'centos', 'suse']):
                    dist_type = 'RPM-based'
                    recommended = 'P2PP.rpm'
                else:
                    dist_type = 'Unknown'
                    recommended = 'P2PP.rpm or P2PP.deb'
        except:
            dist_type = 'Unknown'
            recommended = 'P2PP.rpm or P2PP.deb'
        
        return {
            'platform': 'Linux',
            'recommended': recommended,
            'reason': f'{dist_type} distribution detected'
        }
    
    else:
        return {
            'platform': 'Unknown',
            'recommended': 'Manual build required',
            'reason': f'Unsupported platform: {system}'
        }

def main():
    """Main function."""
    info = get_system_info()
    build_info = determine_build()
    
    print("P2PP Architecture Check")
    print("=" * 30)
    print(f"Operating System: {info['system']}")
    print(f"Architecture: {info['machine']}")
    print(f"Processor: {info['processor']}")
    print()
    
    platform_name = build_info['platform']
    print(f"{platform_name} Detected")
    print()
    
    if platform_name == 'macOS':
        print("You have a macOS system")
        if 'intel' in build_info['recommended'].lower():
            print("Recommendation: P2PP-intel.dmg - For Intel-based Macs")
        elif 'arm' in build_info['recommended'].lower():
            print("Recommendation: P2PP-arm.dmg - For Apple Silicon Macs")
        else:
            print(f"Recommendation: {build_info['recommended']}")
            
    elif platform_name == 'Windows':
        print("You have a Windows system")
        print("Recommendation: P2PP.msi - Universal Windows installer")
        
    elif platform_name == 'Linux':
        print("You have a Linux system")
        print("Choose based on your distribution:")
        print("  • P2PP.rpm - For Fedora, RHEL, SUSE, CentOS, etc.")
        print("  • P2PP.deb - For Ubuntu, Debian, Mint, etc.")
        print()
        if 'deb' in build_info['recommended'].lower():
            print("Detected Debian-based system -> Use P2PP.deb")
        elif 'rpm' in build_info['recommended'].lower():
            print("Detected RPM-based system -> Use P2PP.rpm")
            
    else:
        print(f"Unsupported platform: {platform_name}")
        print("You may need to build P2PP from source")
    
    print()
    print("Download from: https://github.com/vhspace/p2pp/releases/latest")
    print()
    print("Need help? See: docs/ARCHITECTURE_BUILDS.md")
    print()
    print("Important Notes:")
    print("• Never use Universal2 builds - they cause crashes")
    print("• Always download the correct architecture for your system")
    print("• If upgrading, completely remove the old version first")

if __name__ == "__main__":
    main()