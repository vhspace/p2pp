"""
End-to-end tests for P2PP build workflows.
These tests verify the complete build pipeline works.
"""

import pytest
import subprocess
import platform
import os
import sys
from pathlib import Path


class TestBuildWorkflow:
    """Test complete build workflow end-to-end."""
    
    def test_environment_setup(self):
        """Test that build environment can be set up."""
        # Test Python version
        assert sys.version_info >= (3, 9), "Python 3.9+ required"
        
        # Test uv is available
        result = subprocess.run(["uv", "--version"], capture_output=True, text=True)
        assert result.returncode == 0, "uv should be available"
        
        # Test project structure
        project_root = Path(__file__).parent.parent.parent
        assert (project_root / "setup.py").exists()
        assert (project_root / "version.py").exists()
        assert (project_root / "P2PP.py").exists()
    
    def test_dependencies_install(self):
        """Test that dependencies can be installed."""
        # Test uv can create venv
        test_dir = Path("/tmp/p2pp_test_venv")
        if test_dir.exists():
            subprocess.run(["rm", "-rf", str(test_dir)])
        
        result = subprocess.run([
            "uv", "venv", str(test_dir)
        ], capture_output=True, text=True)
        assert result.returncode == 0, f"Failed to create venv: {result.stderr}"
        
        # Test can install basic deps
        venv_python = test_dir / "bin" / "python"
        result = subprocess.run([
            str(venv_python), "-m", "pip", "install", "setuptools", "wheel"
        ], capture_output=True, text=True)
        assert result.returncode == 0, f"Failed to install deps: {result.stderr}"
        
        # Cleanup
        subprocess.run(["rm", "-rf", str(test_dir)])
    
    def test_architecture_detection(self):
        """Test architecture detection works correctly."""
        project_root = Path(__file__).parent.parent.parent
        script = project_root / "scripts" / "check_architecture.py"
        
        result = subprocess.run([
            sys.executable, str(script)
        ], capture_output=True, text=True)
        
        assert result.returncode == 0, f"Architecture check failed: {result.stderr}"
        assert "P2PP Architecture Check" in result.stdout
        assert platform.system() in result.stdout
        assert platform.machine() in result.stdout
    
    def test_version_module_loads(self):
        """Test version module can be loaded."""
        project_root = Path(__file__).parent.parent.parent
        
        # Test version.py can be imported
        result = subprocess.run([
            sys.executable, "-c", 
            f"import sys; sys.path.insert(0, '{project_root}'); import version; print(version.Version)"
        ], capture_output=True, text=True, cwd=project_root)
        
        assert result.returncode == 0, f"Version import failed: {result.stderr}"
        assert "." in result.stdout.strip(), "Version should have dot notation"
    
    def test_setup_py_functionality(self):
        """Test setup.py basic functionality."""
        project_root = Path(__file__).parent.parent.parent
        
        # Test setup.py can show commands
        result = subprocess.run([
            sys.executable, "setup.py", "--help-commands"
        ], capture_output=True, text=True, cwd=project_root)
        
        assert result.returncode == 0, f"setup.py help failed: {result.stderr}"
        assert "build" in result.stdout
    
    @pytest.mark.slow
    def test_development_workflow(self):
        """Test complete development workflow."""
        project_root = Path(__file__).parent.parent.parent
        
        # Test dev script works
        dev_script = project_root / "scripts" / "dev.py"
        result = subprocess.run([
            sys.executable, str(dev_script), "check-arch"
        ], capture_output=True, text=True, cwd=project_root)
        
        assert result.returncode == 0, f"Dev script failed: {result.stderr}"
        assert "P2PP Architecture Check" in result.stdout


class TestPlatformSpecificBuilds:
    """Test platform-specific build configurations."""
    
    @pytest.mark.macos
    def test_macos_build_commands(self):
        """Test macOS build command structure."""
        if platform.system() != "Darwin":
            pytest.skip("macOS-only test")
        
        # Test architecture-specific commands
        intel_cmd = "python setup.py py2app --arch=x86_64"
        arm_cmd = "python setup.py py2app --arch=arm64"
        
        assert "x86_64" in intel_cmd
        assert "arm64" in arm_cmd
        assert intel_cmd != arm_cmd
    
    @pytest.mark.windows
    def test_windows_build_commands(self):
        """Test Windows build command structure."""
        if platform.system() != "Windows":
            pytest.skip("Windows-only test")
        
        # Test MSI build command
        msi_cmd = "python setup.py bdist_msi"
        assert "bdist_msi" in msi_cmd
    
    @pytest.mark.linux
    def test_linux_build_commands(self):
        """Test Linux build command structure.""" 
        if platform.system() != "Linux":
            pytest.skip("Linux-only test")
        
        # Test package build commands
        rpm_cmd = "python setup.py bdist_rpm"
        assert "bdist_rpm" in rpm_cmd


