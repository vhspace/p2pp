__author__ = 'Tom Van den Eede'
__copyright__ = 'Copyright 2018-2021, Palette2 Splicer Post Processing Project'
__credits__ = ['Tom Van den Eede']
__license__ = 'GPLv3 '
__maintainer__ = 'Tom Van den Eede'
__email__ = 'P2PP@pandora.be'

from PyQt5 import uic
from PyQt5.QtWidgets import QApplication
import image_rc
import config.qdroptarget
import config.qmulticombo
import config.prusaconfig as conf
import sys
import os
import copy

form = None

configs = {"printers": {},
           "prints": {},
           "filaments": {}}

def on_click():
    sys.exit(0)

def create_logitem(text, color="#000000"):
    word = '<span style=\" color: {}\">  {}</span>'.format(color, text)
    form.log.append(word)



def get_config():

    cfg = {}

    ### Prusa config items

    cfg["printers"] = form.printerlist.currentText()
    cfg["prints"] = form.printlist.currentText()
    cfg["filaments"] = form.filamentlist.currentText()

    ## Basic P2PP
    cfg["printerprofile"] = form.printerprofile.text()
    cfg["spliceoffset"] = form.spliceoffset.text()
    cfg["extrafilament"] = form.extrafilament.text()

    cfg["consolewait"] = form.consolewait.isChecked()
    cfg["saveunprocessed"] = form.saveunprocessed.isChecked()
    cfg["absoluteextrusion"] = form.absoluteextruder.isChecked()
    cfg["addmcf"] = form.convertfilename.isChecked()
    cfg["linearpingenable"] = form.linearping_enable.isChecked()
    cfg["linearping"] = form.linearping.text()

    #Sidewipe

    cfg["sw_enable"] = form.sidewipe_enable.isChecked()
    cfg["sw_autoadd"] = form.sidewipe_autoadd.isChecked()
    cfg["sw_xloc"] = form.sw_xloc.text()
    cfg["sw_miny"] = form.sw_miny.text()
    cfg["sw_maxy"] = form.sw_maxy.text()
    cfg["sw_wiperate"] = form.sw_wipeFeedrate.text()


    #BB3D
    cfg["bb_enable"] = form.bb_enable.isChecked()
    cfg["bb_autoadd"] = form.bb3d_autoadd.isChecked()
    cfg["bb_left"] = form.bb3d_left.isChecked()
    cfg["bb_blobsize"] = form.bb3d_blobsize.text()
    cfg["bb_cooling"] = form.bb3d_coolingtime.text()
    cfg["bb_xloc"] = form.bb3d_locx.text()
    cfg["bb_motormin"] = form.bb3d_motorhigh.text()
    cfg["bb_motormax"] = form.bb3d_motorlow.text()
    cfg["bb_fandelay"] = form.bb3d_fanoffdelay.text()
    cfg["bb_priming"] = form.bb3d_primingblobs.text()
    cfg["bb_whacks"] = form.bb3d_whacks.text()

    #Towerdelta
    cfg["tower_enable"] = form.towerdelta.isChecked()
    cfg["tower_maxdelta"] = form.maxdelta.text()

    #Full Purge
    cfg["fp_enable"] = form.fullpurge_enable.isChecked()
    cfg["fp_autoadd"] = form.fp_autoadd.isChecked()
    cfg["fp_wiperate"] = form.fp_wipefeedrate.text()

    #Accessory Mode Palette2
    cfg["accmode_p2"] = form.accmode_p2.isChecked()

    #Accessory Mode Palette+
    cfg["accmode_pplus"] = form.accmode_p2.isChecked()
    cfg["accmode_ppm"] = form.pplusppm.text()
    cfg["accmode_lo"] = form.pplus_loading.text()

    return cfg

