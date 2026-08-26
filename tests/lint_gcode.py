#!/usr/bin/env python3
"""
G-code lint for Palette-specific markers in p2pp output (issue #86, sub-issue 4).

Checks the Omega header that p2pp emits (see p2pp/omega.py) for structural
correctness: required markers present, declared counts matching actual line
counts, splice positions monotonically increasing, and Mosaic hexified operands
well formed. Also validates a Palette 3 .mcfx metafile as JSON.

Stdlib only, so it can run in CI before p2pp's requirements are installed.

Run from the repository root:
    python3 tests/lint_gcode.py output.gcode [more.gcode ...]
Exits 0 when clean, 1 when any finding is reported.
"""

import json
import re
import sys

# hexify_short -> "D" + 4 lowercase hex digits; hexify_float / hexify_long -> 8.
HEX_SHORT = re.compile(r"^D[0-9a-f]{4}$")
HEX_LONG = re.compile(r"^D[0-9a-f]{8}$")
# O28 falls back to decimal "D{:0>4d}" when there are more than 9 algorithms.
DEC_SHORT = re.compile(r"^D[0-9]{4}$")


def _finding(code, message):
    return "P2PP-LINT-{}: {}".format(code, message)


def _omega_lines(text):
    """Return the Omega (O-code) lines, stripped, in file order."""
    lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if re.match(r"^O\d+\b", stripped):
            lines.append(stripped)
    return lines


def _by_code(omega, code):
    return [line for line in omega if line.split(" ")[0] == code]


def _operand(line, index=1):
    parts = line.split()
    return parts[index] if len(parts) > index else ""


def _declared_count(omega, code, findings):
    """Read the count operand of a single-valued header marker (O26/O27/O28/O29)."""
    lines = _by_code(omega, code)
    if not lines:
        findings.append(_finding("001", "missing required marker {}".format(code)))
        return None
    if len(lines) > 1:
        findings.append(_finding("002", "{} appears {} times, expected once"
                                 .format(code, len(lines))))
    operand = _operand(lines[0])
    if code == "O28" and DEC_SHORT.match(operand):
        return int(operand[1:], 10)
    if HEX_SHORT.match(operand):
        return int(operand[1:], 16)
    findings.append(_finding("003", "{} has malformed operand {!r}".format(code, operand)))
    return None


