__author__ = 'Tom Van den Eede'
__copyright__ = 'Copyright 2018-2022, Palette2 Splicer Post Processing Project'
__credits__ = ['Tom Van den Eede']
__license__ = 'GPLv3 '
__maintainer__ = 'Tom Van den Eede'
__email__ = 'P2PP@pandora.be'

from PyQt5 import uic
from PyQt5.QtWidgets import QApplication
# following imports are needed to run the program.  DO NOT REMOVE
import image_rc
import config.qdroptarget
import config.qmulticombo
import config.prusaconfig as conf
import sys
import os
import copy
import pickle
import traceback

form = None

configs = {"printers": {},
           "prints": {},
           "filaments": {}}


def on_click():
    sys.exit(0)


def create_logitem(text, color="#000000"):
    word = '<span style=\" color: {}\">  {}</span>'.format(color, text)
    form.log.append(word)


def config_file():
    cfile = "lastconf.conf"

    if sys.platform != 'darwin':
        if len(os.path.dirname(sys.argv[0])) > 0:
            cfile = "{}\\p2ppconf.ui".format(os.path.dirname(sys.argv[0]))

    return cfile


def set_config():
    try:
        cfg = pickle.load(open(config_file(), "rb"))
    except (KeyError, FileNotFoundError, IOError):
        return

    # Basic P2PP
    try:
        form.printerprofile.setText(cfg["printerprofile"])
    except KeyError:
        pass
    try:
        form.spliceoffset.setText(cfg["spliceoffset"])
    except KeyError:
        pass
    try:
        form.extrafilament.setText(cfg["extrafilament"])
    except KeyError:
        pass
    try:
        form.consolewait.setChecked(cfg["consolewait"])
    except KeyError:
        pass
    try:
        form.saveunprocessed.setChecked(cfg["saveunprocessed"])
    except KeyError:
        pass
    try:
        form.absoluteextruder.setChecked(cfg["absoluteextrusion"])
    except KeyError:
        pass
    try:
        form.convertfilename.setChecked(cfg["addmcf"])
    except KeyError:
        pass
    try:
        form.linearping_enable.setChecked(cfg["linearpingenable"])
    except KeyError:
        pass
    try:
        form.linearping.setText(cfg["linearping"])
    except KeyError:
        pass

    # MATERIALS

    try:
        form.materials.setText(cfg["materials"].replace("\\n", "\n"))
    except KeyError:
        pass

    # Sidewipe
    try:
        form.sidewipe_enable.setChecked(cfg["sw_enable"])
    except KeyError:
        pass
    try:
        form.sidewipe_autoadd.setChecked(cfg["sw_autoadd"])
    except KeyError:
        pass
    try:
        form.sw_xloc.setText(cfg["sw_xloc"])
    except KeyError:
        pass
    try:
        form.sw_miny.setText(cfg["sw_miny"])
    except KeyError:
        pass
    try:
        form.sw_maxy.setText(cfg["sw_maxy"])
    except KeyError:
        pass
    try:
        form.sw_wipeFeedrate.setText(cfg["sw_wiperate"])
    except KeyError:
        pass

    # BB3D
    try:
        form.bb_enable.setChecked(cfg["bb_enable"])
    except KeyError:
        pass
    try:
        form.bb3d_autoadd.setChecked(cfg["bb_enable"])
    except KeyError:
        pass
    try:
        form.bb3d_left.setChecked(cfg["bb_left"])
    except KeyError:
        pass
    try:
        form.bb3d_blobsize.setText(cfg["bb_blobsize"])
    except KeyError:
        pass
    try:
        form.bb3d_coolingtime.setText(cfg["bb_cooling"])
    except KeyError:
        pass
    try:
        form.bb3d_locx.setText(cfg["bb_xloc"])
    except KeyError:
        pass
    try:
        form.bb3d_motorhigh.setText(cfg["bb_motormax"])
    except KeyError:
        pass
    try:
        form.bb3d_motorlow.setText(cfg["bb_motormin"])
    except KeyError:
        pass
    try:
        form.bb3d_fanoffdelay.setText(cfg["bb_fandelay"])
    except KeyError:
        pass
    try:
        form.bb3d_primingblobs.setText(cfg["bb_priming"])
    except KeyError:
        pass
    try:
        form.bb3d_whacks.setText(cfg["bb_whacks"])
    except KeyError:
        pass

    # Towerdelta
    try:
        form.towerdelta.setChecked(cfg["tower_enable"])
    except KeyError:
        pass
    try:
        form.maxdelta.setText(cfg["tower_maxdelta"])
    except KeyError:
        pass

    # Full Purge
    try:
        form.fullpurge_enable.setChecked(cfg["fp_enable"])
    except KeyError:
        pass
    try:
        form.fp_autoadd.setChecked(cfg["fp_autoadd"])
    except KeyError:
        pass
    try:
        form.fp_wipefeedrate.setText(cfg["fp_wiperate"])
    except KeyError:
        pass

    # Accessory Mode Palette2
    try:
        form.accmode_p2.setChecked(cfg["accmode_p2"])
    except KeyError:
        pass

    # Accessory Mode Palette+
    try:
        form.accmode_p2.setChecked(cfg["accmode_pplus"])
    except KeyError:
        pass
    try:
        form.pplusppm.setText(cfg["accmode_ppm"])
    except KeyError:
        pass
    try:
        form.pplus_loading.setText(cfg["accmode_lo"])
    except KeyError:
        pass

    form.statusBar.showMessage("Retrieved previous confniguration")