def on_config():

    error = 0

    basicconfig = []

    form.toolBox.setCurrentIndex(7)
    create_logitem("Processing started...")
    if not form.backup.isChecked():
        create_logitem("  Make a backup of your current setup before starting", "red")
        create_logitem("  Processing ENDED", "red")
        return

    cfg = get_config()

    create_logitem("Checking supplied infrmation...")

    if cfg["printers"]=="" and cfg["prints"]=="" and cfg["filaments"]=="":
        create_logitem("  Chose at least a printer,  print or filament profile", "red")
        create_logitem("  Processing ENDED", "red")
        return

    if len(cfg["printerprofile"]) != 16:
        create_logitem("  Invalid printer profile is", "red")
        error += 1

    ### LAYERCONFIG
    ###############

    layergcode = [
        ";LAYER [layer_num]",
        ";LAYERHEIGHT [layer_z]"
    ]

    ### BASICCONFIG
    ###############

    basiccode = [
        ";P2PP PRINTERPROFILE={}".format(cfg["printerprofile"]),
        ";P2PP SPLICEOFFSET={}".format(cfg["spliceoffset"]),
        ";P2PP EXTRAENDFILAMENT={}".format(cfg["extrafilament"]),
        ";P2PP MATERIAL_DEFAULT=0_0_0",
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
    ###############

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
    ###################

    bbcode = [
        ";P2PP BIGBRAIN3D_BLOBSIZE = {}".format(cfg["bb_blobsize"]),
        ";P2PP BIGBRAIN3D_COOLINGTIME = {}".format(cfg["bb_cooling"]),
        ";P2PP BIGBRAIN3D_PURGEPOSITION = {}".format(cfg["bb_xloc"]),
        ";P2PP BIGBRAIN3D_MOTORPOWER_HIGH = {}".format(cfg["bb_motormax"]),
        ";P2PP BIGBRAIN3D_MOTORPOWER_NORMAL = {}".format(cfg["bb_motormin"]),
        ";P2PP BIGBRAIN3D_FAN_OFF_DELAY = {}".format(cfg["bb_fandelay"]),
        ";P2PP BIGBRAIN3D_ENABLE",
        ";P2PP BIGBRAIN3D_PRIME_BLOBS = {}".format(cfg["bb_priming"]),
        ";P2PP BIGBRAIN3D_NUMBER_OF_WHACKS = {}".format(cfg["bb_whacks"]) ]

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
        ";P2PP FULLPURGEREDUCTION" 
        ";P2PP WIPEFEEDRATE={}".format(cfg["fp_wiperate"])
    ]

    if cfg["fp_autoadd"]:
        swcode.append(";P2PP AUTOADDPURGE")

    if len(cfg["printers"]) > 0:
        output_printers = cfg["printers"].split(",")
    else:
        output_printers = []

    if len(cfg["prints"]) > 0:
        output_prints= cfg["prints"].split(",")
    else:
        output_prints = []

    if len(cfg["filaments"]) > 0:
        output_filaments = cfg["filaments"].split(",")
    else:
        output_filaments = []



    for i in output_printers:

        create_logitem("Generating config based on pinrter profile {} ".format(i), "blue")
        store = copy.deepcopy(configs["printers"][i])

        store["layer_gcode"] = "\\n".join(layergcode)

        store["single_extruder_multi_material"] = 1

        tmp = store["retract_before_travel"].split(",")
        print(len(tmp))
        if len(tmp) == 1:
            for item in conf.printer_extend_parameters_comma:
                store[item] = ",".join([store[item],store[item],store[item],store[item]])
            for item in conf.printer_extend_parameters_semicolon:
                store[item] = ";".join([store[item],store[item],store[item],store[item]])

        store["start_gcode"] += "\\n"+"\\n".join(basiccode)
        basic_startcode = store["start_gcode"]

        create_logitem("--> BASIC CONFIG")
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

    for i in output_prints:
        create_logitem("Generating config based on print profile {}".format(i))
        store = configs["prints"][i]
        if cfg["addmcf"]:
            name = store["output_filename_format"]
            if ".mcf." not in name:
                store["output_filename_format"] = store["output_filename_format"].replace(".gcode", ".mcf.gcode")
        store["post process"] = conf.scriptname()
        store["single_extruder_multi_material_priming"] = "0"
        store["min_skirt_length"] = "0"
        store["skirts"] = "0"
        conf.writeconfig("print", "P2PP - "+i, store)


    for i in output_filaments:
        create_logitem("Generating config based on  filament profile {}".format(i))
        store = configs["filaments"][i]
        store["compatible_printers_condition"] = "single_extruder_multi_material"
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
        print("Total errors to correct: {}".format(error))





def init_gui():
    global form, configs

    if sys.platform != 'darwin':
            ui = "{}\\p2ppconf.ui".format(os.path.dirname(sys.argv[0]))
    else:
        ui = "p2ppconf.ui"

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
        conf.loadconfig("printer", p, tmpStore )
        p = p[:-4]
        configs["printers"][p] = tmpStore

        try:
            if not tmpStore["single_extruder_multi_material"] == "1":
                form.printerlist.addItem(p)
        except KeyError:
            pass

    prints = conf.get_configs("print")
    prints = [p for p in prints if p.endswith(".ini") ]
    for prt in prints:
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

    form.exitButton.clicked.connect(on_click)
    form.applyConfig.clicked.connect(on_config)
    window.show()
    get_config()
    app.exec()