def lint_gcode(text):
    """Lint p2pp G-code output. Returns a list of finding strings (empty == clean)."""
    findings = []
    omega = _omega_lines(text)

    if not omega:
        findings.append(_finding("000", "no Omega (O-code) header found; "
                                        "was this file post-processed by p2pp?"))
        return findings

    # --- required markers -------------------------------------------------
    for code in ("O21", "O22", "O25", "O26", "O27", "O28", "O29"):
        if not _by_code(omega, code):
            findings.append(_finding("001", "missing required marker {}".format(code)))

    # O22 carries the printer profile ID; an empty operand means p2pp fell back
    # to its default profile (omega.py:264-272).
    for line in _by_code(omega, "O22"):
        profile = _operand(line)
        if not profile.startswith("D") or len(profile) < 2:
            findings.append(_finding("010", "O22 printer profile is missing or empty: {!r}"
                                     .format(line)))

    # O25 defines the four Palette drives; each is "D0" (unused) or a colour spec.
    for line in _by_code(omega, "O25"):
        drives = line.split()[1:]
        if len(drives) != 4:
            findings.append(_finding("011", "O25 declares {} drives, expected 4: {!r}"
                                     .format(len(drives), line)))
        if drives and all(d == "D0" for d in drives):
            findings.append(_finding("012", "O25 declares no used inputs"))

    # --- declared counts vs. actual lines ---------------------------------
    splices = _by_code(omega, "O30")
    pings = _by_code(omega, "O31")
    algos = _by_code(omega, "O32")

    declared_splices = _declared_count(omega, "O26", findings)
    declared_pings = _declared_count(omega, "O27", findings)
    declared_algos = _declared_count(omega, "O28", findings)
    _declared_count(omega, "O29", findings)  # hotswap count: format check only

    if declared_splices is not None and declared_splices != len(splices):
        findings.append(_finding("020", "O26 declares {} splices but {} O30 lines present"
                                 .format(declared_splices, len(splices))))
    if declared_algos is not None and declared_algos != len(algos):
        findings.append(_finding("021", "O28 declares {} algorithms but {} O32 lines present"
                                 .format(declared_algos, len(algos))))
    # O31 header lines are only emitted in accessory mode; in connected mode the
    # pings are inline in the body. Only cross-check when header pings exist.
    if declared_pings is not None and pings and declared_pings != len(pings):
        findings.append(_finding("022", "O27 declares {} pings but {} O31 lines present"
                                 .format(declared_pings, len(pings))))
    if declared_splices and not algos:
        findings.append(_finding("023", "splices present but no O32 splice algorithm defined"))

    # --- splice records ---------------------------------------------------
    previous = None
    for index, line in enumerate(splices):
        tool = _operand(line, 1)
        position = _operand(line, 2)
        if not re.match(r"^D\d$", tool):
            findings.append(_finding("030", "O30 #{} has malformed tool operand {!r}"
                                     .format(index + 1, tool)))
        if not HEX_LONG.match(position):
            findings.append(_finding("031", "O30 #{} has malformed position operand {!r}"
                                     .format(index + 1, position)))
            continue
        value = int(position[1:], 16)
        if previous is not None and value <= previous:
            findings.append(_finding("032", "O30 splice positions are not increasing "
                                            "at #{} ({!r})".format(index + 1, position)))
        previous = value

    for index, line in enumerate(pings):
        operand = _operand(line, 1)
        # Connected-mode pings use "O31 L<mm> mm"; accessory mode uses hexified floats.
        if not (HEX_LONG.match(operand) or operand.startswith("L")):
            findings.append(_finding("033", "O31 #{} has malformed operand {!r}"
                                     .format(index + 1, operand)))

    # --- job terminator ---------------------------------------------------
    terminators = _by_code(omega, "O1")
    if not terminators:
        findings.append(_finding("040", "missing O1 job terminator"))
    for line in terminators:
        length = _operand(line, 2)
        if not HEX_LONG.match(length):
            findings.append(_finding("041", "O1 has malformed total-length operand {!r}"
                                     .format(length)))

    return findings


def lint_p3_metafile(text):
    """Lint a Palette 3 .mcfx metafile (JSON). Returns a list of finding strings."""
    findings = []
    try:
        meta = json.loads(text)
    except ValueError as exc:
        return [_finding("100", "P3 metafile is not valid JSON: {}".format(exc))]

    if not isinstance(meta, dict):
        return [_finding("101", "P3 metafile is not a JSON object")]

    filaments = meta.get("filaments")
    if not filaments:
        findings.append(_finding("102", "P3 metafile declares no filaments"))

    ping_count = meta.get("pingCount")
    pings = meta.get("pings")
    if ping_count is not None and isinstance(pings, list) and ping_count != len(pings):
        findings.append(_finding("103", "P3 metafile pingCount is {} but {} pings listed"
                                 .format(ping_count, len(pings))))

    return findings


def lint_file(path):
    with open(path, "r", encoding="utf-8", errors="replace") as handle:
        text = handle.read()
    if path.endswith(".json") or path.endswith(".mcfx"):
        return lint_p3_metafile(text)
    return lint_gcode(text)


def main(argv):
    if len(argv) < 2:
        print("usage: lint_gcode.py <file> [file ...]", file=sys.stderr)
        return 2

    total = 0
    for path in argv[1:]:
        findings = lint_file(path)
        total += len(findings)
        if findings:
            print("FAIL {}".format(path))
            for finding in findings:
                print("  {}".format(finding))
        else:
            print("OK   {}".format(path))

    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))