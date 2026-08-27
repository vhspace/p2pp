#!/usr/bin/env python3
"""Unit tests for the Palette 3 acceptance simulator (issue #100).

Stdlib only, so it runs in CI without p2pp's requirements and without a slicer.
"""

import os
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from p3_simulator import decode_float, simulate, simulate_metafile


def hexify_float(value):
    """Mirror of p2pp/formatnumbers.py:hexify_float."""
    return "D" + struct.pack("<f", value).hex()


def job(splices=((0, 150.0), (1, 400.0), (0, 700.0)), pings=(350.0, 700.0),
        profile="D0123456789abcdef", drives="D1ff0000Red;PLA D200ff00Green;PLA D0 D0",
        algos=1, total=900.0):
    lines = [
        "O21 D0014",
        "O22 {}".format(profile),
        "O25 {}".format(drives),
        "O26 D{:0>4x}".format(len(splices)),
        "O27 D{:0>4x}".format(len(pings)),
        "O28 D{:0>4x}".format(algos),
        "O29 D0000",
    ]
    for tool, position in splices:
        lines.append("O30 D{} {}".format(tool, hexify_float(position)))
    for position in pings:
        lines.append("O31 {} D00000000".format(hexify_float(position)))
    for _ in range(algos):
        lines.append("O32 D0 D0 D0000")
    if total is not None:
        lines.append("O1 D0 {}".format(hexify_float(total)))
    return "\n".join(lines) + "\n"


class TestDecoding(unittest.TestCase):
    def test_decode_float_roundtrip(self):
        self.assertAlmostEqual(decode_float(hexify_float(123.5)), 123.5, places=3)

    def test_decode_float_rejects_garbage(self):
        self.assertIsNone(decode_float("Dzz"))


class TestAcceptance(unittest.TestCase):
    def test_well_formed_job_is_accepted(self):
        self.assertEqual(simulate(job()), [])

    def test_empty_file_is_rejected(self):
        self.assertTrue(simulate("G1 X0 Y0\n"))

    def test_non_increasing_splices_rejected(self):
        rejects = simulate(job(splices=((0, 150.0), (1, 400.0), (0, 300.0))))
        self.assertTrue(any("023" in r for r in rejects))

    def test_short_splice_rejected(self):
        rejects = simulate(job(splices=((0, 150.0), (1, 165.0), (0, 500.0))))
        self.assertTrue(any("024" in r for r in rejects))

    def test_short_first_splice_rejected(self):
        rejects = simulate(job(splices=((0, 20.0), (1, 400.0), (0, 700.0))))
        self.assertTrue(any("024" in r for r in rejects))

    def test_splice_from_unused_drive_rejected(self):
        rejects = simulate(job(splices=((3, 150.0), (1, 400.0), (0, 700.0))))
        self.assertTrue(any("021" in r for r in rejects))

    def test_empty_printer_profile_rejected(self):
        rejects = simulate(job(profile="D"))
        self.assertTrue(any("012" in r for r in rejects))

    def test_wrong_drive_count_rejected(self):
        rejects = simulate(job(drives="D1ff0000Red;PLA D0"))
        self.assertTrue(any("010" in r for r in rejects))

    def test_bad_ping_spacing_rejected(self):
        rejects = simulate(job(pings=(350.0, 360.0)))
        self.assertTrue(any("032" in r for r in rejects))

    def test_missing_terminator_rejected(self):
        rejects = simulate(job(total=None))
        self.assertTrue(any("041" in r for r in rejects))

    def test_short_total_length_rejected(self):
        rejects = simulate(job(total=500.0))
        self.assertTrue(any("042" in r for r in rejects))

    def test_no_splice_algorithm_rejected(self):
        rejects = simulate(job(algos=0))
        self.assertTrue(any("013" in r for r in rejects))


class TestMetafile(unittest.TestCase):
    def test_valid_metafile_accepted(self):
        self.assertEqual(simulate_metafile('{"filaments": [{"id": 1}]}'), [])

    def test_invalid_json_rejected(self):
        self.assertTrue(simulate_metafile("{not json"))

    def test_no_filaments_rejected(self):
        self.assertTrue(simulate_metafile('{"filaments": []}'))


if __name__ == "__main__":
    unittest.main(verbosity=2)