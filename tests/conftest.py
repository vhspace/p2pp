"""
Pytest configuration for P2PP tests.
"""

import os
import platform
import tempfile
from pathlib import Path
from typing import Generator, Dict, Union
import pytest

# Ensure we can import from the project root
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))


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
    """Create a temporary workspace for tests."""
    with tempfile.TemporaryDirectory() as temp_dir:
        workspace = Path(temp_dir)
        yield workspace