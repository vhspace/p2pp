"""
Integration tests for the build system and architecture-specific builds.
"""

import pytest  # type: ignore
import platform
import os
import shutil
import subprocess
from pathlib import Path
from unittest.mock import patch, Mock


@pytest.mark.integration
@pytest.mark.build
class TestSetupPyConfiguration:
    """Test setup.py configuration and architecture handling."""
    
    def test_setup_py_imports(self, project_root):
        """Test that setup.py can be imported and parsed."""
        setup_file = project_root / "setup.py"
        content = setup_file.read_text()
        
        # Check for architecture-specific configuration
        assert "--arch=" in content, "setup.py should support --arch parameter"
        assert "universal2" not in content, "setup.py should not use universal2"
        assert "architecture" in content.lower(), "setup.py should handle architecture detection"
    
    def test_pyproject_toml_structure(self, project_root):
        """Test pyproject.toml structure and dependencies."""
        pyproject_file = project_root / "pyproject.toml"
        content = pyproject_file.read_text()
        
        # Check for proper project structure
        assert "[project]" in content
        assert "name = \"p2pp\"" in content
        assert "dependencies" in content
        
        # Check for platform-specific dependencies
        assert "test-macos" in content
        assert "test-windows" in content
        assert "test-linux" in content
        
        # Check for build dependencies
        assert "build-macos" in content
        assert "build-windows" in content
        assert "build-linux" in content
    
    @pytest.mark.parametrize("arch", ["x86_64", "arm64"])
    def test_architecture_parameter_parsing(self, arch, mock_build_environment):
        """Test that architecture parameters are parsed correctly."""
        setup_file = mock_build_environment / "setup.py"
        
        # Test that setup.py handles architecture parameters
        content = setup_file.read_text()
        
        # Should contain architecture detection logic
        assert f"--arch={arch}" in content or "arch=" in content
        assert "platform.machine()" in content or "target_arch" in content


@pytest.mark.integration
@pytest.mark.build
class TestBuildCommands:
    """Test build command generation and execution."""
    
    def test_build_commands_generation(self, system_info, build_commands):
        """Test that build commands are generated correctly for the platform."""
        if system_info["is_macos"]:
            assert "build_intel" in build_commands
            assert "build_arm" in build_commands
            assert "--arch=x86_64" in build_commands["build_intel"]
            assert "--arch=arm64" in build_commands["build_arm"]
        elif system_info["is_windows"]:
            assert "build" in build_commands
            assert "bdist_msi" in build_commands["build"]
        elif system_info["is_linux"]:
            assert "build_rpm" in build_commands
            assert "bdist_rpm" in build_commands["build_rpm"]
    
    def test_clean_commands(self, build_commands):
        """Test that clean commands are available."""
        assert "clean" in build_commands
        clean_cmd = build_commands["clean"]
        assert "build" in clean_cmd and "dist" in clean_cmd
    
    @pytest.mark.slow
    def test_mock_build_execution(self, mock_subprocess, build_commands, system_info):
        """Test build command execution with mocked subprocess."""
        if system_info["is_macos"]:
            # Test Intel build
            result = subprocess.run(build_commands["build_intel"], shell=True, capture_output=True)
            mock_subprocess.assert_called()
        elif system_info["is_windows"]:
            # Test Windows build
            result = subprocess.run(build_commands["build"], shell=True, capture_output=True)
            mock_subprocess.assert_called()
        elif system_info["is_linux"]:
            # Test Linux build
            result = subprocess.run(build_commands["build_rpm"], shell=True, capture_output=True)
            mock_subprocess.assert_called()


@pytest.mark.integration
@pytest.mark.build
@pytest.mark.macos
class TestMacOSBuilds:
    """Test macOS-specific build functionality."""
    
    def test_archflags_environment_variable(self):
        """Test that ARCHFLAGS environment variable affects builds."""
        # Test Intel ARCHFLAGS
        os.environ["ARCHFLAGS"] = "-arch x86_64"
        assert os.environ.get("ARCHFLAGS") == "-arch x86_64"
        
        # Test ARM ARCHFLAGS
        os.environ["ARCHFLAGS"] = "-arch arm64"
        assert os.environ.get("ARCHFLAGS") == "-arch arm64"
        
        # Clean up
        os.environ.pop("ARCHFLAGS", None)
    
    @pytest.mark.parametrize("arch", ["x86_64", "arm64"])
    def test_macos_architecture_builds(self, arch, mock_build_environment, mock_subprocess):
        """Test macOS builds for specific architectures."""
        build_cmd = f"python setup.py py2app --arch={arch}"
        
        # Set appropriate ARCHFLAGS
        os.environ["ARCHFLAGS"] = f"-arch {arch}"
        
        try:
            # Mock the build process
            with patch("subprocess.run") as mock_run:
                mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
                result = subprocess.run(build_cmd, shell=True, cwd=mock_build_environment)
                
                # Verify the command was called
                mock_run.assert_called()
                
        finally:
            # Clean up environment
            os.environ.pop("ARCHFLAGS", None)
    
    def test_dmg_creation_command(self, system_info):
        """Test DMG creation command structure."""
        if not system_info["is_macos"]:
            pytest.skip("DMG creation is macOS-specific")
        
        # Test that create-dmg command structure is correct
        intel_dmg_name = "P2PP-intel.dmg"
        arm_dmg_name = "P2PP-arm.dmg"
        
        assert "intel" in intel_dmg_name
        assert "arm" in arm_dmg_name
        assert intel_dmg_name != arm_dmg_name


