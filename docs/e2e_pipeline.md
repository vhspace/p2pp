# End-to-end test pipeline

Issue #100. Runs on every PR as the `e2e-pipeline` job in
`.github/workflows/live-test.yml`.

```
PrusaSlicer (Flathub)  scripts/install_prusaslicer.sh
  -> slice tests/models/multi-color.stl with profiles/prusaslicer/Palette3-cli.ini
  -> p2pp post-processing (P2PP.py <input> <output>)
  -> tests/lint_gcode.py     structural Omega-header lint
  -> tests/p3_simulator.py   Palette 3 acceptance simulation
```

## Running locally (Linux)

```bash
bash scripts/install_prusaslicer.sh
bash scripts/e2e_pipeline.sh
```

Artifacts land in `.live-test-out/` (`raw.gcode`, `processed.gcode`, any `.mcfx`).

## Pinning the PrusaSlicer build

PrusaSlicer 2.9.x publishes no AppImage; Flathub is the supported Linux channel.
Read the current commit and set it in the workflow's `PRUSASLICER_FLATPAK_COMMIT`:

```bash
flatpak remote-info --system flathub com.prusa3d.PrusaSlicer
```

`scripts/install_prusaslicer.sh` echoes the resolved version/commit on every run,
so a CI log always records exactly which build produced the G-code (issue #99).

## Why a single STL still exercises multi-colour

`profiles/prusaslicer/Palette3-cli.ini` assigns each *feature type* to a different
extruder (`perimeter_extruder=1`, `infill_extruder=2`, `solid_infill_extruder=3`,
`top_solid_infill_extruder=4`). PrusaSlicer therefore emits real T0-T3 tool changes
and a wipe tower from the 10 mm `tests/models/multi-color.stl` cube, with no need to
hand-author per-object extruder assignments inside a 3MF. The pipeline asserts that
at least two tool changes are present before handing the file to p2pp, so a config
regression that silently produces single-colour G-code fails the job rather than
passing vacuously.

## Why the Palette 3 firmware is not emulated under QEMU

Issue #100 asks for a QEMU-hosted P3 firmware stage. That is not achievable in
public CI: Mosaic does not distribute a Palette 3 firmware image or rootfs under
terms that permit redistribution or use in an unattended build, so there is no
lawful artifact to boot with `qemu-system-arm`. Issue #100's acceptance criteria
allow this outcome ("P3 simulator accepts the processed G-code **or documented why
it cannot run in CI**).

`tests/p3_simulator.py` covers the intent instead. It replays the Omega header the
way the device ingests it and enforces the checks that actually gate a job on
hardware, decoding the hexified IEEE-754 float32 operands
(`p2pp/formatnumbers.py:28-31`) to millimetres so it can validate real geometry
rather than raw bit patterns:

| Check | Rejection code |
|---|---|
| Header markers precede splice data | `P3-SIM-001` |
| Exactly four drives declared, at least one used | `P3-SIM-010/011` |
| Printer profile present in `O22` | `P3-SIM-012` |
| Splice algorithm declared when splices exist | `P3-SIM-013` |
| Splice references a used drive | `P3-SIM-021` |
| Splice positions strictly increasing (mm) | `P3-SIM-023` |
| Splice length above the device minimum (mm) | `P3-SIM-024` |
| Ping spacing matches the configured ping length | `P3-SIM-031/032` |
| `O1` total length consistent with the last splice | `P3-SIM-041/042` |
| `.mcfx` metafile parses and declares filaments | `P3-SIM-100/102` |

If a redistributable firmware image becomes available, the simulator stage in
`scripts/e2e_pipeline.sh` is the single place to swap for a QEMU run.