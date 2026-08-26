# Palette Printer Profiles

Printer profiles for PrusaSlicer and OrcaSlicer configured for use with p2pp.

## Installation

### PrusaSlicer
1. Open PrusaSlicer
2. Go to File > Import > Import Config Bundle
3. Select the appropriate `.ini` file from `prusaslicer/`

### OrcaSlicer
1. Open OrcaSlicer
2. Go to File > Import > Import Config(s)
3. Select the appropriate `.ini` file from `orcaslicer/`

## Profiles

| File | Slicer | Palette | P2PP Directives |
|------|--------|---------|-----------------|
| `prusaslicer/Palette2.ini` | PrusaSlicer | Palette 2 | P2PP PALETTE2, ping/splice settings |
| `prusaslicer/Palette3.ini` | PrusaSlicer | Palette 3 | P2PP PALETTE3_PRO, P3 settings, material presets |
| `orcaslicer/Palette2.ini` | OrcaSlicer | Palette 2 | P2PP PALETTE2, ping/splice settings |
| `orcaslicer/Palette3.ini` | OrcaSlicer | Palette 3 | P2PP PALETTE3_PRO, P3 settings, material presets |

## p2pp Directives

Profiles include `;P2PP` directives in the `start_gcode` that configure p2pp behavior:
- `PALETTE3_PRO` / `PALETTE2` — select Palette model
- `LINEARPINGLENGTH` — ping interval in mm
- `SPLICEOFFSET` — splice offset in mm
- `MATERIAL_*` — material splice parameters

## CI Usage

```yaml
# In GitHub Actions:
prusa-slicer --export-gcode --load profiles/prusaslicer/Palette3.ini model.stl --output out.gcode
python3 P2PP.py out.gcode
python3 tests/lint_gcode.py out.p2pp.gcode
```
