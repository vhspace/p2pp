#!/usr/bin/env python3
"""
P2PP Development Script
Simple script to run common development tasks.
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(cmd, description=""):
    """Run a command and show output."""
    print(f"Running: {description or cmd}")
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
    """Check if virtual environment is activated."""
    if not os.environ.get("VIRTUAL_ENV"):
        print("Virtual environment not activated.")
        print("Run: source .venv/bin/activate")
        return False
    return True


def main():
    """Main CLI."""
    if len(sys.argv) < 2:
        print("P2PP Development Script")
        print("Usage: python3 scripts/dev.py <command>")
        print("")
        print("Commands:")
        print("  test          - Run tests")
        print("  test-unit     - Run unit tests only")
        print("  format        - Format code with black")
        print("  check-format  - Check formatting without changes")
        print("  sort-imports  - Sort imports with isort")
        print("  check-arch    - Check system architecture")
        print("  all           - Run all checks")
        return
    
    command = sys.argv[1]
    
    if command == "test":
        if check_venv():
            run_command("python3 -m pytest tests/ -v", "Running all tests")
    
    elif command == "test-unit":
        if check_venv():
            run_command("python3 -m pytest tests/unit/ -v", "Running unit tests")
    
    elif command == "format":
        if check_venv():
            run_command("black .", "Formatting code")
    
    elif command == "check-format":
        if check_venv():
            run_command("black --check --diff .", "Checking code formatting")
    
    elif command == "sort-imports":
        if check_venv():
            run_command("isort .", "Sorting imports")
    
    elif command == "check-arch":
        run_command("python3 scripts/check_architecture.py", "Checking system architecture")
    
    elif command == "all":
        if check_venv():
            success = True
            success &= run_command("python3 scripts/check_architecture.py", "Checking architecture")
            success &= run_command("black --check --diff .", "Checking formatting")
            success &= run_command("isort --check-only .", "Checking imports")
            success &= run_command("python3 -m pytest tests/unit/ -v", "Running unit tests")
            
            if success:
                print("All checks passed!")
            else:
                print("Some checks failed.")
    
    else:
        print(f"Unknown command: {command}")
        print("Run without arguments to see available commands.")


if __name__ == "__main__":
    main()