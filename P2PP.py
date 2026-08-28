#!/usr/bin/env python3
__author__ = 'Tom Van den Eede'
__copyright__ = 'Copyright 2018-2022, Palette2 Splicer Post Processing Project'
__credits__ = ['Tom Van den Eede',
               'Tim Brookman'
               ]
__license__ = 'GPLv3'
__maintainer__ = 'Tom Van den Eede'
__email__ = 'P2PP@pandora.be'
__status__ = 'Beta'

import sys

if "--cli" in sys.argv:
    sys.argv.remove("--cli")
    # Signal to all modules that we're in headless mode
    import os
    os.environ["P2PP_HEADLESS"] = "1"
    # Install headless shim BEFORE any p2pp submodule import.
    # All modules that do `import p2pp.gui as gui` will get this Qt-free
    # version — no QApplication, no event loop, no image_rc.
    import p2pp.headless
    sys.modules["p2pp.gui"] = p2pp.headless

    from p2pp.mcf import p2pp_process_file_cli

    if len(sys.argv) < 2:
        print("Usage: P2PP.py --cli input.gcode [output.gcode]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        p2pp_process_file_cli(input_file, output_file)
        sys.exit(0)
    except Exception as e:
        import traceback
        print(f"Error: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
else:
    from p2pp.main import main
    main()