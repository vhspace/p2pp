"""Headless shim for p2pp.gui — routes GUI logging to stdout, never blocks.

Installed as sys.modules['p2pp.gui'] in CLI mode so that modules which do
`import p2pp.gui as gui` at module level get a Qt-free implementation
and never start a QApplication / event loop.
"""
import re
import sys
import traceback
from unittest import mock

form = mock.MagicMock()
window = mock.MagicMock()


class _App:
    def sync(self): pass
    def exec_(self): return 0
    def exec(self): return 0
    def quit(self): pass
    def exit(self, *_a, **_k): pass
    def processEvents(self): pass


app = _App()


def _strip_html(text):
    return re.sub(r"<[^>]+>", "", str(text))


def create_logitem(text, color=None, force_update=True, position=0):
    line = _strip_html(text)
    if line.strip():
        print(line)


def create_emptyline():
    print("")


def create_colordefinition(reporttype, p2_input, filament_type, color_code, filamentused):
    print(f"  Input {p2_input}  {filamentused:8.2f}mm - {filament_type} [{color_code}]")


def log_warning(text):
    print(f"WARNING: {_strip_html(text)}", file=sys.stderr)


def progress_string(pct):
    pass


def print_summary(summary):
    import p2pp.variables as v
    print("-" * 40)
    print("Print Summary")
    print("-" * 40)
    print(f"Number of splices: {len(v.splice_extruder_position):5}")
    print(f"Number of pings:   {len(v.ping_extruder_position):5}")
    print(f"Total print length {v.total_material_extruded:8.2f}mm")
    for line in summary:
        print(line[1:].strip())


def setfilename(text):
    if text:
        print(f"Input: {text}")


def close_button_enable():
    return


def logexception(e):
    print(f"Error: {e}", file=sys.stderr)
    traceback.print_exc()