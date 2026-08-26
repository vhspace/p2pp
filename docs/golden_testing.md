# Golden Output Regression Testing

This document describes the golden output testing framework for p2pp.

## Overview

Golden tests ensure that p2pp's G-code output remains consistent across changes.
Test inputs are stored in `tests/test_inputs/` and expected outputs in `tests/golden/`.

## Running Tests

```bash
# Run regression tests (compare against golden baselines)
python -m tests.test_golden_regression

# Update golden baselines after intentional changes
python -m tests.test_golden_regression --update-golden
```

## Test Cases

| Test File | Description |
|-----------|-------------|
| `single_color_cube.gcode` | Simple single-color cube |
| `two_color_logo.gcode` | 2-color logo with tool changes |
| `four_color_complex.gcode` | 4-color complex part with many transitions |
| `large_file_stress.gcode` | Large file for performance/stress testing |

## Updating Golden Outputs

**Only update golden outputs when changes are intentional.**

1. Make your code changes
2. Verify the new output is correct manually
3. Run: `python -m tests.test_golden_regression --update-golden`
4. Review the diff in `tests/golden/` before committing
5. Commit both code changes and updated golden files

## Adding New Test Cases

1. Add a new `.gcode` file to `tests/test_inputs/`
2. Add the filename to `TEST_CASES` in `test_golden_regression.py`
3. Run with `--update-golden` to create the baseline
4. Commit both the input and golden output