def get_config():

    cfg = {"printers": [form.printerlist.currentText()],
           "prints":  form.printlist.currentData(),
           "filaments": form.filamentlist.currentData(),
           "printerprofile": form.printerprofile.text(),
           "spliceoffset": form.spliceoffset.text(),
           "extrafilament": form.extrafilament.text(),
           "consolewait": form.consolewait.isChecked(),
           "saveunprocessed": form.saveunprocessed.isChecked(),
           "absoluteextrusion": form.absoluteextruder.isChecked(),
           "addmcf": form.convertfilename.isChecked(),
           "linearpingenable": form.linearping_enable.isChecked(),
           "linearping": form.linearping.text(),
           "materials": form.materials.toPlainText().replace("\n", "\\n"),
           "sw_enable": form.sidewipe_enable.isChecked(),
           "sw_autoadd": form.sidewipe_autoadd.isChecked(),
           "sw_xloc": form.sw_xloc.text(),
           "sw_miny": form.sw_miny.text(),
           "sw_maxy": form.sw_maxy.text(),
           "sw_wiperate": form.sw_wipeFeedrate.text(),
           "bb_enable": form.bb_enable.isChecked(),
           "bb_autoadd": form.bb3d_autoadd.isChecked(),
           "bb_autoadd": form.bb3d_autoadd.isChecked(),
           "bb_left": form.bb3d_left.isChecked(),
           "bb_blobsize": form.bb3d_blobsize.text(),
           "bb_cooling": form.bb3d_coolingtime.text(),
           "bb_xloc": form.bb3d_locx.text(),
           "bb_motormin": form.bb3d_motorlow.text(),
           "bb_motormax": form.bb3d_motorhigh.text(),
           "bb_fandelay": form.bb3d_fanoffdelay.text(),
           "bb_priming": form.bb3d_primingblobs.text(),
           "bb_whacks": form.bb3d_whacks.text(),
           "tower_enable": form.towerdelta.isChecked(),
           "tower_maxdelta": form.maxdelta.text(),
           "fp_enable": form.fullpurge_enable.isChecked(),
           "fp_autoadd": form.fp_autoadd.isChecked(),
           "fp_wiperate": form.fp_wipefeedrate.text(),
           "accmode_p2": form.accmode_p2.isChecked(),
           "accmode_pplus": form.accmode_p2.isChecked(),
           "accmode_ppm": form.pplusppm.text(),
           "accmode_lo": form.pplus_loading.text()
    }

    if cfg["printers"] is None or cfg["printers"] == "":
        cfg["printers"] = []

    if cfg["prints"] is None:
        cfg["prints"] = []

    if cfg["filaments"] is None:
        cfg["filaments"] = []

    if float(cfg["linearping"]) < 350:
        cfg["linearping"] = "350"

    try:
        cfile = config_file()
        pickle.dump(cfg, open(cfile, "wb"))
    except IOError:
        pass

    return cfg


