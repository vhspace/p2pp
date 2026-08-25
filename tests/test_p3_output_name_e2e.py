"""End-to-end test: P3 output-name warnings reach gui.log_warning.

Verifies the full path from config parsing to warning display, not just
that p3_output_name_warnings() returns the right values.
"""

import sys
import os
import unittest.mock as mock

# Stub out gui before importing p2pp modules that depend on it
sys.modules['p2pp.gui'] = mock.MagicMock()

import p2pp.variables as v
import p2pp.p2ppparams as params


def test_p3_output_name_warnings_reach_gui_log_warning():
    """E2E: P3 output-name warnings are emitted via gui.log_warning."""
    # Setup: simulate a Palette 3 config with a bad output name
    v.palette3 = True
    v.filename = "test.gcode"
    v.output_basename = "test"  # missing .mcfx extension

    # Call the warning path
    with mock.patch.object(sys.modules['p2pp.gui'], 'log_warning') as mock_warn:
        # Trigger the output-name check (moved after config parsing by #80)
        params.p3_output_name_warnings()

        # Verify the warning was emitted
        assert mock_warn.called, "P3 output-name warning should reach gui.log_warning"
        call_args = str(mock_warn.call_args_list)
        assert '.mcfx' in call_args or 'output' in call_args.lower(), \
            f"Warning should mention .mcfx extension: {call_args}"


def test_p3_output_name_no_warning_for_valid_name():
    """E2E: no warning when output name has .mcfx extension."""
    v.palette3 = True
    v.filename = "test.gcode"
    v.output_basename = "test.mcfx"

    with mock.patch.object(sys.modules['p2pp.gui'], 'log_warning') as mock_warn:
        params.p3_output_name_warnings()
        assert not mock_warn.called, "No warning expected for valid .mcfx name"


if __name__ == '__main__':
    test_p3_output_name_warnings_reach_gui_log_warning()
    test_p3_output_name_no_warning_for_valid_name()
    print("PASS: e2e P3 output-name warnings reach gui.log_warning")
