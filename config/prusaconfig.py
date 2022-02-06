__author__ = 'Tom Van den Eede'
__copyright__ = 'Copyright 2018-2022, Palette2 Splicer Post Processing Project'
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
configs_filaments = {}
default_store = {}


printer_extend_parameters_comma = ["deretract_speed", "extruder_offset", "max_layer_height",
                                   "min_layer_height", "nozzle_diameter", "retract_before_travel",
                                   "retract_before_wipe", "retract_layer_change", "retract_length",
                                   "retract_length_toolchange", "retract_lift", "retract_lift_above",
                                   "retract_lift_below", "retract_restart_extra", "retract_restart_extra_toolchange",
                                   "retract_speed", "wipe"]
printer_extend_parameters_semicolon = ["extruder_colour"]


def addtopath(path, addition):
    if sys.platform == 'darwin':
        return path+"/"+addition
    else:
        return path + "\\" + addition


def folder(suffix=None):
    if sys.platform == 'darwin':
        _folder = os.path.expanduser('~/Library/Application Support/PrusaSlicer')
        if suffix is not None:
            _folder = _folder + "/" + suffix
    else:
        _folder = os.path.expanduser('~\\AppData\\Roaming\\PrusaSlicer')
        if suffix is not None:
            _folder = _folder + "\\" + suffix

    return _folder


def scriptname():
    if sys.platform == 'darwin':
        return "open -W -a P2PP.app --args"
    else:
        return "{}\\p2pp.exe".format(os.path.dirname(sys.argv[0]).replace(" ", "! "))


def get_configs(type_=None):
    mypath = folder(type_)
    return [f for f in os.listdir(mypath) if os.path.isfile(os.path.join(mypath, f))]


def load_default_configs():
    global default_store

    def enumerate_section(section):
        sect_store = {}
        for name in c.options(section):
            value = c.get(section, name)
            if name == "inherits":
                inherits = value.split(";")
                for inh in range(len(inherits)):
                    item = prefix + inherits[inh].strip()
                    sect_store.update(enumerate_section(item))
            else:
                sect_store[name] = value

        return sect_store

    default_store.clear()
    cfg_folder = folder("vendor")
    c = configparser.RawConfigParser()
    c.read(os.path.join(cfg_folder, "PrusaResearch.ini"))

    for sect in c.sections():
        pos = sect.find(":")
        if pos > 0:
            prefix = sect[:pos+1]
            if sect[pos+1] == "*" or prefix == "printer_model:":
                continue
        else:
            continue

        default_store[sect.strip()] = enumerate_section(sect)


def add_config(configs):

    for item in default_store.keys():

        ci = default_store[item]

        if item.startswith("filament:"):
            if "MMU" in item or "0.6" in item:
                continue
            nme = "(default) - " + item[len("filament:"):]
            configs["filaments"][nme] = ci

        elif item.startswith("print:"):
            if "0.6" in item:
                continue
            try:
                if 0.1 <= float(ci['layer_height']) <= 0.3:
                    nme = "(default) - " + item[len("print:"):]
                    configs["prints"][nme] = ci
            except KeyError:
                continue

        elif item.startswith("printer:"):
            if "MMU" in item or "0.6" in item:
                continue
            try:
                if not ci['printer_technology'].upper() == "FFF":
                    continue
            except KeyError:
                pass

            nme = "(default) - " + item[len("printer:"):]
            configs["printers"][nme] = ci


def loadconfig(tpe, inifile, store):
    try:
        store.clear()
        file = addtopath(folder(tpe), inifile)
        inputfile = open(file, "r", encoding="utf8")
        config = inputfile.readlines()
        inputfile.close()

        for line in config:
            if not line.startswith("#"):
                fields = line.split("=", 1)
                if len(fields) == 2:
                    store[fields[0].strip()] = fields[1].strip()

    except (IOError, IndexError, KeyError):
        pass


def writeconfig(tpe, inifile, outstore):

    if sys.platform == "darwin":
        separator = "\n"
    else:
        separator = "\r\n"

    inifile = inifile.strip()
    if inifile.startswith("(default) - "):
        inifile = inifile[len("(default) - "):]

    try:
        file = addtopath(folder(tpe), inifile + ".ini")
        outputfile = open(file, "wb")
        outputfile.write("# Generated config file [{}]with P2PP Configurator {}".format(inifile, separator).encode('utf8'))
        for entry in sorted(outstore.keys()):
            outputfile.write("{} = {}{}".format(entry, outstore[entry], separator).encode('utf8'))

    except (IOError, KeyError):
        conf.create_logitem("error writing config file {}".format(inifile), "red")


def setstatus(str):
    conf.form.statusBar.showMessage(str)


def omega_inspect(file):
    try:
        inf = open(file, "r", encoding="utf8")
        lines = inf.readlines()
        inf.close()
    except (IOError, UnicodeDecodeError):
        conf.form.statusBar.showMessage("Could not read from {}".format(file))
        return

    for item in lines:
        pos = item.find("O22 D")
        if pos != -1:
            printerid = item[pos+5:pos+21].upper()
            conf.form.printerprofile.setText(printerid)
            conf.create_logitem("Retrieved printer profile ID {} from {}".format(printerid, file))
            conf.form.statusBar.showMessage("Retrieved printer profile ID {} from {}".format(printerid, file))
            return

    conf.create_logitem("Could not retrieve Printer Profile ID supplied file")
    conf.form.statusBar.showMessage("Could not retrieve Printer Profile ID supplied file")
