"""
Unit tests for P2PP version module and basic functionality.
"""

import pytest
import sys
import os
import platform
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import version


@pytest.mark.unit
class TestVersion:
    """Test version module functionality."""

    def test_version_format(self):
        """Test that version follows semantic versioning."""
        assert hasattr(version, 'Version')
        assert isinstance(version.Version, str)
        
        # Should be in format X.Y.Z
        parts = version.Version.split('.')
        assert len(parts) == 3
        
        # Each part should be numeric
        for part in parts:
            assert part.isdigit() or part.zfill(2).isdigit()

    def test_version_constants(self):
        """Test that version constants are defined."""
        assert hasattr(version, 'MajorVersion')
        assert hasattr(version, 'MinorVersion')
        assert hasattr(version, 'Build')
        
        assert isinstance(version.MajorVersion, int)
        assert isinstance(version.MinorVersion, int)
        assert isinstance(version.Build, int)

    @pytest.mark.unit
    def test_author_info(self):
        """Test that author information is present."""
        assert hasattr(version, '__author__')
        assert hasattr(version, '__email__')
        assert hasattr(version, '__maintainer__')
        
        assert "Tom Van den Eede" in version.__author__
        assert "P2PP@pandora.be" in version.__email__

    @pytest.mark.unit 
    def test_email_info(self):
        """Test email format."""
        assert "@" in version.__email__
        assert "." in version.__email__

    def test_release_info(self):
        """Test release information structure."""
        assert hasattr(version, 'releaseinfo')
        assert isinstance(version.releaseinfo, dict)
        assert len(version.releaseinfo) > 0


@pytest.mark.unit
class TestBasicImports:
    """Test basic module imports."""

    def test_version_import(self):
        """Test version module can be imported."""
        import version
        assert version is not None

    def test_main_module_exists(self):
        """Test main P2PP module exists."""
        main_file = Path(__file__).parent.parent.parent / "P2PP.py"
        assert main_file.exists()

    def test_setup_module_exists(self):
        """Test setup.py exists."""
        setup_file = Path(__file__).parent.parent.parent / "setup.py"
        assert setup_file.exists()


@pytest.mark.unit
class TestProjectStructure:
    """Test project structure."""

    @pytest.mark.gui
    def test_ui_files_exist(self):
        """Test UI files exist."""
        project_root = Path(__file__).parent.parent.parent
        ui_files = [
            "p2pp.ui",
            "p2ppconf.ui", 
            "SendError.ui",
            "p3browser.ui"
        ]
        
        for ui_file in ui_files:
            assert (project_root / ui_file).exists(), f"UI file {ui_file} should exist"

    @pytest.mark.unit
    def test_icons_directory_exists(self):
        """Test icons directory exists."""
        icons_dir = Path(__file__).parent.parent.parent / "icons"
        assert icons_dir.exists()

    @pytest.mark.unit
    def test_config_files_exist(self):
        """Test configuration files exist."""
        project_root = Path(__file__).parent.parent.parent
        config_files = [
            "requirements-common.txt",
            "requirements-linux.txt",
            "requirements-mac.txt",
            "requirements-win.txt"
        ]
        
        for config_file in config_files:
            assert (project_root / config_file).exists(), f"Config file {config_file} should exist"


@pytest.mark.unit
class TestEnvironmentCompatibility:
    """Test environment compatibility."""

    def test_python_version_compatibility(self):
        """Test Python version compatibility."""
        # Should work with Python 3.9+
        assert sys.version_info >= (3, 9)

    def test_required_modules_available(self):
        """Test required modules are available."""
        required_modules = [
            'sys',
            'os',
            'platform',
            'pathlib'
        ]
        
        for module in required_modules:
            try:
                __import__(module)
            except ImportError:
                pytest.fail(f"Required module {module} not available")

    @pytest.mark.gui
    def test_qt_availability(self):
        """Test Qt availability for GUI."""
        try:
            import PyQt5.QtCore
            assert PyQt5.QtCore.QT_VERSION_STR is not None
        except ImportError:
            pytest.skip("PyQt5 not available (expected in test environment)")


@pytest.mark.unit
@pytest.mark.parametrize("platform_name", ["Darwin", "Windows", "Linux"])
def test_platform_specific_imports(platform_name):
    """Test platform-specific imports."""
    # This test verifies the structure exists for different platforms
    assert platform_name in ["Darwin", "Windows", "Linux"]
    
    # Test that platform module works
    current_platform = platform.system()
    assert current_platform in ["Darwin", "Windows", "Linux"]


@pytest.mark.unit
class TestArchitectureDetection:
    """Test architecture detection functionality."""

    def test_architecture_detection(self):
        """Test architecture detection."""
        machine = platform.machine()
        assert machine in ["x86_64", "arm64", "AMD64", "aarch64"]

    def test_platform_detection(self):
        """Test platform detection."""
        system = platform.system()
        assert system in ["Darwin", "Windows", "Linux"]