def remove_p2ppconfig(store):

    removeditems = [";P2PP PRINTERPROFILE",
                    ";P2PP SPLICEOFFSET",
                    ";P2PP EXTRAENDFILAMENT",
                    ";P2PP MATERIAL_DEFAULT",
                    ";P2PP LINEARPINGLENGTHT",
                    ";P2PP CONSOLEWAIT",
                    ";P2PP SAVEUNPROCESSED",
                    ";P2PP SIDEWIPE",
                    ";P2PP WIPEFEEDRATE",
                    ";P2PP AUTOADDPURGE",
                    ";P2PP BIGBRAIN3D",
                    ";P2PP PURGETOWERDELTA",
                    ";P2PP FULLPURGEREDUCTION",
                    ";P2PP ACCESSORYMODE",
                    ";P2PP P+PPM",
                    ";P2PP P+LOADINGOFFSET",
                    ]
    try:
        gcodelines = store["start_gcode"].split("\\n")
        result = []
        for line in gcodelines:
            removed = False
            if line.startswith(";P2PP"):
                for rlin in removeditems:
                    if rlin in line:
                        removed = True
                        break
            if not removed:
                result.append(line)
            else:
                create_logitem("Previous config line removed: {}".format(line), "blue")
        store["startup_gcode"] = "\\n".join(result)
    except KeyError:
        pass


