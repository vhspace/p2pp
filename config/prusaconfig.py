__author__ = 'Tom Van den Eede'
__copyright__ = 'Copyright 2018-2021, Palette2 Splicer Post Processing Project'
__credits__ = ['Tom Van den Eede']
__license__ = 'GPLv3 '
__maintainer__ = 'Tom Van den Eede'
__email__ = 'P2PP@pandora.be'

from os import listdir
import sys
import os
import config.config_gui as gui

configs_printers = {}
configs_prints = {}
configs_fiaments = {}


printer_extend_parameters_comma = ["deretract_speed", "extruder_offset", "max_layer_height",
                                   "min_layer_height" , "nozzle_diameter", "retract_before_travel",
                                   "retract_before_wipe", "retract_layer_change", "retract_length",
                                   "retract_length_toolchange", "retract_lift", "retract_lift_above",
                                   "retract_lift_below", "retract_restart_extra", "retract_restart_extra_toolchange",
                                   "retract_speed", "wipe"]
printer_extend_parameters_semicolon = ["extruder_colour" ]


def addtopath( path , addition):
    if sys.platform == 'darwin':
        return path+"/"+addition
    elif sys.platform == 'windows':
        return path + "\\" + addition

def folder(suffix = None):
    if sys.platform == 'darwin':
        folder = os.path.expanduser('~/Library/Application Support/PrusaSlicer')
        if suffix is not None:
            folder = folder + "/" + suffix
    elif sys.platform == 'windows':
        folder = os.path.expanduser('~\\AppData\\Roaming\\PrusaSlicer')
        if suffix is not None:
            folder = folder + "\\" + suffix

    return folder


def scriptname():
    if sys.platform == 'darwin':
        return "open -W -a P2PP.app --args"
    elif sys.platform == 'windows':
        return  "{}\\p2pp.exe".format(os.path.dirname(sys.argv[0]).replace(" ", "! "))


def get_configs(type = None):
    mypath = folder(type)
    return [f for f in os.listdir(mypath) if os.path.isfile(os.path.join(mypath, f))]


def scriptname():
    scriptname ="unknown"
    if sys.platform == 'darwin':
        scriptname = "open -W -a P2PP.app --args"
    elif sys.platform == 'windows':
        scriptname = "{}\\p2pp.exe".format(os.path.dirname(sys.argv[0]).replace(" ", "! "))
    return scriptname


def loadconfig(tpe, inifile, store):
    try:
        file = addtopath(folder(tpe), inifile)
        inputfile = open(file, "r")
        config = inputfile.readlines()
        inputfile.close()

        for line in config:
            if not line.startswith("#"):
                fields = line.split("=",1)
                if len(fields) == 2:
                    store[fields[0].strip()] = fields[1].strip()
    except:
        pass


def writeconfig( tpe, inifile, store):

    if sys.platform == "windows":
        separator = "\n"
    else:
        separator = "\r\n"
    try:
        file = addtopath(folder(tpe), inifile + ".ini")
        outputfile = open(file, "wb")
        outputfile.write("# Generated config file [{}]with P2PP Configurator {}".format(inifile, separator).encode('ascii'))
        for entry in sorted(store.keys):
            outputfile.write("{} = {}{}".format(entry , store[entry], separator).encode('ascii'))
    except:
        print("error writing config file {}".format(inifile))
        pass


def get_config_item( config, name ):

    if config is not None:
        for configline in config:
            if configline.startswitch(name+" = "):
                return (configline[len(name+" = ")])

    return None


def set_config_item(config, name, value):
    if config is not None:
        for configline in config:
            if configline.startswitch(name + " = "):
                configline = name + " = " + value
                return True
    return False

def create_filament_config( name, store ):
    store["compatible_printers_condition"] = "single_extruder_multi_material"
    store["filament_ramming_parameters"] = ""
    store["filament_minimal_purge_on_wipe_tower"] = 0
    store["filament_cooling_final_speed"] = 0
    store["filament_cooling_initial_speed"] = 0
    store["filament_cooling_moves"] = 0
    store["filament_toolchange_delay"] = 0
    store["filament_unload_time"] = 0
    store["filament_unloading_speed"] = 0
    store["filament_unloading_speed_start"] = 0
    writeconfig("filament", name, store)

def create_print_config(name, store):
    store["post process"] = scriptname()
    store["single_extruder_multi_material_priming"] = "0"
    store["min_skirt_length"] = "0"
    store["skirts"] = "0"
    writeconfig("print", name, store)