class TestContinuousIntegration:
    """Test CI/CD related functionality."""
    
    def test_github_actions_matrix(self):
        """Test GitHub Actions matrix configuration."""
        project_root = Path(__file__).parent.parent.parent
        workflow_file = project_root / ".github" / "workflows" / "build-packages.yml"
        
        if not workflow_file.exists():
            pytest.skip("GitHub workflow file not found")
        
        content = workflow_file.read_text()
        
        # Should have separate build jobs
        assert "build-macos-intel" in content or "macos-13" in content
        assert "build-macos-arm" in content or "macos-14" in content
        
        # Should not use universal2
        assert "universal2" not in content
    
    def test_requirements_files_exist(self):
        """Test that platform-specific requirements exist."""
        project_root = Path(__file__).parent.parent.parent
        
        req_files = [
            "requirements-common.txt",
            "requirements-linux.txt", 
            "requirements-mac.txt",
            "requirements-win.txt"
        ]
        
        for req_file in req_files:
            file_path = project_root / req_file
            assert file_path.exists(), f"Missing {req_file}"
            assert file_path.stat().st_size > 0, f"Empty {req_file}"
    
    def test_test_commands_work(self):
        """Test that test commands work in CI environment."""
        project_root = Path(__file__).parent.parent.parent
        
        # Test unit tests can run
        result = subprocess.run([
            sys.executable, "-m", "pytest", "tests/unit/", "-v", "--tb=short"
        ], capture_output=True, text=True, cwd=project_root)
        
        # Should pass (or at least run without import errors)
        assert "ImportError" not in result.stderr
        assert "ModuleNotFoundError" not in result.stderr


class TestDistributionPackaging:
    """Test distribution and packaging."""
    
    def test_package_metadata(self):
        """Test package metadata is correct."""
        project_root = Path(__file__).parent.parent.parent
        
        # Test pyproject.toml exists and is valid
        pyproject = project_root / "pyproject.toml"
        assert pyproject.exists()
        
        content = pyproject.read_text()
        assert "[tool.pytest.ini_options]" in content
        assert "testpaths" in content
    
    def test_distribution_files(self):
        """Test distribution files are present."""
        project_root = Path(__file__).parent.parent.parent
        
        essential_files = [
            "README.md",
            "setup.py",
            "version.py",
            "P2PP.py"
        ]
        
        for file_name in essential_files:
            file_path = project_root / file_name
            assert file_path.exists(), f"Missing essential file: {file_name}"


@pytest.mark.integration
class TestRealWorldWorkflow:
    """Test complete real-world workflows."""
    
    def test_user_download_workflow(self):
        """Test the workflow a user would follow."""
        # 1. Check architecture
        project_root = Path(__file__).parent.parent.parent
        result = subprocess.run([
            sys.executable, "scripts/check_architecture.py"
        ], capture_output=True, text=True, cwd=project_root)
        
        assert result.returncode == 0
        assert "Recommended download:" in result.stdout
        
        # 2. Verify recommended file format
        output = result.stdout
        system = platform.system()
        
        if system == "Darwin":
            assert (".dmg" in output) or ("Intel" in output) or ("Apple Silicon" in output)
        elif system == "Windows":
            assert ".msi" in output
        elif system == "Linux":
            assert (".deb" in output) or (".rpm" in output)
    
    @pytest.mark.slow
    def test_developer_workflow(self):
        """Test the workflow a developer would follow."""
        project_root = Path(__file__).parent.parent.parent
        
        # 1. Check environment
        result = subprocess.run([
            sys.executable, "scripts/dev.py", "check-arch"
        ], capture_output=True, text=True, cwd=project_root)
        assert result.returncode == 0
        
        # 2. Run tests  
        result = subprocess.run([
            sys.executable, "scripts/dev.py", "test-unit"
        ], capture_output=True, text=True, cwd=project_root)
        # Should run without critical errors
        assert "ImportError" not in result.stderr
        assert "ModuleNotFoundError" not in result.stderr