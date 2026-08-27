#!/usr/bin/env python3
"""
Palette 3 device acceptance simulator (issue #100).

Models how the Palette 3 ingests a p2pp-produced job: it replays the Omega
header the way the device does and rejects anything the device would reject.

This is a *behavioural* simulator, not emulated firmware. Mosaic does not
publish a redistributable Palette 3 firmware image or rootfs, so there is
nothing to boot under qemu-system-arm in a public CI run -- see
docs/e2e_pipeline.md. Issue #100's acceptance criteria allow this explicitly
("or documented why it cannot run in CI").

What this adds over tests/lint_gcode.py: the lint checks structure only and
compares O30 operands as raw integers. Splice and ping positions are hexified
IEEE-754 float32 bit patterns (p2pp/formatnumbers.py:28-31), so this simulator
decodes them to millimetres and enforces the device's *geometric* limits --
minimum splice length, minimum first splice, ping spacing, and total-length
consistency.

Usage:
    python3 tests/p3_simulator.py processed.gcode [job.mcfx ...]
Exits 0 when the device would accept every file, 1 otherwise.
"""

import argparse
import json
import re
import struct
import sys

HEX_LONG = re.compile(r"^D([0-9a-f]{8})$")
HEX_SHORT = re.compile(r"^D([0-9a-f]{4})$")
DEC_SHORT = re.compile(r"^D([0-9]{4})$")

# Header markers must be seen before the first splice record, in this order.
HEADER_ORDER = ("O21", "O22", "O25", "O26", "O27", "O28", "O29")


def _reject(code, message):
    return "P3-SIM-{}: {}".format(code, message)


def decode_float(operand):
    """Decode a hexify_float operand ("D" + 8 hex digits) to millimetres."""
    match = HEX_LONG.match(operand)
    if not match:
        return None
    return struct.unpack("<f", bytes.fromhex(match.group(1)))[0]


def decode_short(operand):
    """Decode a hexify_short count operand; O28 may fall back to decimal."""
    match = HEX_SHORT.match(operand)
    if match:
        return int(match.group(1), 16)
    match = DEC_SHORT.match(operand)
    if match:
        return int(match.group(1), 10)
    return None


def _omega(text):
    out = []
    for line in text.splitlines():
        stripped = line.strip()
        if re.match(r"^O\d+\b", stripped):
            out.append(stripped.split())
    return out


