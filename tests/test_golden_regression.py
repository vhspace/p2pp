#!/usr/bin/env python3
"""
Golden output regression tests for p2pp.

Compares processed G-code output against stored golden baselines.
Run with --update-golden to regenerate baselines after intentional changes.
"""

import os
import sys
import argparse
import tempfile
import shutil
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock GUI modules so p2pp can be imported headless (no Qt/image_rc needed)
import types
for _mod_name in ("image_rc", "p2pp.gui"):
    if _mod_name not in sys.modules:
        _mock = types.ModuleType(_mod_name)
        _mock.create_logitem = lambda *a, **kw: None
        _mock.create_erroritem = lambda *a, **kw: None
        _mock.show_infobox = lambda *a, **kw: None
        _mock.dialog_insert_rows = lambda *a, **kw: []
        _mock.QMessageBox = lambda *a, **kw: None
        sys.modules[_mod_name] = _mock

try:
    from p2pp.mcf import p2pp_process_file
    P2PP_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    P2PP_AVAILABLE = False
    print("WARNING: p2pp dependencies not installed — golden tests will be skipped")


TEST_INPUTS_DIR = Path(__file__).parent / "test_inputs"
GOLDEN_DIR = Path(__file__).parent / "golden"

TEST_CASES = [
    "single_color_cube.gcode",
    "two_color_logo.gcode",
    "four_color_complex.gcode",
    "large_file_stress.gcode",
]


def run_p2pp_on_input(input_path, output_path):
    """Run p2pp on input file, capture output."""
    # Reset global state between runs
    import p2pp.variables as v
    v.__dict__.clear()
    # Re-initialize defaults by reimporting
    import importlib
    import p2pp.variables
    importlib.reload(p2pp.variables)
    
    p2pp_process_file(str(input_path), str(output_path))
    
    with open(output_path, 'r') as f:
        return f.read()


def normalize_output(output):
    """Normalize output for comparison (remove timestamps, versions, etc.)."""
    lines = output.splitlines()
    normalized = []
    for line in lines:
        # Skip version lines that change every release
        if line.startswith(";--------- THIS CODE HAS BEEN PROCESSED BY P2PP v"):
            continue
        if "Version Check:" in line:
            continue
        if line.startswith("; P2PP") and "processtime" in line.lower():
            continue
        normalized.append(line)
    return "\n".join(normalized)


def test_golden_output(update_golden=False):
    """Run golden regression tests."""
    if not P2PP_AVAILABLE:
        print("SKIP: p2pp not importable — install requirements-common.txt to run golden tests")
        return True  # don't fail CI when deps are missing

    if not TEST_INPUTS_DIR.exists():
        print(f"ERROR: Test inputs directory not found: {TEST_INPUTS_DIR}")
        return False
    
    GOLDEN_DIR.mkdir(parents=True, exist_ok=True)
    
    all_passed = True
    
    for test_case in TEST_CASES:
        input_path = TEST_INPUTS_DIR / test_case
        golden_path = GOLDEN_DIR / test_case
        
        if not input_path.exists():
            print(f"SKIP: Test input not found: {input_path}")
            continue
        
        print(f"Testing: {test_case}")
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.gcode', delete=False) as tmp:
            tmp_output = tmp.name
        
        try:
            output = run_p2pp_on_input(input_path, tmp_output)
            normalized_output = normalize_output(output)
            
            if update_golden:
                with open(golden_path, 'w') as f:
                    f.write(normalized_output)
                print(f"  UPDATED golden: {golden_path}")
            else:
                if not golden_path.exists():
                    print(f"  FAIL: Golden baseline missing: {golden_path}")
                    print(f"  Run with --update-golden to create it")
                    all_passed = False
                else:
                    with open(golden_path, 'r') as f:
                        golden = f.read()
                    
                    if normalized_output == golden:
                        print(f"  PASS")
                    else:
                        print(f"  FAIL: Output differs from golden")
                        # Show diff
                        import difflib
                        diff = difflib.unified_diff(
                            golden.splitlines(keepends=True),
                            normalized_output.splitlines(keepends=True),
                            fromfile='golden',
                            tofile='actual'
                        )
                        sys.stdout.writelines(list(diff)[:50])
                        all_passed = False
        
        finally:
            if os.path.exists(tmp_output):
                os.unlink(tmp_output)
    
    return all_passed


def main():
    parser = argparse.ArgumentParser(description="Golden output regression tests")
    parser.add_argument("--update-golden", action="store_true",
                        help="Update golden baselines with current output")
    args = parser.parse_args()
    
    success = test_golden_output(update_golden=args.update_golden)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()