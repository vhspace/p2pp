"""
Unit tests for the Palette G-code lint validator (issue #86).

The fixtures are synthetic Omega headers matching the format p2pp emits in
p2pp/omega.py, so these tests run offline with no slicer dependency.

Run from the repository root:
    python3 tests/test_lint_gcode.py
or with pytest:
    pytest tests/test_lint_gcode.py
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lint_gcode import lint_gcode, lint_p3_metafile

# Two splices, one algorithm, no header pings (connected mode).
GOOD_P2_HEADER = """\
O21 D0014
O22 D0123456789abcdef
O23 D0001
O24 D0000
O25 D1FF0000Red;PLA D2 00FF00Green;PLA D0 D0
O26 D0002
O27 D0003
O28 D0001
O29 D0000
O30 D0 D42c80000
O30 D1 D43160000
O32 D1 D1 D0 D0 D0
O1 Dtest.gcode D000186a0
"""


def _codes(findings):
    return sorted(finding.split(":")[0] for finding in findings)


def test_good_header_is_clean():
    assert lint_gcode(GOOD_P2_HEADER) == []


def test_missing_omega_header():
    assert _codes(lint_gcode("G1 X0 Y0\nG1 X1 Y1\n")) == ["P2PP-LINT-000"]


def test_missing_o22():
    text = "\n".join(line for line in GOOD_P2_HEADER.splitlines()
                     if not line.startswith("O22")) + "\n"
    assert "P2PP-LINT-001" in _codes(lint_gcode(text))


def test_splice_count_mismatch():
    text = GOOD_P2_HEADER.replace("O26 D0002", "O26 D0005")
    assert "P2PP-LINT-020" in _codes(lint_gcode(text))


def test_algorithm_count_mismatch():
    text = GOOD_P2_HEADER.replace("O28 D0001", "O28 D0003")
    assert "P2PP-LINT-021" in _codes(lint_gcode(text))


def test_non_monotonic_splice_positions():
    text = GOOD_P2_HEADER.replace("O30 D1 D43160000", "O30 D1 D42000000")
    assert "P2PP-LINT-032" in _codes(lint_gcode(text))


def test_malformed_splice_position():
    text = GOOD_P2_HEADER.replace("O30 D1 D43160000", "O30 D1 DZZZZ")
    assert "P2PP-LINT-031" in _codes(lint_gcode(text))


def test_missing_job_terminator():
    text = "\n".join(line for line in GOOD_P2_HEADER.splitlines()
                     if not line.startswith("O1 ")) + "\n"
    assert "P2PP-LINT-040" in _codes(lint_gcode(text))


def test_o28_accepts_decimal_form_above_nine_algorithms():
    algos = "\n".join("O32 D1 D1 D0 D0 D0" for _ in range(12))
    text = GOOD_P2_HEADER.replace("O28 D0001", "O28 D0012").replace(
        "O32 D1 D1 D0 D0 D0", algos)
    assert lint_gcode(text) == []


def test_p3_metafile_valid():
    meta = json.dumps({"filaments": [{"filamentId": 1}],
                       "pingCount": 2,
                       "pings": [{"length": 1.0}, {"length": 2.0}]})
    assert lint_p3_metafile(meta) == []


def test_p3_metafile_bad_json():
    assert _codes(lint_p3_metafile("{not json")) == ["P2PP-LINT-100"]


def test_p3_metafile_ping_count_mismatch():
    meta = json.dumps({"filaments": [{"filamentId": 1}],
                       "pingCount": 5,
                       "pings": [{"length": 1.0}]})
    assert "P2PP-LINT-103" in _codes(lint_p3_metafile(meta))


if __name__ == "__main__":
    failures = 0
    for name, func in sorted(list(globals().items())):
        if name.startswith("test_") and callable(func):
            try:
                func()
                print("PASS {}".format(name))
            except AssertionError as exc:
                failures += 1
                print("FAIL {}: {}".format(name, exc))
    sys.exit(1 if failures else 0)