def on_config():

    error = 0

    updated_prints = 0
    updated_printers = 0
    updated_filaments = 0

    # form.toolBox.setCurrentIndex(7)
    try:
        create_logitem("Processing started...")
        form.statusBar.showMessage("Processing...")
        if not form.backup.isChecked():
            create_logitem("  Make a backup of your current setup before starting", "red")
            create_logitem("  Processing ENDED", "red")
            form.statusBar.showMessage("Processing Error occurred - Backup not confirmed")
            form.toolBox.setCurrentIndex(7)
            return

        cfg = get_config()

        create_logitem("Checking supplied information...")

        if cfg["printers"] == [] and cfg["prints"] == [] and cfg["filaments"] == []:
            create_logitem("  Chose at least a printer,  print or filament profile", "red")
            create_logitem("  Processing ENDED", "red")
            form.statusBar.showMessage("Processing Error occurred - No item selected")
            form.toolBox.setCurrentIndex(7)
            return

        if len(cfg["printerprofile"]) != 16:
            create_logitem("  Invalid printer profile ID", "red")
            form.statusBar.showMessage("Processing Error occurred - Invalid printer profile ID")
            form.toolBox.setCurrentIndex(7)
            error += 1

        # LAYERCONFIG

        layergcode = [
            ";LAYER [layer_num]",
            ";LAYERHEIGHT [layer_z]"
        ]

        # BASICCONFIG

        basiccode = [
            ";P2PP PRINTERPROFILE={}".format(cfg["printerprofile"]),
            ";P2PP SPLICEOFFSET={}".format(cfg["spliceoffset"]),
            ";P2PP EXTRAENDFILAMENT={}".format(cfg["extrafilament"]),
            cfg["materials"]

        ]

        if cfg["linearpingenable"]:
            basiccode.append(";P2PP LINEARPINGLENGTHT={}".format(cfg["linearping"]))

        if cfg["consolewait"]:
            basiccode.append(";P2PP CONSOLEWAIT")

        if cfg["saveunprocessed"]:
            basiccode.append(";P2PP SAVEUNPROCESSED")

        if cfg["absoluteextrusion"]:
            basiccode.append(";P2PP ABSOLUTEEXTRUDER")

        # sidewipe code

        swcode = [
            ";P2PP SIDEWIPELOC=X{}".format(cfg["sw_xloc"]),
            ";P2PP SIDEWIPEMINY={}".format(cfg["sw_miny"]),
            ";P2PP SIDEWIPEMAXY={}".format(cfg["sw_maxy"]),
            ";P2PP WIPEFEEDRATE={}".format(cfg["sw_wiperate"])
        ]

        if cfg["sw_maxy"] == cfg["sw_miny"]:
            cfg["sw_wiperate"] = "200"

        if cfg["sw_autoadd"]:
            swcode.append(";P2PP AUTOADDPURGE")

        # big brain 3d code

        bbcode = [
            ";P2PP BIGBRAIN3D_BLOBSIZE = {}".format(cfg["bb_blobsize"]),
            ";P2PP BIGBRAIN3D_COOLINGTIME = {}".format(cfg["bb_cooling"]),
            ";P2PP BIGBRAIN3D_PURGEPOSITION = {}".format(cfg["bb_xloc"]),
            ";P2PP BIGBRAIN3D_MOTORPOWER_HIGH = {}".format(cfg["bb_motormax"]),
            ";P2PP BIGBRAIN3D_MOTORPOWER_NORMAL = {}".format(cfg["bb_motormin"]),
            ";P2PP BIGBRAIN3D_FAN_OFF_DELAY = {}".format(cfg["bb_fandelay"]),
            ";P2PP BIGBRAIN3D_ENABLE",
            ";P2PP BIGBRAIN3D_PRIME_BLOBS = {}".format(cfg["bb_priming"]),
            ";P2PP BIGBRAIN3D_NUMBER_OF_WHACKS = {}".format(cfg["bb_whacks"])]

        if cfg["bb_left"]:
            bbcode.append(";P2PP BIGBRAIN3D_LEFT_SIDE")

        if cfg["bb_autoadd"]:
            bbcode.append(";P2PP AUTOADDPURGE")

        # tower delta
        #############

        twcode = [
            ";P2PP PURGETOWERDELTA={}".format(cfg["tower_maxdelta"])
        ]

        # full purge
        #############

        fpcode = [
            ";P2PP FULLPURGEREDUCTION",
            ";P2PP WIPEFEEDRATE={}".format(cfg["fp_wiperate"])
        ]

        if cfg["fp_autoadd"]:
            swcode.append(";P2PP AUTOADDPURGE")

        for i in cfg["printers"]:

            i = i.strip()
            if len(i) > 0:
                updated_printers += 1
                create_logitem("Generating config based on pinrter profile {} ".format(i), "blue")

                store = copy.deepcopy(configs["printers"][i])


                remove_p2ppconfig(store)

                store["layer_gcode"] = "\\n".join(layergcode)

                store["single_extruder_multi_material"] = 1

                tmp = store["retract_before_travel"].split(",")
                if len(tmp) == 1:
                    for item in conf.printer_extend_parameters_comma:
                        try:
                            store[item] = ",".join([store[item], store[item], store[item], store[item]])
                        except KeyError:
                            pass
                    for item in conf.printer_extend_parameters_semicolon:
                        try:
                            store[item] = ";".join([store[item], store[item], store[item], store[item]])
                        except KeyError:
                            pass

                store["start_gcode"] += "\\n"+"\\n".join(basiccode)
                basic_startcode = store["start_gcode"]

                create_logitem("--> BASIC CONFIG")

                if i.startswith("P2PP"):
                    i = i.replace("P2PP - Basic -", "")
                    i = i.replace("P2PP - SideWipe -", "")
                    i = i.replace("P2PP - BB3D -", "")
                    i = i.replace("P2PP - TowerDelta -", "")
                    i = i.replace("P2PP - FullPurge -", "")
                    i = i.replace("P2PP - P2 AccMode -", "")
                    i = i.replace("P2PP - PPlus AccMode -", "")

                conf.writeconfig("printer", "P2PP - Basic -" + i, store)

                if cfg["sw_enable"]:
                    create_logitem("--> SideWipe CONFIG")
                    store["start_gcode"] = basic_startcode + "\\n" + "\\n".join(swcode)
                    conf.writeconfig("printer", "P2PP - SideWipe -" + i, store)

                if cfg["bb_enable"]:
                    create_logitem("--> BigBrain 3D CONFIG")
                    store["start_gcode"] = basic_startcode + "\\n" + "\\n".join(bbcode)
                    conf.writeconfig("printer", "P2PP - BB3D -" + i, store)

                if cfg["tower_enable"]:
                    create_logitem("--> Tower Delta CONFIG")
                    store["start_gcode"] = basic_startcode + "\\n" + "\\n".join(twcode)
                    conf.writeconfig("printer", "P2PP - TowerDelta -" + i, store)

                if cfg["fp_enable"]:
                    create_logitem("--> Full Purge Reduction CONFIG")
                    store["start_gcode"] = basic_startcode + "\\n" + "\\n".join(fpcode)
                    conf.writeconfig("printer", "P2PP - FullPurge -" + i, store)

                if cfg["accmode_p2"]:
                    create_logitem("--> P2PP Accessory Mode Config")
                    store["start_gcode"] = basic_startcode + "\\n; ;P2PP ACCESSORYMODE_MAF"
                    conf.writeconfig("printer", "P2PP - P2 AccMode -" + i, store)

                if cfg["accmode_pplus"]:
                    create_logitem("--> P2PP Accessory Mode Config")
                    basic_startcode = basic_startcode + "\\n;P2PP ACCESSORYMODE_MSF"
                    basic_startcode = basic_startcode + "\\n;P2PP P+PPM={}".format(cfg["accmode_ppm"])
                    basic_startcode = basic_startcode + "\\n;P2PP P+LOADINGOFFSET={}".format(cfg["accmode_lo"])
                    store["start_gcode"] = basic_startcode

                    store["extra_loading_move"] = 0
                    store["cooling_tube_length"] = 0
                    store["cooling_tube_retraction"] = 0
                    store["parking_pos_retraction"] = 0

                    conf.writeconfig("printer", "P2PP - PPlus AccMode -" + i, store)

        for i in cfg["prints"]:
            i = i.strip()
            updated_prints += 1
            create_logitem("Generating config based on print profile {}".format(i))
            store_prt = copy.deepcopy(configs["prints"][i])

            if cfg["addmcf"]:
                name = store_prt["output_filename_format"]
                if ".mcf." not in name:
                    store_prt["output_filename_format"] = store_prt["output_filename_format"].replace(".gcode", ".mcf.gcode")
            store_prt["post process"] = conf.scriptname()
            store_prt["single_extruder_multi_material_priming"] = "0"
            store_prt["min_skirt_length"] = "0"
            store_prt["skirts"] = "0"
            store_prt["compatible_printers_condition"] = ""
            conf.writeconfig("print", "P2PP - "+i, store_prt)

        for i in cfg["filaments"]:
            i = i.strip()
            updated_filaments += 1
            create_logitem("Generating config based on  filament profile {}".format(i))
            store = copy.deepcopy(configs["filaments"][i])
            store["compatible_printers_condition"] = ""
            store["filament_ramming_parameters"] = "10 10| 0.05 6.6 0.45 6.8 0.95 7.8 1.45 8.3 1.95 9.7 2.45 10 2.95 7.6 3.45 7.6 3.95 7.6 4.45 7.6 4.95 7.6"
            store["filament_minimal_purge_on_wipe_tower"] = 0
            store["filament_cooling_final_speed"] = 0
            store["filament_cooling_initial_speed"] = 0
            store["filament_cooling_moves"] = 0
            store["filament_toolchange_delay"] = 0
            store["filament_unload_time"] = 0
            store["filament_unloading_speed"] = 0
            store["filament_unloading_speed_start"] = 0
            store["filament_loading_speed"] = 0
            store["filament_loading_speed_start"] = 0
            conf.writeconfig("filament", "P2PP - "+i, store)

        if error > 0:
            create_logitem("Total errors to correct: {}".format(error), "red")

        create_logitem("Updated {} printer, {} print and {} filament profiles".format(updated_printers, updated_prints, updated_filaments))

        form.statusBar.showMessage("Processing Completed, see log panel for info")

    except Exception as e:
        create_logitem("We're sorry but an unexpected error occurred while processing your file", "red")
        create_logitem("Please sumbit an issue report on https://github.com/tomvandeneede/p2pp","red")
        create_logitem(" ")
        create_logitem("<b>Error:</b> {}".format(e))
        tb = traceback.format_tb(e.__traceback__)
        create_logitem(" ")
        create_logitem("<b>Traceback Info:</b>")
        for line in tb:
            create_logitem("{}".format(line))


