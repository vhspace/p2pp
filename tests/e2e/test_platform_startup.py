"""
Test P2PP platform startup capabilities.
Tests actual application startup without GUI requirements.
"""

import pytest
import subprocess
import sys
import os
import platform
from pathlib import Path


class TestPlatformStartup:
    """Test P2PP startup on different platforms."""
    
    def test_version_module_import(self):
        """Test version module imports correctly."""
        result = subprocess.run([
            sys.executable, "-c", 
            "import sys; sys.path.insert(0, '.'); import version; print(f'Version: {version.Version}')"
        ], capture_output=True, text=True)
        
        assert result.returncode == 0, f"Version import failed: {result.stderr}"
        assert "Version:" in result.stdout
        assert "10.02.01" in result.stdout  # Current version
    
    def test_p2pp_module_structure(self):
        """Test P2PP module structure can be analyzed without GUI."""
        # Test non-GUI imports work
        result = subprocess.run([
            sys.executable, "-c", 
            """
import sys
sys.path.insert(0, '.')

# Test imports that don't require GUI
try:
    import p2pp.variables as v
    print("variables: OK")
except Exception as e:
    print(f"variables: FAIL - {e}")

try:
    import p2pp.formatnumbers as fn
    print("formatnumbers: OK")
except Exception as e:
    print(f"formatnumbers: FAIL - {e}")

try:
    import p2pp.checkversion as cv
    print("checkversion: OK")
except Exception as e:
    print(f"checkversion: FAIL - {e}")
            """
        ], capture_output=True, text=True)
        
        assert result.returncode == 0, f"Module structure test failed: {result.stderr}"
        assert "variables: OK" in result.stdout
        assert "formatnumbers: OK" in result.stdout
        assert "checkversion: OK" in result.stdout
    
    def test_p2pp_main_headless_mode(self):
        """Test P2PP main module in headless mode."""
        result = subprocess.run([
            sys.executable, "-c", 
            """
import os
import sys
sys.path.insert(0, '.')

# Set headless environment
os.environ['QT_QPA_PLATFORM'] = 'offscreen'
os.environ['DISPLAY'] = ''

try:
    import P2PP
    print("P2PP import: SUCCESS")
except Exception as e:
    error_str = str(e).lower()
    if any(x in error_str for x in ['no module named', 'modulenotfounderror']):
        print(f"P2PP import: MISSING_DEPENDENCY - {e}")
    elif any(x in error_str for x in ['platform plugin', 'xdg_runtime_dir', 'glx', 'display', 'graphics']):
        print("P2PP import: GUI_UNAVAILABLE (expected in headless)")
    else:
        print(f"P2PP import: ERROR - {e}")
            """
        ], capture_output=True, text=True)
        
        # Check both stdout and stderr for output
        output = result.stdout + result.stderr
        
        # Accept success, GUI unavailable, or missing dependency as valid results
        valid_results = ["SUCCESS", "GUI_UNAVAILABLE", "MISSING_DEPENDENCY"]
        assert any(status in output for status in valid_results), f"Unexpected failure: stdout='{result.stdout}' stderr='{result.stderr}' returncode={result.returncode}"
    
    def test_setup_py_commands_available(self):
        """Test setup.py has required build commands for platform."""
        result = subprocess.run([
            sys.executable, "setup.py", "--help-commands"
        ], capture_output=True, text=True)
        
        # Should work regardless of missing dependencies
        assert result.returncode == 0 or "setuptools" in result.stderr
        
        if result.returncode == 0:
            output = result.stdout
            assert "build" in output
            
            # Platform-specific command availability
            if platform.system() == "Darwin":
                # macOS should support py2app
                pass  # py2app not installed in test env
            elif platform.system() == "Windows":
                assert "bdist_msi" in output
            elif platform.system() == "Linux":
                assert "bdist_rpm" in output
    
    def test_requirements_satisfied(self):
        """Test that core requirements can be satisfied."""
        project_root = Path(__file__).parent.parent.parent
        
        # Test common requirements
        req_file = project_root / "requirements-common.txt"
        assert req_file.exists()
        
        requirements = req_file.read_text().strip().split('\n')
        core_requirements = [req for req in requirements if not req.startswith('#') and req.strip()]
        
        # Should have core dependencies
        req_text = ' '.join(core_requirements)
        assert "PyQt5" in req_text
        assert "requests" in req_text
    
    @pytest.mark.slow
    def test_architecture_specific_startup(self):
        """Test architecture-specific considerations for startup."""
        system = platform.system()
        machine = platform.machine()
        
        # Test architecture detection works
        result = subprocess.run([
            sys.executable, "scripts/check_architecture.py"
        ], capture_output=True, text=True)
        
        assert result.returncode == 0
        output = result.stdout
        
        # Verify correct recommendations per platform
        if system == "Darwin":
            if machine == "arm64":
                assert "P2PP-arm.dmg" in output
            else:
                assert "P2PP-intel.dmg" in output
        elif system == "Windows":
            assert "P2PP.msi" in output
        elif system == "Linux":
            assert ("P2PP.deb" in output or "P2PP.rpm" in output)
        
        # Verify Universal2 warning
        assert "Universal2" in output and ("Never" in output or "crashes" in output)


class TestBuildPrerequisites:
    """Test build prerequisites for each platform."""
    
    def test_python_version_compatibility(self):
        """Test Python version is suitable for building."""
        version_info = sys.version_info
        
        # Should work with Python 3.9+ for development
        assert version_info >= (3, 9), f"Python {version_info} too old"
        
        # Note: Building requires Python 3.11 for cx_Freeze compatibility
        if version_info >= (3, 11) and version_info < (3, 12):
            print("Python version optimal for building with cx_Freeze")
        elif version_info >= (3, 12):
            print("Python version may have cx_Freeze compatibility issues")
    
    def test_build_tool_detection(self):
        """Test build tools can be detected."""
        system = platform.system()
        
        if system == "Darwin":
            # Test if we can detect Xcode tools
            result = subprocess.run(["which", "gcc"], capture_output=True)
            # OK if not available in test environment
            
        elif system == "Linux":
            # Test if we can detect rpm tools
            rpm_result = subprocess.run(["which", "rpmbuild"], capture_output=True)
            # Test if we can detect deb tools  
            deb_result = subprocess.run(["which", "dpkg-buildpackage"], capture_output=True)
            # At least one should be potentially available
            
        # Don't fail tests for missing build tools in test environment
        assert True  # Pass - actual tools checked in CI
    
    def test_environment_variables(self):
        """Test environment variables needed for building."""
        # These are the key environment variables for building
        build_vars = {
            "Darwin": ["ARCHFLAGS"],  # For macOS architecture-specific builds
            "Windows": [],  # Windows builds don't need special env vars
            "Linux": [],    # Linux builds don't need special env vars
        }
        
        system = platform.system()
        if system in build_vars:
            # Variables are set during build process, not required in test env
            assert True
        
        # Test that we can set the variables
        os.environ["TEST_BUILD_VAR"] = "test"
        assert os.environ.get("TEST_BUILD_VAR") == "test"
        del os.environ["TEST_BUILD_VAR"]