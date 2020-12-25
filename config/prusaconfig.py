__author__ = 'Tom Van den Eede'
__copyright__ = 'Copyright 2018-2021, Palette2 Splicer Post Processing Project'
__credits__ = ['Tom Van den Eede']
__license__ = 'GPLv3 '
__maintainer__ = 'Tom Van den Eede'
__email__ = 'P2PP@pandora.be'

import sys
import os
import configparser
import config.config_gui as conf

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
    rval = "unknown"
    if sys.platform == 'darwin':
        rval = "open -W -a P2PP.app --args"
    elif sys.platform == 'windows':
        rval = "{}\\p2pp.exe".format(os.path.dirname(sys.argv[0]).replace(" ", "! "))
    return rval


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


def processdrop( file ):
    return
    config = configparser.ConfigParser()
    if sys.platform == "darwin":
        config.read(file+"Contents/Resources/profiles/PrusaResearch.ini")
        for key in config.__dict__["_sections"].keys():
            if key.startswith("filament:"):
                print(key, config.__dict__["_sections"][key])
                store = config.__dict__["_sections"][key]



def writeconfig( tpe, inifile, store):

    if sys.platform == "windows":
        separator = "\n"
    else:
        separator = "\r\n"
    try:
        file = addtopath(folder(tpe), inifile + ".ini")
        outputfile = open(file, "wb")
        outputfile.write("# Generated config file [{}]with P2PP Configurator {}".format(inifile, separator).encode('ascii'))
        for entry in sorted(store.keys()):
            outputfile.write("{} = {}{}".format(entry , store[entry], separator).encode('ascii'))

    except:
        print("error writing config file {}".format(inifile))


def omega_inspect(file):
    lines = []
    try:
        inf = open(file, "r")
        lines = inf.readlines()
        inf.close()
    except:
        return

    for item in lines:
        item.strip()
        if item.startswith("O22 D") and len(item) == 22:
            conf.form.printerprofile.setText(item[5:21].upper())
            conf.create_logitem("Retrieved printer profile ID {} from {}".format(item[5:21], file))

def retrieveconfig(file):
    pass







