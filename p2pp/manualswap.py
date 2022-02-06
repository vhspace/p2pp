__author__ = 'Tom Van den Eede'
__copyright__ = 'Copyright 2018-2022, Palette2 Splicer Post Processing Project'
__credits__ = ['Tom Van den Eede']
__license__ = 'GPLv3'
__maintainer__ = 'Tom Van den Eede'
__email__ = 'P2PP@pandora.be'

# Added functionality for manual swap - Manmeet Singh

import p2pp.variables as v
import p2pp.gui as gui
import p2pp.gcode as gc

warning = True


def swap_pause(command):
    global warning
    if v.z_maxheight > 0:
        lift = min(v.current_position_z + 20, v.z_maxheight)
    else:
        lift = v.current_position_z + 20
        if warning:
            gui.log_warning("Manual swap lift of 20 without constraint!!")

    gc.issue_code(";MANUAL SWAP PAUSE SEQUENCE")
    gc.issue_code("G1 Z{:.2f} F10800".format(lift))
    gc.issue_code(command)


def swap_unpause(z=v.current_position_z):
    gc.issue_code("G1 Z{:.2f} F10800".format(z))
