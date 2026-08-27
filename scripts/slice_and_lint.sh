#!/usr/bin/env bash
# Slice a test model, post-process it with p2pp, then lint the result.
# Issue #86 sub-issue 3 (G-code capture) + 4 (lint validator).
#
# Usage:
#   scripts/slice_and_lint.sh <model.stl|model.3mf> [slicer-config.ini]
#
# Set SLICER to the slicer binary (prusa-slicer, PrusaSlicer AppImage, or
# orca-slicer). If no slicer is found the script skips with exit 0 so it can be
# wired into CI before the container work (sub-issue 1) lands.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MODEL="${1:-}"
CONFIG="${2:-${REPO_ROOT}/profiles/prusaslicer/Palette3-cli.ini}"
OUTDIR="${OUTDIR:-${REPO_ROOT}/.live-test-out}"

if [ -z "${MODEL}" ]; then
  echo "usage: $0 <model.stl|model.3mf> [slicer-config.ini]" >&2
  exit 2
fi

SLICER="${SLICER:-}"
if [ -z "${SLICER}" ]; then
  for candidate in prusa-slicer PrusaSlicer orca-slicer OrcaSlicer; do
    if command -v "${candidate}" >/dev/null 2>&1; then
      SLICER="${candidate}"
      break
    fi
  done
fi

if [ -z "${SLICER}" ]; then
  echo "SKIP: no slicer binary found (set SLICER=/path/to/prusa-slicer)."
  echo "      See docs/live-test-research.md for container setup (issue #86)."
  exit 0
fi

mkdir -p "${OUTDIR}"
GCODE="${OUTDIR}/$(basename "${MODEL%.*}").gcode"

echo "==> Slicing ${MODEL} with ${SLICER}"
if [ -n "${CONFIG}" ]; then
  "${SLICER}" --export-gcode --load "${CONFIG}" --output "${GCODE}" "${MODEL}"
else
  "${SLICER}" --export-gcode --output "${GCODE}" "${MODEL}"
fi

echo "==> Running p2pp over ${GCODE}"
# P2PP.py takes positional args (p2pp/main.py:100-104); there is no -i flag.
PROCESSED="${OUTDIR}/$(basename "${MODEL%.*}")-p2pp.gcode"
QT_QPA_PLATFORM="${QT_QPA_PLATFORM:-offscreen}" \
  python3 "${REPO_ROOT}/P2PP.py" "${GCODE}" "${PROCESSED}"

echo "==> Linting p2pp output"
shopt -s nullglob
OUTPUTS=("${OUTDIR}"/*.gcode "${OUTDIR}"/*.mcfx "${OUTDIR}"/*.msf)
if [ ${#OUTPUTS[@]} -eq 0 ]; then
  echo "FAIL: p2pp produced no output files in ${OUTDIR}" >&2
  exit 1
fi
python3 "${REPO_ROOT}/tests/lint_gcode.py" "${OUTPUTS[@]}"