def simulate(text, min_splice=70.0, min_first_splice=100.0,
             ping_length=350.0, ping_tolerance=0.35):
    """Replay a job the way the P3 does. Returns a list of rejection strings."""
    rejects = []
    omega = _omega(text)
    if not omega:
        return [_reject("000", "no Omega header; device would reject the file")]

    seen = set()
    used_drives = set()
    header_done = False
    splices = []
    pings = []
    algo_count = 0
    terminator = None

    for parts in omega:
        code, operands = parts[0], parts[1:]

        if code == "O25":
            # Drive spec: 4 entries, "D0" == unused. Colour specs contain
            # spaces, so re-split the raw record on " D" boundaries.
            drives = re.split(r"\s+(?=D)", " ".join(parts))[1:]
            if len(drives) != 4:
                rejects.append(_reject("010", "O25 declares {} drives, device "
                                          "expects 4".format(len(drives))))
            for index, drive in enumerate(drives):
                if drive != "D0":
                    used_drives.add(index)
            if not used_drives:
                rejects.append(_reject("011", "O25 declares no used inputs"))

        elif code == "O22":
            profile = operands[0] if operands else ""
            if len(profile) < 2 or not profile.startswith("D"):
                rejects.append(_reject("012", "O22 printer profile is empty; the "
                                              "device cannot match a profile"))

        elif code == "O28":
            algo_count = decode_short(operands[0]) if operands else None

        elif code == "O30":
            if not header_done:
                missing = [m for m in HEADER_ORDER if m not in seen]
                if missing:
                    rejects.append(_reject("001", "splice data starts before header "
                                                  "markers {}".format(",".join(missing))))
                header_done = True
            tool = operands[0] if operands else ""
            position = decode_float(operands[1]) if len(operands) > 1 else None
            if not re.match(r"^D\d$", tool):
                rejects.append(_reject("020", "O30 #{} malformed tool {!r}"
                                       .format(len(splices) + 1, tool)))
            elif int(tool[1:]) not in used_drives:
                rejects.append(_reject("021", "O30 #{} splices from drive {} which "
                                              "O25 marks unused"
                                       .format(len(splices) + 1, tool[1:])))
            if position is None:
                rejects.append(_reject("022", "O30 #{} malformed position"
                                       .format(len(splices) + 1)))
            else:
                splices.append(position)

        elif code == "O31":
            operand = operands[0] if operands else ""
            value = decode_float(operand)
            if value is None and not operand.startswith("L"):
                rejects.append(_reject("030", "O31 #{} malformed operand {!r}"
                                       .format(len(pings) + 1, operand)))
            elif value is not None:
                pings.append(value)

        elif code == "O1":
            terminator = decode_float(operands[1]) if len(operands) > 1 else None
            if terminator is None:
                rejects.append(_reject("040", "O1 has a malformed total length"))

        seen.add(code)

    # --- geometry the device enforces before it will start a job ------------
    previous = 0.0
    for index, position in enumerate(splices):
        length = position - previous
        limit = min_first_splice if index == 0 else min_splice
        if length <= 0:
            rejects.append(_reject("023", "splice #{} at {:.2f}mm does not advance "
                                          "past {:.2f}mm".format(index + 1, position, previous)))
        elif length < limit:
            rejects.append(_reject("024", "splice #{} is {:.2f}mm, below the {:.2f}mm "
                                          "minimum the device can cut"
                                   .format(index + 1, length, limit)))
        previous = position

    previous = None
    for index, position in enumerate(pings):
        if previous is not None:
            gap = position - previous
            if gap <= 0:
                rejects.append(_reject("031", "ping #{} does not advance past the "
                                              "previous ping".format(index + 1)))
            elif abs(gap - ping_length) > ping_length * ping_tolerance:
                rejects.append(_reject("032", "ping #{} spacing {:.1f}mm is outside "
                                              "{:.0f}% of the {:.0f}mm ping length"
                                       .format(index + 1, gap, ping_tolerance * 100,
                                               ping_length)))
        previous = position

    if splices and not algo_count:
        rejects.append(_reject("013", "job has splices but declares no O32 splice "
                                      "algorithm; the device cannot splice"))
    if terminator is None and splices:
        rejects.append(_reject("041", "missing O1 job terminator"))
    elif terminator is not None and splices and terminator < splices[-1]:
        rejects.append(_reject("042", "O1 total length {:.2f}mm is shorter than the "
                                      "last splice at {:.2f}mm"
                               .format(terminator, splices[-1])))

    return rejects


def simulate_metafile(text):
    """Validate a Palette 3 .mcfx metafile the way the device parses it."""
    try:
        meta = json.loads(text)
    except ValueError as exc:
        return [_reject("100", "metafile is not valid JSON: {}".format(exc))]
    if not isinstance(meta, dict):
        return [_reject("101", "metafile is not a JSON object")]
    if not meta.get("filaments"):
        return [_reject("102", "metafile declares no filaments")]
    return []


def simulate_file(path, **limits):
    with open(path, "r", encoding="utf-8", errors="replace") as handle:
        text = handle.read()
    if path.endswith(".mcfx") or path.endswith(".json"):
        return simulate_metafile(text)
    return simulate(text, **limits)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    parser.add_argument("files", nargs="+")
    parser.add_argument("--min-splice", type=float, default=70.0)
    parser.add_argument("--min-first-splice", type=float, default=100.0)
    parser.add_argument("--ping-length", type=float, default=350.0)
    parser.add_argument("--json", action="store_true",
                        help="emit a machine-readable report")
    args = parser.parse_args(argv)

    report = {}
    total = 0
    for path in args.files:
        if path.endswith(".mcfx") or path.endswith(".json"):
            rejects = simulate_file(path)
        else:
            rejects = simulate_file(path,
                                    min_splice=args.min_splice,
                                    min_first_splice=args.min_first_splice,
                                    ping_length=args.ping_length)
        report[path] = rejects
        total += len(rejects)
        if not args.json:
            if rejects:
                print("REJECTED {}".format(path))
                for reject in rejects:
                    print("  {}".format(reject))
            else:
                print("ACCEPTED {}".format(path))

    if args.json:
        print(json.dumps({"accepted": total == 0, "findings": report}, indent=2))
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())