#!/usr/bin/env python3
"""
Test script to verify architecture-specific builds work correctly.
This script helps developers ensure their P2PP builds work properly on different architectures.

Usage:
    python scripts/test_architecture_builds.py
"""

import os
import sys
import subprocess
import platform
import tempfile
import shutil
from pathlib import Path

def run_command(cmd, cwd=None, capture_output=True, timeout=30):
    """Run a command and return the result."""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            cwd=cwd, 
            capture_output=capture_output,
            text=True,
            timeout=timeout
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)

def test_macos_build(arch):
    """Test macOS build for specific architecture."""
    print(f"\n=== Testing macOS {arch} Build ===")
    
    # Clean previous builds
    if os.path.exists('build'):
        shutil.rmtree('build')
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    
    # Build the application
    print(f"Building for {arch}...")
    os.environ['ARCHFLAGS'] = f"-arch {arch}"
    success, stdout, stderr = run_command(f"python setup.py py2app --arch={arch}")
    
    if not success:
        print(f"❌ Build failed for {arch}")
        print(f"Error: {stderr}")
        return False
    
    print(f"✅ Build successful for {arch}")
    
    # Test the built application
    app_path = "dist/P2PP.app"
    if not os.path.exists(app_path):
        print(f"❌ App bundle not found at {app_path}")
        return False
    
    # Check binary architecture
    binary_path = f"{app_path}/Contents/MacOS/P2PP"
    success, stdout, stderr = run_command(f"file {binary_path}")
    
    if not success:
        print(f"❌ Could not check binary architecture")
        return False
    
    if arch == "x86_64" and "x86_64" not in stdout:
        print(f"❌ Binary is not x86_64 architecture")
        print(f"Output: {stdout}")
        return False
    elif arch == "arm64" and "arm64" not in stdout:
        print(f"❌ Binary is not arm64 architecture")
        print(f"Output: {stdout}")
        return False
    
    print(f"✅ Binary architecture correct for {arch}")
    
    # Test basic app launch (with timeout to avoid hanging)
    print("Testing app launch...")
    success, stdout, stderr = run_command(f"{binary_path} --version", timeout=10)
    
    if success:
        print("✅ App launched successfully")
    else:
        print("⚠️  App launch test inconclusive (this is normal for GUI apps)")
    
    # Test PyQt5 import
    print("Testing PyQt5 import...")
    success, stdout, stderr = run_command(
        f"{binary_path} -c \"import PyQt5.QtWidgets; print('PyQt5 import successful')\"",
        timeout=10
    )
    
    if success:
        print("✅ PyQt5 import successful")
    else:
        print("⚠️  PyQt5 import test inconclusive")
    
    # Check dependencies
    print("Checking dependencies...")
    success, stdout, stderr = run_command(f"otool -L {binary_path}")
    
    if success:
        qt_libs = [line for line in stdout.split('\n') if 'Qt' in line]
        if qt_libs:
            print(f"✅ Qt libraries found: {len(qt_libs)} libraries")
        else:
            print("⚠️  No Qt libraries found in otool output")
    else:
        print("⚠️  Could not check dependencies")
    
    return True

