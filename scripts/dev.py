#!/usr/bin/env python3
"""
P2PP Development Script
"""

import subprocess
import sys
import os


def run_cmd(cmd, desc=""):
    """Run command and return success status."""
    print(f"Running: {desc or cmd}")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        if e.stderr:
            print(f"stderr: {e.stderr}")
        return False


def check_venv():
    """Ensure virtual environment is active."""
    if not os.environ.get("VIRTUAL_ENV"):
        print("Virtual environment not activated.")
        print("Run: source .venv/bin/activate")
        return False
    return True


COMMANDS = {
    "test": ("python3 -m pytest tests/ -v", "All tests"),
    "test-unit": ("python3 -m pytest tests/unit/ -v", "Unit tests"),
    "test-e2e": ("python3 -m pytest tests/e2e/ -v", "End-to-end tests"),
    "test-e2e-fast": ("python3 -m pytest tests/e2e/ -v -k 'not slow'", "Fast e2e tests"),
    "format": ("black .", "Format code"),
    "check-format": ("black --check --diff .", "Check formatting"),
    "sort-imports": ("isort .", "Sort imports"),
    "check-arch": ("python3 scripts/check_architecture.py", "Check architecture"),
}


def run_all():
    """Run comprehensive checks."""
    if not check_venv():
        return
    
    checks = [
        ("python3 scripts/check_architecture.py", "Architecture check"),
        ("black --check --diff .", "Format check"),
        ("isort --check-only .", "Import check"),
        ("python3 -m pytest tests/unit/ -v", "Unit tests"),
        ("python3 -m pytest tests/e2e/ -v -k 'not slow'", "Fast e2e tests"),
    ]
    
    success = all(run_cmd(cmd, desc) for cmd, desc in checks)
    print("All checks passed!" if success else "Some checks failed.")


def main():
    """Main CLI."""
    if len(sys.argv) < 2:
        print("P2PP Development Script")
        print("Usage: python3 scripts/dev.py <command>")
        print("\nCommands:")
        for cmd, (_, desc) in COMMANDS.items():
            print(f"  {cmd:<15} - {desc}")
        print(f"  {'all':<15} - Run all checks")
        return
    
    command = sys.argv[1]
    
    if command in COMMANDS:
        cmd, desc = COMMANDS[command]
        if check_venv():
            run_cmd(cmd, desc)
    elif command == "all":
        run_all()
    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()