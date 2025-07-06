"""
Pytest configuration and shared fixtures for P2PP tests.
"""

import os
import platform
import tempfile
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Generator, Dict, Any, Union, Optional

# Ensure we can import from the project root
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import pytest and related modules
# Note: These may not be available until pytest is installed
import pytest  # type: ignore
from unittest.mock import Mock, patch

# Test markers for different categories
pytest_plugins = ["pytestqt"]


@pytest.fixture(scope="session")
def project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def system_info() -> Dict[str, Union[str, bool]]:
    """Get system information for architecture-specific tests."""
    return {
        "system": platform.system(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "architecture": "arm64" if platform.machine() == "arm64" else "x86_64",
        "is_macos": platform.system() == "Darwin",
        "is_windows": platform.system() == "Windows", 
        "is_linux": platform.system() == "Linux",
    }


@pytest.fixture
def temp_workspace() -> Generator[Path, None, None]:
    """Create a temporary workspace for build tests."""
    with tempfile.TemporaryDirectory() as temp_dir:
        workspace = Path(temp_dir)
        yield workspace


@pytest.fixture
def mock_build_environment(temp_workspace: Path, project_root: Path) -> Path:
    """Set up a mock build environment with necessary files."""
    # Copy essential files to temp workspace
    essential_files = [
        "setup.py",
        "pyproject.toml", 
        "version.py",
        "P2PP.py",
        "p2pp.ui",
        "p2ppconf.ui",
        "SendError.ui",
        "p3browser.ui",
    ]
    
    for file_name in essential_files:
        src = project_root / file_name
        if src.exists():
            shutil.copy2(src, temp_workspace / file_name)
    
    # Copy icons directory if it exists
    icons_dir = project_root / "icons"
    if icons_dir.exists():
        shutil.copytree(icons_dir, temp_workspace / "icons")
    
    return temp_workspace


@pytest.fixture
def mock_qt_application() -> Generator[Mock, None, None]:
    """Mock Qt application for GUI tests."""
    with patch('PyQt5.QtWidgets.QApplication') as mock_app:
        mock_instance = Mock()
        mock_app.instance.return_value = None
        mock_app.return_value = mock_instance
        yield mock_app


@pytest.fixture
def architecture_test_matrix(system_info: Dict[str, Union[str, bool]]) -> list[str]:
    """Provide test matrix for architecture-specific testing."""
    if system_info["is_macos"]:
        # macOS can test both architectures (cross-compilation)
        return ["x86_64", "arm64"]
    else:
        # Other platforms test native architecture only
        return [str(system_info["architecture"])]


@pytest.fixture
def build_commands(system_info: Dict[str, Union[str, bool]]) -> Dict[str, str]:
    """Get build commands for the current platform."""
    commands = {}
    
    if system_info["is_macos"]:
        commands.update({
            "build_intel": "python setup.py py2app --arch=x86_64",
            "build_arm": "python setup.py py2app --arch=arm64",
            "clean": "rm -rf build dist",
        })
    elif system_info["is_windows"]:
        commands.update({
            "build": "python setup.py bdist_msi",
            "clean": "rmdir /s /q build dist",
        })
    elif system_info["is_linux"]:
        commands.update({
            "build_rpm": "python setup.py bdist_rpm",
            "build_deb": "python setup.py sdist",
            "clean": "rm -rf build dist",
        })
    
    return commands


@pytest.fixture
def mock_subprocess() -> Generator[Mock, None, None]:
    """Mock subprocess for testing build commands without actually running them."""
    with patch('subprocess.run') as mock_run:
        # Default to successful execution
        mock_run.return_value = Mock(
            returncode=0,
            stdout="Mock successful execution",
            stderr="",
        )
        yield mock_run


@pytest.fixture
def skip_gui_tests() -> None:
    """Skip GUI tests if no display is available."""
    if os.environ.get("CI") and not os.environ.get("DISPLAY"):
        pytest.skip("GUI tests require display")


@pytest.fixture
def sample_gcode_file(temp_workspace: Path) -> Path:
    """Create a sample G-code file for testing."""
    gcode_content = """
; P2PP Test G-code file
G28 ; Home all axes
G1 Z0.2 F3000 ; Move to first layer height
G1 X10 Y10 F1500 ; Move to start position
G1 E5 F300 ; Extrude some filament
G1 X50 Y10 E2 F900 ; Draw line
M104 S0 ; Turn off extruder
M140 S0 ; Turn off bed
M84 ; Disable motors
"""
    
    gcode_file = temp_workspace / "test_print.gcode"
    gcode_file.write_text(gcode_content.strip())
    return gcode_file


@pytest.fixture
def sample_config_file(temp_workspace: Path) -> Path:
    """Create a sample P2PP configuration file for testing."""
    config_content = """
[printer]
type = prusa_mk3s
palette_type = 2
bed_size_x = 250
bed_size_y = 210

[processing]
enable_optimization = true
purge_length = 150
minimum_splice_length = 70

[output]
output_directory = ./output
create_backup = true
"""
    
    config_file = temp_workspace / "p2pp_config.ini"
    config_file.write_text(config_content.strip())
    return config_file


def run_command_with_timeout(cmd: str, cwd: Optional[Path] = None, timeout: int = 30) -> tuple[bool, str, str]:
    """
    Helper function to run commands with timeout for integration tests.
    
    Args:
        cmd: Command to run
        cwd: Working directory
        timeout: Timeout in seconds
        
    Returns:
        Tuple of (success, stdout, stderr)
    """
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=str(cwd) if cwd else None,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)


