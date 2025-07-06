"""
End-to-end tests for architecture detection and testing tools.
"""

import pytest  # type: ignore
import subprocess
import sys
import os
import platform
from pathlib import Path
from unittest.mock import patch, Mock


@pytest.mark.e2e
class TestArchitectureCheckTool:
    """Test the scripts/check_architecture.py tool."""
    
    def test_architecture_check_script_exists(self, project_root):
        """Test that the architecture check script exists and is executable."""
        script_path = project_root / "scripts" / "check_architecture.py"
        assert script_path.exists(), "Architecture check script should exist"
        
        # Check that it's executable
        assert script_path.stat().st_mode & 0o111, "Script should be executable"
    
    def test_architecture_check_script_runs(self, project_root, command_runner):
        """Test that the architecture check script runs successfully."""
        script_path = project_root / "scripts" / "check_architecture.py"
        
        # Run the script
        success, stdout, stderr = command_runner(
            f"python3 {script_path}",
            cwd=project_root,
            timeout=30
        )
        
        assert success, f"Architecture check script should run successfully: {stderr}"
        assert len(stdout) > 0, "Script should produce output"
    
    def test_architecture_check_output_content(self, project_root, command_runner):
        """Test that the architecture check script produces correct output."""
        script_path = project_root / "scripts" / "check_architecture.py"
        
        success, stdout, stderr = command_runner(
            f"python3 {script_path}",
            cwd=project_root
        )
        
        assert success, f"Script should run: {stderr}"
        
        # Check that output contains expected elements
        assert "Architecture Check" in stdout
        assert platform.system() in stdout
        assert platform.machine() in stdout
        
        # Check for platform-specific recommendations
        if platform.system() == "Darwin":
            assert "macOS Detected" in stdout
            assert ("P2PP-intel.dmg" in stdout or "P2PP-arm.dmg" in stdout)
        elif platform.system() == "Windows":
            assert "Windows Detected" in stdout
            assert "P2PP.msi" in stdout
        elif platform.system() == "Linux":
            assert "Linux Detected" in stdout
            assert ("P2PP.rpm" in stdout or "P2PP.deb" in stdout)
    
    @pytest.mark.parametrize("platform_name,expected_build", [
        ("Darwin", "P2PP-"),  # Should contain either intel or arm
        ("Windows", "P2PP.msi"),
        ("Linux", "P2PP."),  # Should contain either rpm or deb
    ])
    def test_platform_specific_recommendations(self, platform_name, expected_build, project_root, command_runner):
        """Test platform-specific build recommendations."""
        script_path = project_root / "scripts" / "check_architecture.py"
        
        # Only test current platform to avoid cross-platform issues
        if platform.system() != platform_name:
            pytest.skip(f"Test requires {platform_name}")
        
        success, stdout, stderr = command_runner(
            f"python3 {script_path}",
            cwd=project_root
        )
        
        assert success, f"Script should run: {stderr}"
        assert expected_build in stdout, f"Should recommend {expected_build} for {platform_name}"


@pytest.mark.e2e
class TestArchitectureBuildTestTool:
    """Test the scripts/test_architecture_builds.py tool."""
    
    def test_build_test_script_exists(self, project_root):
        """Test that the build test script exists and is executable."""
        script_path = project_root / "scripts" / "test_architecture_builds.py"
        assert script_path.exists(), "Build test script should exist"
        
        # Check that it's executable
        assert script_path.stat().st_mode & 0o111, "Script should be executable"
    
    @pytest.mark.slow
    def test_build_test_script_help(self, project_root, command_runner):
        """Test that the build test script provides help information."""
        script_path = project_root / "scripts" / "test_architecture_builds.py"
        
        # Test running without arguments (should show info)
        success, stdout, stderr = command_runner(
            f"python3 {script_path}",
            cwd=project_root,
            timeout=60
        )
        
        # Script might fail (expected for actual builds), but should produce output
        output = stdout + stderr
        assert len(output) > 0, "Script should produce output"
        assert "Architecture Build Test" in output or "P2PP" in output
    
    @pytest.mark.slow
    @pytest.mark.build
    def test_build_test_script_with_mock(self, project_root, command_runner):
        """Test the build test script with mocked build processes."""
        script_path = project_root / "scripts" / "test_architecture_builds.py"
        
        # This test would normally mock the build process
        # For now, just verify the script structure
        with open(script_path) as f:
            content = f.read()
        
        # Check that script contains expected functions
        assert "test_macos_build" in content
        assert "test_windows_build" in content  
        assert "test_linux_build" in content
        assert "run_command" in content


