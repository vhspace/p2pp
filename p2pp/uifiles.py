import os
import sys

SYSTEM_UI_DIR = "/usr/share/p2pp"


def find_ui(filename):
    candidates = []
    argv_dir = os.path.dirname(sys.argv[0])
    if len(argv_dir) > 0:
        candidates.append(os.path.join(argv_dir, filename))
    candidates.append(os.path.join(SYSTEM_UI_DIR, filename))
    candidates.append(filename)
    for candidate in candidates:
        if os.path.exists(candidate):
            return candidate
    return filename
