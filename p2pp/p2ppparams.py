__author__ = 'Tom Van den Eede'
__copyright__ = 'Copyright 2018-2021, Palette2 Splicer Post Processing Project'
__credits__ = ['Tom Van den Eede',
               'Tim Brookman'
               ]
__license__ = 'GPLv3'
__maintainer__ = 'Tom Van den Eede'
__email__ = 'P2PP@pandora.be'

import p2pp.gui as gui
import p2pp.variables as v


def floatparameter(s):
    try:
        return float(s)
    except ValueError:
        return 0


def intparameter(s):
    try:
        return int(s)
    except ValueError:
        return 0


def check_splice_table():
    if len(v.splice_algorithm_table) > 0 or v.default_splice_algorithm is not None:
        gui.log_warning("Algorithm definitions should appear AFTER Palette Model selection (PALETTE3/PALETTE3_PRO/ACCESSORYMODE_MAF/ACCESSORYMODE_MSF)")


def check_config_parameters(keyword, value):
    keyword = keyword.upper().strip()

    if value is None:
        value = ""

    if keyword == "TEMPERATURECONTROL":
        v.process_temp = True

    if keyword == "SAVEUNPROCESSED":
        v.save_unprocessed = True


    if keyword == "PRINTERPROFILE":
        value = value.strip(" ")
        if len(value) != 16:
            gui.log_warning("Invalid Printer profile!  - Has invalid length (expect 16) - [{}]"
                            .format(value))
            value = ""
        if not all(char in set("0123456789ABCDEFabcdef") for char in value):
            gui.log_warning("Invalid Printer profile!  - Invalid characters  (expect 0123456789abcdef) - [{}]"
                            .format(value))
            value = ""

        if len(value) == 16:
            v.printer_profile_string = value
            return

    if keyword == "PALETTE3":
        v.palette3 = True
        v.colors = 4
        check_splice_table()
        return

    if keyword == "PALETTE3_PRO":
        v.palette3 = True
        v.colors = 8
        check_splice_table()
        return

    if keyword == "ACCESSORYMODE_MAF":
        v.accessory_mode = True
        v.colors = 4
        gui.create_logitem("Config: Palette2 Accessory Mode Selected")
        check_splice_table()
        return

    if keyword == "ACCESSORYMODE_MSF":
        v.accessory_mode = True
        v.palette_plus = True
        v.colors = 4
        gui.create_logitem("Config: Palette+ Accessory Mode Selected")
        check_splice_table()
        return

    if keyword == "P+LOADINGOFFSET":
        v.palette_plus_loading_offset = int(float(value))
        return

    if keyword == "P+PPM":
        v.palette_plus_ppm = floatparameter(value)
        return

    if keyword == "SPLICEOFFSET":
        v.splice_offset = floatparameter(value)
        gui.create_logitem("SPLICE OFFSET: {:-5.2f}mm".format(v.splice_offset))
        return

    if keyword == "EXTRUSIONMULTIPLIERCORRECTION":
        v.filament_type[v.current_tool] = floatparameter(value)
        return

    if keyword == "EXTRAENDFILAMENT":
        v.extra_runout_filament = floatparameter(value)
        gui.create_logitem("Extra filament at end of print {:-8.2f}mm".format(v.extra_runout_filament))
        return

    if keyword == "MANUAL_SWAP":
        v.manual_filament_swap = True
        gui.create_logitem("Manual filament swap in place.")
        return

    if keyword == "BEFORESIDEWIPEGCODE":
        v.before_sidewipe_gcode.append(value)
        return

    if keyword == "AFTERSIDEWIPEGCODE":
        v.after_sidewipe_gcode.append(value)
        return

    if keyword == "AUTOLOADINGOFFSET":
        v.autoloadingoffset = floatparameter(value)
        return

    if keyword == "AUTOADDPURGE":
        v.autoaddsplice = True
        return

    if keyword == "POWERCHAOS":   #Special feature request to allow sub 300mm pings
        v.powerchaos = True
        return

    if keyword == "MINSTARTSPLICE":
        v.min_start_splice_length = floatparameter(value)
        if v.min_start_splice_length < 100:
            v.min_start_splice_length = 100
            gui.log_warning("Minimal first slice length adjusted to 100mm")
        return

    if keyword == "BEDSIZEX":
        v.bed_size_x = floatparameter(value)
        v.bed_shape_warning = True
        return

    if keyword == "BEDSIZEY":
        v.bed_size_y = floatparameter(value)
        v.bed_shape_warning = True
        return

    if keyword == "BEDORIGINX":
        v.bed_origin_x = floatparameter(value)
        v.bed_shape_warning = True
        return

    if keyword == "BEDORIGINY":
        v.bed_origin_y = floatparameter(value)
        v.bed_shape_warning = True
        return

    if keyword == "BIGBRAIN3D_BLOBSIZE":
        v.bigbrain3d_blob_size = intparameter(value)
        return

    if keyword == "BIGBRAIN3D_SINGLEBLOB":
        v.single_blob = True
        return

    if keyword == "BIGBRAIN3D_BLOBSPEED":
        v.bigbrain3d_blob_speed = intparameter(value)
        return

    if keyword == "BIGBRAIN3D_COOLINGTIME":
        v.bigbrain3d_blob_cooling_time = intparameter(value)
        return

    if keyword == "BIGBRAIN3D_PURGEPOSITION":
        v.bigbrain3d_x_position = floatparameter(value)
        return

    if keyword == "BIGBRAIN3D_PURGEYPOSITION":
        v.bigbrain3d_y_position = floatparameter(value)
        return

    if keyword == "BIGBRAIN3D_MOTORPOWER_HIGH":
        v.bigbrain3d_motorpower_high = intparameter(value)
        return

    if keyword == "BIGBRAIN3D_MOTORPOWER_NORMAL":
        v.bigbrain3d_motorpower_normal = intparameter(value)
        return

    if keyword == "BIGBRAIN3D_NUMBER_OF_WHACKS":
        v.bigbrain3d_whacks = intparameter(value)
        return

    if keyword == "BIGBRAIN3D_PRIME_BLOBS":
        v.bigbrain3d_prime = intparameter(value)
        return

    if keyword == "BIGBRAIN3D_FAN_OFF_PAUSE":
        v.bigbrain3d_fanoffdelay = intparameter(value)
        return

    if keyword == "BIGBRAIN3D_LEFT_SIDE":
        v.bigbrain3d_left = -1
        return

    if keyword == "BIGBRAIN3D_CLEARANCE_MM":
        v.bigbrain3d_minimalclearenceheight = floatparameter(value)
        return

    if keyword == "BIGBRAIN3D_ENABLE":
        if not v.wipe_remove_sparse_layers:
            v.bigbrain3d_purge_enabled = True
            gui.create_logitem("<b>BIGBRAIN3D Will only work with installed hardware on a Prusa Printer</b>")
        else:
            gui.log_warning("<b>BIGBRAIN3D mode not compatible with sparse wipe tower in PS</b>")
        return

    if keyword == "BIGBRAIN3D_SMARTFAN":
        v.bigbrain3d_smartfan = True
        return

    if keyword == "MINSPLICE":
        v.min_splice_length = floatparameter(value)
        if v.min_splice_length < 70:
            v.min_splice_length = 70
            gui.log_warning("Minimal slice length adjusted to 70mm")
        return

    # LINEAR PING removed

    if keyword == "LINEARPINGLENGTH":
        v.ping_interval = floatparameter(value)
        v.ping_length_multiplier = 1.0
        if not v.powerchaos:
            if v.ping_interval < 300:
                v.ping_interval = 300
                gui.log_warning("Minimal Linear Ping distance is 300mm!  Your config stated: {}".format(value))
            gui.create_logitem("Linear Ping interval of  {:-6.2f}mm".format(v.ping_interval))
        return

    # SIDE TRANSITIONING
    if keyword == "SIDEWIPELOC":
        v.side_wipe_loc = value
        return

    if keyword == "PURGETOPSPEED":
        v.purgetopspeed = int(floatparameter(value))
        gui.create_logitem("Purge Max speed set to {:.0f}mm/min ({}mm/s)".format(v.purgetopspeed, v.purgetopspeed / 60))
        return

    if keyword == "WIPEFEEDRATE":
        v.wipe_feedrate = floatparameter(value)
        return

    if keyword == "SIDEWIPEMINY":
        v.sidewipe_miny = floatparameter(value)
        return

    if keyword == "SIDEWIPEMAXY":
        v.sidewipe_maxy = floatparameter(value)
        return

    if keyword == "SIDEWIPECORRECTION":
        v.sidewipe_correction = floatparameter(value)
        if v.sidewipe_correction < 0.9 or v.sidewipe_correction > 1.10:
            v.sidewipe_correction = 1.0
        return

    if keyword == "PURGETOWERDELTA":
        parm = abs(floatparameter(value))
        if parm > 0.001 and v.wipe_remove_sparse_layers:
            gui.log_warning("TOWER DELTA feature mode not compatible with sparse wipe tower in PS")
            v.max_tower_delta = 0.0
        else:
            if parm != float(0):
                v.max_tower_z_delta = abs(floatparameter(value))
                gui.create_logitem("Max Purge Tower Delta set to {:-2.2f}mm".format(v.max_tower_z_delta))
        return

    if keyword == "FULLPURGEREDUCTION":
        if not v.wipe_remove_sparse_layers:
            gui.create_logitem("Full purge reduction configured")
            v.full_purge_reduction = True
            v.needpurgetower = True
        else:
            gui.log_warning("FULL PURGE TOWER REDUCTION feature mode not compatible with sparse wipe tower in PS")
            v.full_purge_reduction = False
        return

    if keyword == "CHECKVERSION":
        import p2pp.checkversion as cv
        import version
        latest = cv.get_version(cv.MASTER)
        if latest:
            if latest > version.Version:
                gui.create_logitem("New development version of P2PP available ({})".format(latest), "red", False, "2.0")
            else:
                if latest < version.Version:
                    latest = cv.get_version(cv.DEV)
                    if latest > version.Version:
                        gui.create_logitem("New development version of P2PP available ({})".format(latest), "red", False,
                                           "2.0")
        else:
            gui.create_logitem("Could not check for latest online version")

    if keyword == "DO_NOT_GENERATE_M0":
        return
        # this command has been obsoleted as harmful to the print
        v.generate_M0 = False
        return

    if keyword == "CONSOLEWAIT":
        v.consolewait = True
        return

    if keyword == "KLIPPER_TOOLCHANGE":
        v.klipper = True
        return

    if keyword == "IGNOREWARNINGS":
        v.ignore_warnings = True
        return

    if keyword == "ABSOLUTEEXTRUDER":
        v.absolute_extruder = True
        gui.create_logitem("Convert to absolute extrusion parameters")
        return

    if keyword == "DEBUGTCOMMAND":
        v.debug_leaveToolCommands = True
        gui.log_warning("DEBUGTCOMMAND ACTIVE - File will not print correctly!!")
        return
