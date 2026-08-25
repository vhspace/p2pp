# Live end-to-end testing research — p2pp with real slicers

**Date:** 2026-08-25
**Issue:** Epic for live p2pp testing with PrusaSlicer + OrcaSlicer

## Problem

p2pp has unit tests and CI builds, but no end-to-end validation that post-processed G-code is correct for real printers. We need to run p2pp against real slicer output and validate the result.

## Proposed pipeline

```
PrusaSlicer/OrcaSlicer (VM/container)
  → slice test model (multi-color)
  → capture G-code
  → run p2pp post-processing
  → validate output (lint/simulator)
  → report pass/fail
```

## 1. Slicer setup

### PrusaSlicer
- **Headless mode**: `prusa-slicer --export-gcode --load config.ini model.stl` — runs without display on Linux
- **Container**: `prusa3d/prusa-slicer` Docker image or build from source
- **Config**: Need a Palette 2/3 printer profile (`.ini`) with correct post-processing script path pointing to p2pp
- **CI**: Can run in GitHub Actions `ubuntu-latest` with Xvfb for any GUI-dependent operations

### OrcaSlicer
- **Headless**: OrcaSlicer supports `--slice` CLI mode similar to PrusaSlicer
- **Palette support**: OrcaSlicer has built-in Palette 2/3 support via printer profiles
- **Container**: No official Docker image; would need to build or use AppImage in a container
- **Compatibility**: OrcaSlicer generates G-code in the same format as PrusaSlicer for Palette printers — p2pp should work with minimal changes

## 2. Test models

| Model | Purpose | Complexity |
|-------|---------|------------|
| 2-color cube | Minimal smoke test | Low |
| 4-color calibration tower | Purge + tool changes | Medium |
| Multi-material benchy | Full feature exercise | High |

## 3. Validation approaches

### Option A: G-code lint (recommended first step)
Parse the p2pp output and check for:
- O22 header present with correct printer profile
- P3 metafile structure valid
- Ping/pong sequences present and correctly spaced
- No temperature violations (temp drops below minimum)
- Tool changes match expected sequence
- Purge tower present and correctly sized

### Option B: G-code simulator
Replay the toolpath in a simulator (e.g., gcode-simulator or custom):
- Verify no collisions
- Verify extrusion amounts are positive
- Verify tool changes happen at correct Z heights
- Estimate print time and material usage

### Option C: Golden output diff
- Slice a known model with known-good p2pp output
- Diff new output against golden (allowing for timestamp/version differences)
- Flag any unexpected changes

## 4. CI integration

```yaml
live-test:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - name: Install PrusaSlicer
      run: |
        # Download PrusaSlicer AppImage or use Docker
    - name: Slice test model
      run: |
        prusa-slicer --export-gcode --load profiles/palette3.ini models/2color-cube.stl
    - name: Run p2pp
      run: |
        python3 P2PP.py output.gcode
    - name: Validate output
      run: |
        python3 tests/lint_gcode.py output.p2pp.gcode
```

## 5. Platform matrix

| Platform | Slicer | Status |
|----------|--------|--------|
| Linux (Ubuntu) | PrusaSlicer | CI-ready |
| Linux (Ubuntu) | OrcaSlicer | Needs container/AppImage |
| macOS | PrusaSlicer | Local dev |
| macOS | OrcaSlicer | Local dev |
| Windows | PrusaSlicer | VM/container |
| Windows | OrcaSlicer | VM/container |

## Sub-issues

1. **VM/container setup**: Docker image with PrusaSlicer + p2pp + test models
2. **Printer profiles**: Palette 2/3 profiles for PrusaSlicer and OrcaSlicer
3. **G-code capture**: Script to slice test models and capture output
4. **Lint validator**: G-code lint for Palette-specific markers
5. **CI workflow**: GitHub Actions job running the full pipeline
6. **OrcaSlicer support**: Verify OrcaSlicer G-code compatibility with p2pp
7. **Golden outputs**: Establish baseline outputs for regression testing

## References

- PrusaSlicer CLI: https://github.com/prusa3d/PrusaSlicer/wiki/Command-Line-Interface
- OrcaSlicer releases: https://github.com/SoftFever/OrcaSlicer/releases
- G-code specification: https://reprap.org/wiki/G-code
- Palette 2/3 G-code format: https://www.mosaicmfg.com/pages/palette-2