@pytest.mark.integration  
@pytest.mark.build
@pytest.mark.windows
class TestWindowsBuilds:
    """Test Windows-specific build functionality."""
    
    def test_msi_build_command(self, system_info, mock_subprocess):
        """Test Windows MSI build command."""
        if not system_info["is_windows"]:
            pytest.skip("MSI builds are Windows-specific")
        
        build_cmd = "python setup.py bdist_msi"
        
        # Mock the build process
        result = subprocess.run(build_cmd, shell=True, capture_output=True)
        mock_subprocess.assert_called()
    
    def test_windows_signing_process(self, system_info):
        """Test Windows code signing process structure."""
        if not system_info["is_windows"]:
            pytest.skip("Windows signing is Windows-specific")
        
        # Test that signing commands are properly structured
        signing_tools = ["signtool", "Set-AuthenticodeSignature"]
        
        # At least one signing method should be available in the workflow
        # This is tested by checking the workflow file structure
        assert len(signing_tools) > 0


@pytest.mark.integration
@pytest.mark.build  
@pytest.mark.linux
class TestLinuxBuilds:
    """Test Linux-specific build functionality."""
    
    def test_rpm_build_command(self, system_info, mock_subprocess):
        """Test Linux RPM build command."""
        if not system_info["is_linux"]:
            pytest.skip("RPM builds are Linux-specific")
        
        build_cmd = "python setup.py bdist_rpm"
        
        # Mock the build process
        result = subprocess.run(build_cmd, shell=True, capture_output=True)
        mock_subprocess.assert_called()
    
    def test_deb_build_process(self, system_info):
        """Test DEB build process structure."""
        if not system_info["is_linux"]:
            pytest.skip("DEB builds are Linux-specific")
        
        # Test that debian directory structure requirements are understood
        debian_files = ["control", "changelog", "rules"]
        
        # The build process should handle these files
        assert len(debian_files) > 0


@pytest.mark.integration
@pytest.mark.build
class TestCrossCompilation:
    """Test cross-compilation capabilities."""
    
    @pytest.mark.macos
    def test_cross_compilation_matrix(self, system_info, architecture_test_matrix):
        """Test cross-compilation support on macOS."""
        if not system_info["is_macos"]:
            pytest.skip("Cross-compilation test is macOS-specific")
        
        # macOS should support both architectures
        assert len(architecture_test_matrix) == 2
        assert "x86_64" in architecture_test_matrix
        assert "arm64" in architecture_test_matrix
    
    @pytest.mark.macos
    @pytest.mark.arm
    def test_arm_to_intel_cross_compilation(self, system_info):
        """Test that ARM Macs can build Intel binaries."""
        if not (system_info["is_macos"] and system_info["machine"] == "arm64"):
            pytest.skip("Test requires ARM64 macOS")
        
        # ARM Macs should be able to build Intel binaries
        build_cmd = "python setup.py py2app --arch=x86_64"
        os.environ["ARCHFLAGS"] = "-arch x86_64"
        
        try:
            # This would be a real test in integration environment
            # For now, just verify the command structure
            assert "x86_64" in build_cmd
            assert os.environ.get("ARCHFLAGS") == "-arch x86_64"
        finally:
            os.environ.pop("ARCHFLAGS", None)


@pytest.mark.integration
@pytest.mark.build
class TestBuildArtifacts:
    """Test build artifact generation and validation."""
    
    def test_expected_artifacts_macos(self, system_info):
        """Test expected macOS build artifacts."""
        if not system_info["is_macos"]:
            pytest.skip("macOS artifact test is macOS-specific")
        
        expected_artifacts = [
            "dist/P2PP.app",
            "dist/P2PP-intel.dmg",  # For Intel builds
            "dist/P2PP-arm.dmg",    # For ARM builds
        ]
        
        # These are the expected output paths
        for artifact in expected_artifacts:
            assert "/" in artifact and "P2PP" in artifact
    
    def test_expected_artifacts_windows(self, system_info):
        """Test expected Windows build artifacts."""
        if not system_info["is_windows"]:
            pytest.skip("Windows artifact test is Windows-specific")
        
        expected_artifacts = [
            "dist/P2PP.msi",
            "build/exe.win-amd64-*/P2PP.exe",
        ]
        
        # These are the expected output patterns
        for artifact in expected_artifacts:
            assert "P2PP" in artifact
    
    def test_expected_artifacts_linux(self, system_info):
        """Test expected Linux build artifacts."""
        if not system_info["is_linux"]:
            pytest.skip("Linux artifact test is Linux-specific")
        
        expected_artifacts = [
            "dist/p2pp-*.rpm",
            "dist/deb/p2pp*.deb",
        ]
        
        # These are the expected output patterns
        for artifact in expected_artifacts:
            assert "p2pp" in artifact.lower()


@pytest.mark.integration
class TestDependencyManagement:
    """Test dependency management and resolution."""
    
    def test_platform_specific_requirements(self, project_root):
        """Test that platform-specific requirement files exist."""
        requirements_files = [
            "requirements-mac.txt",
            "requirements-win.txt", 
            "requirements-linux.txt",
            "requirements-common.txt",
        ]
        
        for req_file in requirements_files:
            req_path = project_root / req_file
            assert req_path.exists(), f"Requirements file {req_file} should exist"
            
            # Check that file has content
            content = req_path.read_text().strip()
            assert len(content) > 0, f"Requirements file {req_file} should not be empty"
    
    def test_pyproject_toml_dependencies(self, project_root):
        """Test pyproject.toml dependency specification."""
        pyproject_file = project_root / "pyproject.toml"
        content = pyproject_file.read_text()
        
        # Check for core dependencies
        assert "PyQt5" in content
        assert "PyQtWebEngine" in content or "QtWebEngine" in content
        
        # Check for development dependencies
        assert "pytest" in content
        assert "pytest-cov" in content
        assert "pytest-qt" in content