#!/usr/bin/pythonw
__author__ = 'Tom Van den Eede'
__copyright__ = 'Copyright 2018-2020, Palette2 Splicer Post Processing Project'
__credits__ = ['Tom Van den Eede',
               'Tim Brookman'
               ]
__license__ = 'GPLv3'
__maintainer__ = 'Tom Van den Eede'
__email__ = 'P2PP@pandora.be'
__status__ = 'Beta'

import os
import platform
import sys


if len(sys.argv) == 2 and sys.argv[1].lower()=="-config":
    import config.config_gui as gui
    import config.prusaconfig as prusaconfig
    gui.init_gui()
    sys.exit(-1)
else:
    import p2pp.checkversion as checkversion
    import p2pp.mcf as mcf
    import p2pp.variables as v
    import version as ver
    import traceback
    import p2pp.gui as gui

v.version = ver.Version

if len(sys.argv) == 1 or (len(sys.argv) == 2 and sys.argv[1] == "-i"):
    platformD = platform.system()

    gui.setfilename('')
    gui.form.label_5.setText("")

    MASTER_VERSION = checkversion.get_version(checkversion.MASTER)
    DEV_VERSION = checkversion.get_version(checkversion.DEV)

    if MASTER_VERSION and DEV_VERSION:

        if v.version > MASTER_VERSION:
            if v.version < DEV_VERSION:
                v.version = "Version Check: Current version {} (New dev version {} available)".format(ver.Version, DEV_VERSION)
                color = "red"
            else:
                v.version = "Version Check: Current version {} (Dev version up to date)".format(ver.Version)
                color = "green"
        else:
            if v.version < MASTER_VERSION:
                v.version = "VVersion Check: Current version {} (New stable version {} available)".format(ver.Version, MASTER_VERSION)
                color = "red"
            else:
                v.version = "Version Check: Current version {} (Version up to date)".format(ver.Version)
                color = "green"
        gui.create_logitem(v.version, color, True)

    gui.create_emptyline()
    gui.create_logitem("Line to be used in PrusaSlicer [Print Settings][Output Options][Post Processing Script]",
                       "blue")
    gui.create_emptyline()

    if platformD == 'Darwin':
        gui.create_logitem("<b>open -W -a P2PP.app --args<b>".format(os.path.dirname(sys.argv[0])), "red")
    elif platformD == 'Windows':
        pathname = os.path.dirname(sys.argv[0])
        pathname = pathname.replace(" ", "! ")
        gui.create_logitem("<b>{}\\p2pp.exe</b>".format(os.path.dirname(sys.argv[0]).replace(" ", "! ")), "red")

    gui.create_emptyline()
    gui.create_logitem("This requires ADVANCED/EXPERT settings to be enabled", "blue")
    gui.create_emptyline()
    gui.create_emptyline()
    gui.create_logitem("Don't forget to complete the remaining Prusaslicer Configuration", "blue")
    gui.create_logitem("More info on: https://github.com/tomvandeneede/p2pp", "blue")
    gui.progress_string(101)
    gui.close_button_enable()
    sys.exit()

else:

    filename = sys.argv[1]
    if len(sys.argv) > 2:
        outputfile = sys.argv[2]
    else:
        outputfile = None
    try:
        mcf.generate(filename, outputfile)
    except Exception as e:
        gui.create_emptyline()
        gui.log_warning("We're sorry but an unexpected error occurred while processing your file")
        gui.log_warning("Please sumbit an issue report on https://github.com/tomvandeneede/p2pp")
        gui.create_emptyline()
        gui.create_logitem("<b>Error:</b> {}".format(e))
        tb = traceback.format_tb(e.__traceback__)
        gui.create_emptyline()
        gui.create_logitem("<b>Traceback Info:</b>")
        for line in tb:
            gui.create_logitem("{}".format(line))

        gui.progress_string(0)
        gui.close_button_enable()
        sys.exit(-1)

gui.close_button_enable()