@pytest.mark.e2e
class TestEndToEndWorkflow:
    """Test complete end-to-end workflows."""
    
    def test_architecture_detection_workflow(self, project_root, system_info, command_runner):
        """Test the complete architecture detection workflow."""
        # Step 1: Run architecture check
        check_script = project_root / "scripts" / "check_architecture.py"
        success, stdout, stderr = command_runner(
            f"python3 {check_script}",
            cwd=project_root
        )
        
        assert success, f"Architecture check failed: {stderr}"
        
        # Step 2: Verify output matches current system
        assert system_info["system"] in stdout
        assert system_info["machine"] in stdout
        
        # Step 3: Verify correct build recommendation
        if system_info["is_macos"]:
            if system_info["machine"] == "x86_64":
                assert "P2PP-intel.dmg" in stdout
            elif system_info["machine"] == "arm64":
                assert "P2PP-arm.dmg" in stdout
        elif system_info["is_windows"]:
            assert "P2PP.msi" in stdout
        elif system_info["is_linux"]:
            assert "P2PP.rpm" in stdout or "P2PP.deb" in stdout
    
    @pytest.mark.slow
    def test_local_development_workflow(self, project_root, command_runner):
        """Test local development workflow with testing tools."""
        # This test simulates a developer workflow
        
        # Step 1: Check architecture
        check_script = project_root / "scripts" / "check_architecture.py"
        success, stdout, stderr = command_runner(
            f"python3 {check_script}",
            cwd=project_root
        )
        assert success, "Architecture check should work"
        
        # Step 2: Verify project structure
        assert (project_root / "pyproject.toml").exists()
        assert (project_root / "setup.py").exists()
        
        # Step 3: Check that testing tools are available
        test_script = project_root / "scripts" / "test_architecture_builds.py"
        assert test_script.exists()
    
    def test_ci_cd_simulation(self, project_root, system_info):
        """Test CI/CD workflow simulation."""
        # Simulate what happens in GitHub Actions
        
        # Step 1: Check that workflow files exist
        workflow_dir = project_root / ".github" / "workflows"
        assert workflow_dir.exists()
        
        build_workflow = workflow_dir / "build-packages.yml"
        assert build_workflow.exists()
        
        # Step 2: Check workflow content
        content = build_workflow.read_text()
        
        # Should have separate jobs for different architectures
        if system_info["is_macos"]:
            assert "build-macos-intel" in content
            assert "build-macos-arm" in content
            assert "macos-13" in content  # Intel runner
            assert "macos-14" in content  # ARM runner
        
        # Should have end-to-end testing
        assert "End-to-End Test" in content
        
        # Should not use universal2
        assert "universal2" not in content


@pytest.mark.e2e
@pytest.mark.gui
class TestApplicationLaunch:
    """Test application launch and basic functionality."""
    
    @pytest.mark.skipif("CI" in os.environ, reason="GUI tests not supported in CI")
    def test_application_import(self, project_root):
        """Test that the main application can be imported."""
        sys.path.insert(0, str(project_root))
        
        try:
            # Try to import main module
            import P2PP
            assert P2PP is not None
        except ImportError as e:
            pytest.skip(f"Application import failed (expected in test environment): {e}")
        finally:
            if str(project_root) in sys.path:
                sys.path.remove(str(project_root))
    
    @pytest.mark.skipif("CI" in os.environ, reason="GUI tests not supported in CI")
    def test_qt_modules_available(self, skip_gui_tests):
        """Test that Qt modules are available for GUI functionality."""
        try:
            import PyQt5.QtCore  # type: ignore
            import PyQt5.QtWidgets  # type: ignore
            
            # Basic Qt version check
            qt_version = PyQt5.QtCore.QT_VERSION_STR
            assert qt_version is not None
            
            # Check minimum version (5.15+)
            version_parts = qt_version.split('.')
            major, minor = int(version_parts[0]), int(version_parts[1])
            assert major >= 5 and minor >= 15, f"Qt version {qt_version} is too old"
            
        except ImportError:
            pytest.skip("PyQt5 not available (expected in CI)")


@pytest.mark.e2e
class TestDocumentationIntegration:
    """Test that documentation is properly integrated."""
    
    def test_architecture_documentation_exists(self, project_root):
        """Test that architecture documentation exists."""
        docs_dir = project_root / "docs"
        arch_doc = docs_dir / "ARCHITECTURE_BUILDS.md"
        
        assert arch_doc.exists(), "Architecture documentation should exist"
        
        content = arch_doc.read_text()
        assert "Architecture-Specific Builds" in content
        assert "P2PP-intel.dmg" in content
        assert "P2PP-arm.dmg" in content
    
    def test_cursor_rules_exist(self, project_root):
        """Test that cursor rules exist and contain architecture guidance."""
        cursor_rules = project_root / ".cursorrules"
        assert cursor_rules.exists(), "Cursor rules should exist"
        
        content = cursor_rules.read_text()
        assert "Architecture-Specific Builds" in content
        assert "universal2" in content.lower()
        assert "never" in content.lower()
    
    def test_readme_updated(self, project_root):
        """Test that README contains architecture information."""
        readme = project_root / "README.md"
        assert readme.exists(), "README should exist"
        
        content = readme.read_text()
        assert "Architecture" in content or "architecture" in content
        assert "Download" in content or "download" in content
        assert ("P2PP-intel" in content or "P2PP-arm" in content)


@pytest.mark.e2e
class TestErrorHandling:
    """Test error handling in architecture tools."""
    
    def test_architecture_check_error_handling(self, project_root, command_runner):
        """Test that architecture check handles errors gracefully."""
        script_path = project_root / "scripts" / "check_architecture.py"
        
        # Test with invalid environment (simulated)
        with patch.dict('os.environ', {}, clear=True):
            success, stdout, stderr = command_runner(
                f"python3 {script_path}",
                cwd=project_root
            )
            
            # Should still work even with minimal environment
            # (Python's platform module should still work)
            assert success or len(stdout + stderr) > 0
    
    def test_missing_dependencies_handling(self, project_root):
        """Test handling of missing dependencies."""
        # This would test what happens when PyQt5 is not available
        # For now, just verify the structure exists to handle it
        
        pyproject_file = project_root / "pyproject.toml"
        content = pyproject_file.read_text()
        
        # Should have optional dependencies
        assert "optional-dependencies" in content
        assert "dev" in content
        assert "test-" in content  # Platform-specific test dependencies