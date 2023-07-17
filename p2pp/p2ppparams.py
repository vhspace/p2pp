__author__ = 'Tom Van den Eede'
__copyright__ = 'Copyright 2018-2022, Palette2 Splicer Post Processing Project'
__credits__ = ['Tom Van den Eede',
               'Tim Brookman'
               ]
__license__ = 'GPLv3'
__maintainer__ = 'Tom Van den Eede'
__email__ = 'P2PP@pandora.be'

import p2pp.gui as gui
import p2pp.variables as v

# SECTION Helper functions


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
    if len(v.splice_algorithm_table) > 0:
        gui.log_warning("Algorithm definitions should appear AFTER Palette Model selection (PALETTE3/PALETTE3_PRO/ACCESSORYMODE_MAF/ACCESSORYMODE_MSF)")


# SECTION P2PP Parameter parsing


def check_config_parameters(keyword, value):
    keyword = keyword.upper().strip()

    if value is None:
        value = ""

    # allows for delaying the change of temperature until after the putge block
    # not sure if this should stay in future releases.   To be evaluated
    #  low complexity, but it adds a waiting position calculation which moves off the regular path.
    if keyword == "TEMPERATURECONTROL":
        v.process_temp = True

    # saves the unprocessed file, so it can be sent for processing simulation in case of errors
    if keyword == "SAVEUNPROCESSED":
        v.save_unprocessed = True

    # enable the preheat function on the Palette 3
    if keyword == "P3_PROCESSPREHEAT":
        v.p3_process_preheat = True

    # enable the preheat function on the Palette 3
    if keyword == "P3_ROTATEINTERFACE":
        v.p3_upside_down = True

    # defines the printer profile for config storage on the Palette hardware
    if keyword == "PRINTERPROFILE":
        value = value.strip(" ")
        _idlen = 16
        if v.palette3:
            _idlen = 32

        if len(value) != _idlen:
            gui.log_warning("Invalid Printer profile!  - Has invalid length (expect {}) - [{}]"
                            .format(_idlen, value))
            value = ""

        if not all(char in set("0123456789ABCDEFabcdef") for char in value):
            gui.log_warning("Invalid Printer profile!  - Invalid characters  (expect 0123456789abcdef) - [{}]"
                            .format(value))
            value = ""

        if len(value) <= _idlen:
            v.printer_profile_string = value
            return

    # toggles hardware to Palette 3 - sets the number of inputs, output format.
    if keyword == "PALETTE3":
        if len(v.printer_profile_string) == 16:
            gui.log_warning("Invalid Printer profile!  - P3 printer profile should be 32 characters ({})".format(v.printer_profile_string))

        v.palette3 = True
        v.colors = 4
        # Min first splice length for P3 == 130
        v.min_start_splice_length = max(v.min_start_splice_length, v.min_first_splice_p3)
        v.min_splice_length = max(v.min_splice_length, v.min_splice_p3)
        check_splice_table()
        return

    # toggles hardware to Palette 3 Pro - sets the number of inputs, output format.
    if keyword == "PALETTE3_PRO":
        if len(v.printer_profile_string) == 16:
            gui.log_warning("Invalid Printer profile!  - P3 printer profile should be 32 characters")

        v.palette3 = True
        v.colors = 8
        # Min first splice length for P3 == 130
        v.min_start_splice_length = max(v.min_start_splice_length, v.min_first_splice_p3)
        v.min_splice_length = max(v.min_splice_length, v.min_splice_p3)
        check_splice_table()
        return

    if keyword == "P3_HOSTNAME":
        v.p3_hostname = value

    if keyword == "P3_PROFILENAME":
        v.p3_printername = value

    if keyword == "P3_UPLOADFILE":
        v.p3_uploadfile = True

    if keyword == "P3_SHOWPRINTERPAGE":
        v.p3_showwebbrowser = True

    # toggles Palette 3 accessory mode = added 22/02/2022
    if keyword == "ACCESSORYMODE_MAFX":
        if not v.palette3:
            gui.log_warning("ACCESSORYMODE_MAFX can only be used with Palette 3!")
            gui.log_warning("This file may not print correctly")

        v.accessory_mode = True
        gui.create_logitem("Config: Palette3 Accessory Mode Selected")
        return


    # toggles Palette 3 accessory mode = added 22/12/2022
    # if keyword == "CONNECTED_ACCESSORYMODE_MAFX":
    #     if not v.palette3:
    #         gui.log_warning("CONNECTED_ACCESSORYMODE_MAFX can only be used with Palette 3!")
    #         gui.log_warning("This file may not print correctly")
    #     v.accessory_mode = True
    #     v.connected_accessory_mode = True
    #     gui.create_logitem("Config: Palette3 Connected Accessory Mode Selected")
    #     gui.create_logitem("This file will only print with Octoprintn and the P3PING plugin configured and enabled!!")
    #     return

    # toggles Palette 2 accessory mode
    if keyword == "ACCESSORYMODE_MAF":
        if v.palette3:
            gui.log_warning("For Palette3 use ACCESSORYMODE_MAFX instead of ACCESSORYMODE_MAF")
            gui.log_warning("This file may not print correctly")


        v.accessory_mode = True
        v.colors = 4
        gui.create_logitem("Config: Palette2 Accessory Mode Selected")
        check_splice_table()
        return

    # toggles Palette + Accessory Mode
    if keyword == "ACCESSORYMODE_MSF":
        if v.palette3:
            gui.log_warning("For Palette3 use ACCESSORYMODE_MAFX instead of ACCESSORYMODE_MSF")
            gui.log_warning("This file may not print correctly")

        v.accessory_mode = True
        v.palette_plus = True
        v.colors = 4
        gui.create_logitem("Config: Palette+ Accessory Mode Selected")
        check_splice_table()
        return

    # Loading Offset - Required for the P+ configuration, take from existing print after callibration with Chroma
    if keyword == "P+LOADINGOFFSET":
        v.palette_plus_loading_offset = int(float(value))
        return

    # PPM  - Required for the P+ configuration, take from existing print after callibration with Chroma
    if keyword == "P+PPM":
        v.palette_plus_ppm = floatparameter(value)
        return

    # Splice offset defines how much the start of the toolchange is located after the position of the toolchange.
    # in general, you want this value as small as possible BUT this value is the buffer you need when material is consumed
    # at a too high rate, so putting it very low may result in early transition
    if keyword == "SPLICEOFFSET":
        v.splice_offset = floatparameter(value)
        gui.create_logitem("SPLICE OFFSET: {:-5.2f}mm".format(v.splice_offset))
        return

    # This parameter sets the amount of extra filament that is generated at the end of the print, to allow for the filament to still
    # engage with the motor gears.   This should be at least the plength of the path from the nozzel to the gears of the extruder motor
    if keyword == "EXTRAENDFILAMENT":
        v.extra_runout_filament = floatparameter(value)
        gui.create_logitem("Extra filament at end of print {:-8.2f}mm".format(v.extra_runout_filament))
        return

    # This parameter specified the minimal amount of total filament  USE ???
    if keyword == "P3_MINIMALTOTALFILAMENT":
        v.minimaltotal_filament = floatparameter(value)
        gui.create_logitem("Minimal ilament length {:-8.2f}mm".format(v.minimaltotal_filament))
        return

    # Specially Added for Manmeet - Not  documented
    if keyword == "MANUAL_SWAP":
        v.manual_filament_swap = True
        gui.create_logitem("Manual filament swap in place.")
        return

    # May be removed ??
    if keyword == "BEFORESIDEWIPEGCODE":
        v.before_sidewipe_gcode.append(value)
        return

    # May be removed ??
    if keyword == "AFTERSIDEWIPEGCODE":
        v.after_sidewipe_gcode.append(value)
        return

    # unused ???
    if keyword == "AUTOLOADINGOFFSET":
        v.autoloadingoffset = floatparameter(value)
        return

    if keyword == "PURGESPEEDADJUST":
        v.purgespeedmultiplier = floatparameter(value)/100.0
        # 10 % trhough 500%
        v.purgespeedmultiplier = min(max(v.purgespeedmultiplier, 0.1), 5.0)

    # autmoaticall adds purge in case of short splices when fullpruereduction is applied
    if keyword == "AUTOADDPURGE":
        v.autoaddsplice = True
        return

    # special reauest feature - not documents - allows for pings shorter than 300 mm
    if keyword == "POWERCHAOS":   # Special feature request to allow sub 300 mm pings
        v.powerchaos = True
        return

    # sets the minimal first splice length (100 / 130 for P2/P3 resp)
    if keyword == "MINSTARTSPLICE":
        v.min_start_splice_length = floatparameter(value)
        if v.palette3:
            if v.min_start_splice_length < v.min_first_splice_p3:
                gui.log_warning("Minimal first slice length adjusted to {}mm for palette 3".format(v.min_first_splice_p3))
                v.min_start_splice_length = v.min_first_splice_p3

        if v.min_start_splice_length < 100:
            v.min_start_splice_length = 100
            gui.log_warning("Minimal first slice length adjusted to 100mm")
        return

    # firmware purge support
    if keyword == "FIRMWARE_PURGE_LENGTH":
        v.firmwarepurge = intparameter(value)
        return

    # SECTION BLOBSTER and BB3D

    # BB3D/BLOBSTER config parm
    if keyword in ["BIGBRAIN3D_BLOBSIZE", "BLOBSTER_BLOBSIZE"]:
        v.mechpurge_blob_size = intparameter(value)
        return

    # BLOBSTER config parm
    if keyword in ["BLOBSTER_ENGAGETIME"]:
        v.blobster_engagetime = intparameter(value)
        return

    # BB3D config parm
    if keyword == "BIGBRAIN3D_SINGLEBLOB":
        v.single_blob = True
        return

    # BB3D/blobster config parm
    if keyword in ["BIGBRAIN3D_BLOBSPEED", "BLOBSTER_BLOBSPEED"]:
        v.mechpurge_blob_speed = intparameter(value)
        return

    # BB3D/blobster config parm
    if keyword in ["BIGBRAIN3D_COOLINGTIME", "BLOBSTER_COOLINGTIME"]:
        v.mechpurge_blob_cooling_time = intparameter(value)
        return

    # BB3D/blobster config parm
    if keyword in ["BIGBRAIN3D_PURGEPOSITION", "BLOBSTER_PURGEPOSITION"]:
        v.mechpurge_x_position = floatparameter(value)
        return

    # BB3D config parm
    if keyword == "BIGBRAIN3D_PURGEYPOSITION":
        v.bigbrain3d_y_position = floatparameter(value)
        return

    # BB3D config parm
    if keyword == "BIGBRAIN3D_MOTORPOWER_HIGH":
        v.bigbrain3d_motorpower_high = intparameter(value)
        return

    # BB3D config parm
    if keyword == "BIGBRAIN3D_MOTORPOWER_NORMAL":
        v.bigbrain3d_motorpower_normal = intparameter(value)
        return

    # BB3D config parm
    if keyword == "BIGBRAIN3D_NUMBER_OF_WHACKS":
        v.bigbrain3d_whacks = intparameter(value)
        return

    # BB3D config parm
    if keyword in ["BIGBRAIN3D_PRIME_BLOBS", "BLOBSTER_PRIME_BLOBS"]:
        v.mechpurge_prime_blobs = intparameter(value)
        return

    # BB3D config parm
    if keyword == "BIGBRAIN3D_FAN_OFF_PAUSE":
        v.bigbrain3d_fanoffdelay = intparameter(value)
        return

    # BB3D config parm
    if keyword == "BIGBRAIN3D_LEFT_SIDE":
        v.bigbrain3d_left = -1
        return

    # BB3D/BLOBSTER config parm
    if keyword in ["BIGBRAIN3D_CLEARANCE_MM", "BLOBSTER_CLEARANCE_MM"]:
        v.mechpurge_minimalclearenceheight = floatparameter(value)
        return

    # BB3D/BLBSTER config parm
    if keyword in ["BIGBRAIN3D_RETRACT", "BLOBSTER_RETRACT"]:
        v.mechpurge_retract = floatparameter(value)
        return

    # BB3D/BLOBSTER config parm
    if keyword == "BIGBRAIN3D_ENABLE":
        if not v.wipe_remove_sparse_layers:
            v.bigbrain3d_purge_enabled = True
            gui.create_logitem("<b>BIGBRAIN3D Will only work with installed hardware on a Prusa Printer</b>")
        else:
            gui.log_warning("<b>BIGBRAIN3D mode not compatible with sparse wipe tower in PS</b>")
        return

    if keyword == "BLOBSTER_ADVANCED":
        v.blobster_advanced = True
        gui.create_logitem("<b>BLOBSTER ADVANCED MODE ENABLED</b>")
        return

    if keyword == "BLOBSTER_ADVANCED_LENGTH":
        v.blobster_advanced_length = []
        fields = value.split(",")
        for i in fields:
            try:
                v.blobster_advanced_length.append(abs(int(i)))
            except ValueError:
                gui.log_warning("BLOBSTER_ADVANCED_LENGTH parameter accepts a list of interger values (length in mm)")
        return

    if keyword == "BLOBSTER_ADVANCED_SPEED":
        v.blobster_advanced_speed = []
        fields = value.split(",")
        for i in fields:
            try:
                v.blobster_advanced_speed.append(abs(int(i)))
            except ValueError:
                gui.log_warning("BLOBSTER_ADVANCED_SPEEDH parameter accepts a list of interger values (length in mm)")
        return

    if keyword == "BLOBSTER_ADVANCED_FAN":
        v.blobster_advanced_fan = []
        fields = value.split(",")
        for i in fields:
            try:
                v.blobster_advanced_fan.append(int(min(abs(int(i)), 100)*2.55))
            except ValueError:
                gui.log_warning("BLOBSTER_ADVANCED_FAN parameter accepts a list of interger values (percentage 0-100)")
        return

    # BB3D/BLOBSTER config parm
    if keyword == "BLOBSTER_ENABLE":
        if not v.wipe_remove_sparse_layers:
            v.blobster_purge_enabled = True
            v.mechpurge_blob_size = 180
            v.mechpurge_minimalclearenceheight = 30
            v.mechpurge_blob_cooling_time = 60

            gui.create_logitem("<b>BLOBSTER Will only work with installed hardware on a Prusa Printer</b>")
        else:
            gui.log_warning("<b>BLOBSTER mode not compatible with sparse wipe tower in PS</b>")
        return

    # BB3D/BLOBSTER config parm
    if keyword in ["BIGBRAIN3D_SMARTFAN", "BLOBSTER_SMARTFAN"]:
        v.mechpurge_smartfan = True
        return

    # defines the minimal splice length ( this is the safe length to make sure a splice is only heated once (70/90 for P2/P3 resp)
    if keyword == "MINSPLICE":
        v.min_splice_length = floatparameter(value)
        if v.palette3:
            if v.min_splice_length < v.min_splice_p3:
                gui.log_warning("Minimal slice length adjusted to {}mm for palette 3".format(v.min_splice_p3))
                v.min_splice_length = v.min_splice_p3

        if v.min_splice_length < 70:
            v.min_splice_length = 70
            gui.log_warning("Minimal slice length adjusted to 70mm")
        return

    # IDEX secondary extruder
    if keyword == "MAPPHYSICALEXTRUDER":
        try:
            fields = value.split(",")
            v.mapphysical = True
            v.mapphysicalfrom=int(floatparameter(fields[0]))
            v.mapphysicalto = int(floatparameter(fields[1]))
        except (IndexError, ValueError):
            gui.log_warning("MAPPHYSICALEXTRUDER - ERROR in parameters {}, should be source,target".format(value))
            v.mapphysical = False

    # LINEAR PING removed

    # set the distance between pings (same length every time), instead of increasing ping lengths
    if keyword == "LINEARPINGLENGTH":
        v.ping_interval = floatparameter(value)
        v.ping_length_multiplier = 1.0
        if not v.powerchaos:
            if v.ping_interval < 100:
                v.ping_interval = 100
                gui.log_warning("Minimal Linear Ping distance is 300mm!  Your config stated: {}".format(value))
            gui.create_logitem("Linear Ping interval of  {:-6.2f}mm".format(v.ping_interval))
        return

    # Set the location for the side wipes
    if keyword == "SIDEWIPELOC":
        v.side_wipe_loc = value
        return

    # define a Z-Hop for jumps to the wipe location
    if keyword == "SIDEWIPEZHOP":
        v.addzop = floatparameter(value)
        gui.create_logitem("Side Wipe ZHOP of {:3.2f}mm".format(v.addzop))

    # maybe removed??
    if keyword == "SIDEWIPEZHOP_SKIPRETURN":
        v.sidewipe_delay_zreturn = True

    # set the highest top speed for purging
    if keyword == "PURGETOPSPEED":
        v.purgetopspeed = int(floatparameter(value))

        # if parameter specified is below 200 then the value is assumed mm/sec and is converted to mm/min
        if v.purgetopspeed < 200:
            v.purgetopspeed = v.purgetopspeed * 60

        gui.create_logitem("Purge Max speed set to {:.0f}mm/min ({}mm/s)".format(v.purgetopspeed, v.purgetopspeed / 60))
        return

    # set the wipe feedrate
    if keyword == "WIPEFEEDRATE":
        v.wipe_feedrate = floatparameter(value)
        return

    # define the sidewipe minimal and macimal Y position
    if keyword == "SIDEWIPEMINY":
        v.sidewipe_miny = floatparameter(value)
        return

    # define the sidewipe minimal and macimal Y position
    if keyword == "SIDEWIPEMAXY":
        v.sidewipe_maxy = floatparameter(value)
        return

    # define a extrusion multiplier for sidewipe.  needed???
    if keyword == "SIDEWIPECORRECTION":
        v.sidewipe_correction = floatparameter(value)
        if v.sidewipe_correction < 0.9 or v.sidewipe_correction > 1.10:
            v.sidewipe_correction = 1.0
        return

    # apply delta (similar to sparse layer removal in PS2.4
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

    # simlir to tower delta but rather reduces the base of the tower to make it growmore evenly with the print
    if keyword == "FULLPURGEREDUCTION":
        if not v.wipe_remove_sparse_layers:
            gui.create_logitem("Full purge reduction configured")
            v.full_purge_reduction = True
            v.needpurgetower = True
        else:
            gui.log_warning("FULL PURGE TOWER REDUCTION feature mode not compatible with sparse wipe tower in PS")
            v.full_purge_reduction = False
        return

    if keyword == "FIRSTTOWERLAYERSPEEDUP":
        v.firsttowerlayerspeedup = True
        return

    # chech the version of P2PP on startup (requires an internet connection)
    if keyword == "CHECKVERSION":
        import p2pp.checkversion as cv
        import version
        latest = cv.get_version(cv.MASTER)
        if latest:
            if latest > version.Version:
                gui.create_logitem("New version of P2PP available ({})".format(latest), "red", False, "2.0")

    # co be removed ?
    if keyword == "DO_NOT_GENERATE_M0":
        v.generate_M0 = False
        return

    # wait for user feedback at the ned of processing
    if keyword == "CONSOLEWAIT":
        v.consolewait = True
        return

    if keyword == "FINISH_MOVES_M400":
        v.finish_moves = "M400"
        v.replace_G4S0 = True

    # process toolchanges the KLIPPER way
    if keyword == "KLIPPER_TOOLCHANGE":
        v.klipper = True
        return

    # close and continue even if there are warnings
    if keyword == "IGNOREWARNINGS":
        v.ignore_warnings = True
        return

    # p2pp_process_file a gcode file with absolute extrusios instead of relative ones
    if keyword == "ABSOLUTEEXTRUDER":
        v.absolute_extruder = True
        gui.create_logitem("Convert to absolute extrusion parameters")
        return

    # unused !!! to be removed.
    if keyword == "DEBUGTCOMMAND":
        v.debug_leaveToolCommands = True
        gui.log_warning("DEBUGTCOMMAND ACTIVE - File will not print correctly!!")
        return