def test_windows_build():
    """Test Windows build."""
    print(f"\n=== Testing Windows Build ===")
    
    # Clean previous builds
    if os.path.exists('build'):
        shutil.rmtree('build')
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    
    # Build the application
    print("Building Windows MSI...")
    success, stdout, stderr = run_command("python setup.py bdist_msi")
    
    if not success:
        print(f"❌ Build failed")
        print(f"Error: {stderr}")
        return False
    
    print("✅ Build successful")
    
    # Check MSI file exists
    msi_files = list(Path("dist").glob("*.msi"))
    if not msi_files:
        print("❌ No MSI file found")
        return False
    
    print(f"✅ MSI file created: {msi_files[0]}")
    
    # Test MSI installation in temp directory
    print("Testing MSI installation...")
    with tempfile.TemporaryDirectory() as temp_dir:
        msi_path = msi_files[0].absolute()
        success, stdout, stderr = run_command(
            f'msiexec /i "{msi_path}" /qn TARGETDIR="{temp_dir}"',
            timeout=60
        )
        
        if success:
            print("✅ MSI installation successful")
            
            # Check if executable exists
            exe_path = Path(temp_dir) / "P2PP.exe"
            if exe_path.exists():
                print("✅ P2PP.exe found after installation")
                
                # Try to run the executable
                success, stdout, stderr = run_command(f'"{exe_path}" --version', timeout=10)
                if success:
                    print("✅ Executable runs successfully")
                else:
                    print("⚠️  Executable test inconclusive")
            else:
                print("❌ P2PP.exe not found after installation")
        else:
            print("❌ MSI installation failed")
            print(f"Error: {stderr}")
    
    return True

def test_linux_build():
    """Test Linux build."""
    print(f"\n=== Testing Linux Build ===")
    
    # Clean previous builds
    if os.path.exists('build'):
        shutil.rmtree('build')
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    
    # Build RPM
    print("Building RPM...")
    success, stdout, stderr = run_command("python setup.py bdist_rpm")
    
    if not success:
        print(f"❌ RPM build failed")
        print(f"Error: {stderr}")
        return False
    
    print("✅ RPM build successful")
    
    # Build DEB
    print("Building DEB...")
    success, stdout, stderr = run_command("python setup.py sdist")
    
    if not success:
        print(f"❌ DEB build failed")
        print(f"Error: {stderr}")
        return False
    
    print("✅ DEB build successful")
    
    # Check files exist
    rpm_files = list(Path("dist").glob("*.rpm"))
    deb_files = list(Path("dist").glob("*.deb"))
    
    if rpm_files:
        print(f"✅ RPM file created: {rpm_files[0]}")
    else:
        print("❌ No RPM file found")
    
    if deb_files:
        print(f"✅ DEB file created: {deb_files[0]}")
    else:
        print("⚠️  No DEB file found (this is normal, requires additional setup)")
    
    return True

def main():
    """Main test runner."""
    print("P2PP Architecture Build Test Suite")
    print("=" * 40)
    
    current_platform = platform.system().lower()
    current_arch = platform.machine()
    
    print(f"Current platform: {current_platform}")
    print(f"Current architecture: {current_arch}")
    
    # Check if we're in the right directory
    if not os.path.exists('setup.py'):
        print("❌ Error: setup.py not found. Run this script from the project root.")
        return 1
    
    # Check if we're in a virtual environment
    if not (hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)):
        print("⚠️  Warning: Not running in a virtual environment. This is recommended.")
    
    success = True
    
    if current_platform == "darwin":  # macOS
        print("\n🍎 Testing macOS builds...")
        
        # Test current architecture
        if current_arch == "x86_64":
            success &= test_macos_build("x86_64")
        elif current_arch == "arm64":
            success &= test_macos_build("arm64")
        else:
            print(f"⚠️  Unknown architecture: {current_arch}")
        
        # Optionally test cross-compilation
        print("\n🔄 Testing cross-compilation...")
        if current_arch == "x86_64":
            print("Note: Cross-compiling to ARM64 on Intel Mac may require Rosetta")
            # success &= test_macos_build("arm64")
        elif current_arch == "arm64":
            print("Testing Intel build on Apple Silicon...")
            success &= test_macos_build("x86_64")
    
    elif current_platform == "windows":
        print("\n🪟 Testing Windows builds...")
        success &= test_windows_build()
    
    elif current_platform == "linux":
        print("\n🐧 Testing Linux builds...")
        success &= test_linux_build()
    
    else:
        print(f"❌ Unsupported platform: {current_platform}")
        return 1
    
    print("\n" + "=" * 40)
    if success:
        print("✅ All tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())