def populate_dropdowns():
    global form, configs

    check = form.includeDefault.isChecked()

    form.printerlist.clear()
    for printer in configs["printers"].keys():
        if check or not printer.startswith("(default) -"):
            form.printerlist.addItem(printer)
    form.printerlist.setCurrentIndex(-1)

    form.printlist.clear()
    for prnt in configs["prints"].keys():
        if check or not prnt.startswith("(default) -"):
            form.printlist.addItem(prnt)
    form.printlist.setCurrentIndex(-1)

    form.filamentlist.clear()
    for filament in configs["filaments"].keys():
        if check or not filament.startswith("(default) -"):
            form.filamentlist.addItem(filament)
    form.filamentlist.setCurrentIndex(-1)


def init_gui():
    global form, configs

    ui = "p2ppconf.ui"

    if sys.platform != 'darwin':
        if len(os.path.dirname(sys.argv[0])) > 0:
            ui = "{}\\p2ppconf.ui".format(os.path.dirname(sys.argv[0]))

    Form, Window = uic.loadUiType(ui)
    app = QApplication([])
    window = Window()
    form = Form()
    form.setupUi(window)

    printers = conf.get_configs("printer")
    for p in printers:
        if not p.endswith(".ini"):
            continue
        tmpStore = {}
        conf.loadconfig("printer", p, tmpStore)
        p = p[:-4]
        configs["printers"][p] = tmpStore
        # try:
        #     if not tmpStore["single_extruder_multi_material"] == "1":
        form.printerlist.addItem(p)
        # except KeyError:
        #     pass

    prints = conf.get_configs("print")
    prints = [p for p in prints if p.endswith(".ini")]
    for prt in prints:
        tmpStore = {}
        conf.loadconfig("print", prt, tmpStore)
        prt = prt[:-4]
        form.printlist.addItem(prt)
        configs["prints"][prt] = tmpStore

    filaments = conf.get_configs("filament")
    filaments = [p for p in filaments if p.endswith(".ini")]

    for fil in filaments:
        tmpStore = {}
        conf.loadconfig("filament", fil, tmpStore)
        # filter for 1.75mm filaments only  1.65 -- 1.85
        try:
            if abs(float(tmpStore["filament_diameter"]) - 1.75) < 0.10:
                fil = fil[:-4]
                form.filamentlist.addItem(fil)
                configs["filaments"][fil] = tmpStore
        except:
            pass

    conf.load_default_configs()
    conf.add_config(configs)
    populate_dropdowns()
    set_config()
    form.includeDefault.stateChanged.connect(populate_dropdowns)
    form.exitButton.clicked.connect(on_click)
    form.applyConfig.clicked.connect(on_config)
    form.toolBox.setCurrentIndex(0)
    form.printerlist.setCurrentIndex(-1)
    window.show()
    get_config()
    app.exec()
