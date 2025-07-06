"""
Unit tests for version module and basic application functionality.
"""

import pytest
import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from version import Version, __author__, __email__


@pytest.mark.unit
class TestVersion:
    """Test version information."""
    
    def test_version_format(self):
        """Test that version follows semantic versioning."""
        assert isinstance(Version, str)
        assert len(Version) > 0
        
        # Basic semantic version pattern (x.y.z)
        parts = Version.split('.')
        assert len(parts) >= 2, "Version should have at least major.minor"
        
        # Check that major and minor are numeric
        assert parts[0].isdigit(), "Major version should be numeric"
        assert parts[1].isdigit(), "Minor version should be numeric"
    
    def test_author_info(self):
        """Test that author information is properly defined."""
        assert isinstance(__author__, str)
        assert len(__author__) > 0
        assert __author__ != "Unknown"
    
    def test_email_info(self):
        """Test that email information is properly defined."""
        assert isinstance(__email__, str)
        assert len(__email__) > 0
        assert "@" in __email__
        assert "." in __email__


@pytest.mark.unit
class TestBasicImports:
    """Test that basic imports work correctly."""
    
    def test_version_import(self):
        """Test that version can be imported without errors."""
        import version
        assert hasattr(version, 'Version')
        assert hasattr(version, '__author__')
        assert hasattr(version, '__email__')
    
    def test_main_module_exists(self):
        """Test that main P2PP module exists."""
        p2pp_file = Path(__file__).parent.parent.parent / "P2PP.py"
        assert p2pp_file.exists(), "P2PP.py should exist"
    
    def test_setup_module_exists(self):
        """Test that setup.py exists and is readable."""
        setup_file = Path(__file__).parent.parent.parent / "setup.py"
        assert setup_file.exists(), "setup.py should exist"
        
        # Check that it contains basic setup information
        content = setup_file.read_text()
        assert "setup" in content.lower()
        assert "py2app" in content or "cx_freeze" in content or "setuptools" in content


@pytest.mark.unit
class TestProjectStructure:
    """Test that project structure is correct."""
    
    def test_ui_files_exist(self):
        """Test that UI files exist."""
        project_root = Path(__file__).parent.parent.parent
        
        required_ui_files = [
            "p2pp.ui",
            "p2ppconf.ui", 
            "SendError.ui",
            "p3browser.ui",
        ]
        
        for ui_file in required_ui_files:
            ui_path = project_root / ui_file
            assert ui_path.exists(), f"UI file {ui_file} should exist"
    
    def test_icons_directory_exists(self):
        """Test that icons directory exists."""
        icons_dir = Path(__file__).parent.parent.parent / "icons"
        assert icons_dir.exists(), "Icons directory should exist"
        assert icons_dir.is_dir(), "Icons should be a directory"
    
    def test_config_files_exist(self):
        """Test that configuration files exist."""
        project_root = Path(__file__).parent.parent.parent
        
        # pyproject.toml should exist (new format)
        pyproject_file = project_root / "pyproject.toml"
        assert pyproject_file.exists(), "pyproject.toml should exist"
        
        # Check basic pyproject.toml structure
        content = pyproject_file.read_text()
        assert "[project]" in content
        assert "name" in content
        assert "p2pp" in content.lower()


@pytest.mark.unit
class TestEnvironmentCompatibility:
    """Test environment and dependency compatibility."""
    
    def test_python_version_compatibility(self):
        """Test that Python version is compatible."""
        import sys
        
        # Check minimum Python version (3.8+)
        assert sys.version_info >= (3, 8), "Python 3.8+ is required"
    
    def test_required_modules_available(self):
        """Test that required modules can be imported."""
        # Test core Python modules
        try:
            import os
            import sys
            import platform
            import pathlib
            import configparser
        except ImportError as e:
            pytest.fail(f"Core Python module import failed: {e}")
    
    @pytest.mark.gui
    def test_qt_availability(self):
        """Test that Qt modules are available (when not in headless mode)."""
        try:
            import PyQt5.QtCore
            import PyQt5.QtWidgets
            assert PyQt5.QtCore.QT_VERSION_STR is not None
        except ImportError:
            pytest.skip("PyQt5 not available (expected in CI)")


@pytest.mark.unit
@pytest.mark.parametrize("platform_name", ["Darwin", "Windows", "Linux"])
def test_platform_specific_imports(platform_name):
    """Test that platform-specific functionality can be imported."""
    import platform
    
    current_platform = platform.system()
    
    if current_platform == platform_name:
        # Test platform-specific imports for current platform
        if platform_name == "Darwin":
            # macOS specific
            import subprocess
            import shutil
        elif platform_name == "Windows":
            # Windows specific  
            import subprocess
            import shutil
        elif platform_name == "Linux":
            # Linux specific
            import subprocess
            import shutil
        
        # All platforms should have these
        import tempfile
        import configparser


@pytest.mark.unit
class TestArchitectureDetection:
    """Test architecture detection functionality."""
    
    def test_architecture_detection(self):
        """Test that we can detect the current architecture."""
        import platform
        
        machine = platform.machine()
        assert machine in ["x86_64", "arm64", "AMD64", "i386", "i686"], f"Unknown architecture: {machine}"
    
    def test_platform_detection(self):
        """Test that we can detect the current platform."""
        import platform
        
        system = platform.system()
        assert system in ["Darwin", "Windows", "Linux"], f"Unknown platform: {system}"
    
    def test_cross_compilation_matrix(self, system_info, architecture_test_matrix):
        """Test that architecture test matrix is correct for the platform."""
        if system_info["is_macos"]:
            # macOS should support both architectures
            assert "x86_64" in architecture_test_matrix
            assert "arm64" in architecture_test_matrix
        else:
            # Other platforms should only have their native architecture
            assert len(architecture_test_matrix) == 1
            assert architecture_test_matrix[0] == system_info["architecture"]