@pytest.fixture
def command_runner():
    """Provide the command runner helper for integration tests."""
    return run_command_with_timeout


# Custom markers for test categories
def pytest_configure(config) -> None:
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "unit: Unit tests for individual components")
    config.addinivalue_line("markers", "integration: Integration tests for system components")
    config.addinivalue_line("markers", "e2e: End-to-end tests for complete workflows")
    config.addinivalue_line("markers", "gui: Tests that require GUI components")
    config.addinivalue_line("markers", "build: Tests that involve the build system")
    config.addinivalue_line("markers", "slow: Tests that take longer to run")
    config.addinivalue_line("markers", "macos: macOS-specific tests")
    config.addinivalue_line("markers", "windows: Windows-specific tests")
    config.addinivalue_line("markers", "linux: Linux-specific tests")
    config.addinivalue_line("markers", "intel: Intel architecture tests")
    config.addinivalue_line("markers", "arm: ARM architecture tests")


def pytest_collection_modifyitems(config, items) -> None:
    """Modify test collection to handle platform-specific tests."""
    system = platform.system()
    arch = platform.machine()
    
    for item in items:
        # Skip platform-specific tests on wrong platform
        if "macos" in item.keywords and system != "Darwin":
            item.add_marker(pytest.mark.skip(reason="macOS-only test"))
        elif "windows" in item.keywords and system != "Windows":
            item.add_marker(pytest.mark.skip(reason="Windows-only test"))
        elif "linux" in item.keywords and system != "Linux":
            item.add_marker(pytest.mark.skip(reason="Linux-only test"))
        
        # Skip architecture-specific tests on wrong architecture
        if "intel" in item.keywords and arch != "x86_64":
            item.add_marker(pytest.mark.skip(reason="Intel-only test"))
        elif "arm" in item.keywords and arch != "arm64":
            item.add_marker(pytest.mark.skip(reason="ARM-only test"))
        
        # Mark slow tests
        if "slow" in item.keywords:
            item.add_marker(pytest.mark.slow)
        
        # Mark GUI tests for potential skipping in headless environments
        if "gui" in item.keywords and os.environ.get("CI") and not os.environ.get("DISPLAY"):
            item.add_marker(pytest.mark.skip(reason="GUI test in headless environment"))