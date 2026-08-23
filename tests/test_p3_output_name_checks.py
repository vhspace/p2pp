"""
Smoke test for the Palette 3 output-name checks (issue #77).

Both warnings used to be evaluated before configuration parsing completed,
so v.palette3 was still False and they could never fire. They now run in
p2pp_process_file() right after parse_config_parameters().

Run from the repository root:
    python3 tests/test_p3_output_name_checks.py
or with pytest:
    pytest tests/test_p3_output_name_checks.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from p2pp.variables import p3_output_name_warnings

MCF_SOURCE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "p2pp", "mcf.py")


def test_no_upload_warning_for_file_host():
    assert p3_output_name_warnings("File", "job.mcfx") == []


def test_upload_warning_for_non_file_host():
    assert p3_output_name_warnings("OctoPrint", "job.mcfx") == [
        "Palette 3 File uploading currently not supported"]


def test_mcfx_extension_warning():
    assert p3_output_name_warnings(None, "job.gcode") == [
        "Palette 3 files should have a .mcfx extension"]


def test_both_warnings():
    assert p3_output_name_warnings("PrusaLink", "job.gcode") == [
        "Palette 3 File uploading currently not supported",
        "Palette 3 files should have a .mcfx extension",
    ]


def test_valid_output_has_no_warnings():
    assert p3_output_name_warnings(None, "job.mcfx") == []
    assert p3_output_name_warnings("File", "job.mcfx") == []


def test_empty_host_counts_as_upload_target():
    assert p3_output_name_warnings("", "job.mcfx") == [
        "Palette 3 File uploading currently not supported"]


def test_checks_run_after_config_parsing():
    # Regression guard: p2pp.mcf cannot be imported without PyQt5, so verify
    # in the source that the output-name check is emitted after
    # parse_config_parameters(), which is what sets v.palette3.
    with open(MCF_SOURCE, encoding="utf-8") as sourcefile:
        source = sourcefile.read()
    parse_position = source.index("parse_config_parameters()")
    check_position = source.index("p3_output_name_warnings(")
    assert check_position > parse_position, \
        "P3 output-name checks must run after config parsing sets v.palette3"


if __name__ == "__main__":
    test_no_upload_warning_for_file_host()
    test_upload_warning_for_non_file_host()
    test_mcfx_extension_warning()
    test_both_warnings()
    test_valid_output_has_no_warnings()
    test_empty_host_counts_as_upload_target()
    test_checks_run_after_config_parsing()
    print("All P3 output-name check tests passed.")
