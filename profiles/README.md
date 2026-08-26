# Palette Printer Profiles

Printer profiles for PrusaSlicer and OrcaSlicer configured for use with p2pp.

## Installation

### PrusaSlicer
1. Open PrusaSlicer
2. Go to Settings > Printer > Add > Load from file
3. Select the appropriate `.ini` file from this directory

### OrcaSlicer
1. Open OrcaSlicer
2. Go to Settings > Printer > Add > Load profile
3. Select the appropriate `.ini` file from this directory

## Profiles

| File | Slicer | Palette | Ping Interval | Splice Tolerance |
|------|--------|---------|---------------|-------------------|
| `palette2-prusaslicer.ini` | PrusaSlicer | Palette 2 | 350mm | 0.5mm |
| `palette3-prusaslicer.ini` | PrusaSlicer | Palette 3 | 300mm | 0.3mm |
| `palette2-orcaslicer.ini` | OrcaSlicer | Palette 2 | 350mm | 0.5mm |
| `palette3-orcaslicer.ini` | OrcaSlicer | Palette 3 | 300mm | 0.3mm |

## Post-Processing

All profiles configure p2pp as the post-processing script. The G-code output from the slicer is passed through p2pp which adds Palette-specific markers (O22 ping/pong, P3 metafile) for multi-color printing.

## Customization

Adjust the following parameters in the `[post_process]` section:
- `--ping-interval`: Distance between ping markers (mm). Lower = more frequent pings
- `--splice-tolerance`: Acceptable splice position variance (mm)
- `--enable-ping-logging`: Enable detailed ping/pong logging for debugging
