__author__ = 'Tom Van den Eede'
__copyright__ = 'Copyright 2018-2021, Palette2 Splicer Post Processing Project'
__credits__ = ['Tom Van den Eede']
__license__ = 'GPLv3 '
__maintainer__ = 'Tom Van den Eede'
__email__ = 'P2PP@pandora.be'

from PyQt5 import uic
from PyQt5.QtWidgets import QApplication
import image_rc
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
    warning = 0

    basicconfig = []

    form.toolBox.setCurrentIndex(7)
    create_logitem("Processing started...")
    if not form.backup.isChecked():
        create_logitem("  Make a backup of your current setup before starting", "red")
        create_logitem("  Processing ENDED", "red")
        return

    cfg = get_config()

    create_logitem("Checking supplied infrmation...")

    if cfg["printers"]=="" or cfg["prints"]=="" or cfg["filaments"]=="":
        create_logitem("  Chose at least 1 printer, 1 print and 1 filament profile", "red")
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
        ";P2PP EXTRAENDFILAMENT=".format(cfg["extrafilament"]),
        ";P2PP MATERIAL_DEFAULT=0_0_0",
    ]

    if cfg["linearpingenable"]:
        basiccode.append(";P2PP EXTRAENDFILAMENT=".format(cfg["linearping"]))

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
        ";P2PP IGBRAIN3D_PRIME_BLOBS = {}".format(cfg["bb_priming"]),
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

    output_printers = cfg["printers"].split(",")
    output_prints= cfg["prints"].split(",")
    output_filaments = cfg["filaments"].split(",")



    for i in output_printers:
        try:
            create_logitem("Generating config based on pinrter profile {}".format(i),"blue")
            cofg = copy.deepcopy(configs["printers"][i])

            cofg["single_extruder_single_extruder_multi_material"] = 1

            tmp = cofg["retract_before_travel"].split(",")
            if len(tmp) == 1:
                for i in conf.printer_extend_parameters_comma:
                    cofg[i] = ",".join([cofg[i]]*4)
                for i in conf.printer_extend_parameters_semicolon:
                    cofg[i] = ";".join([cofg[i]] * 4)



            cofg["start_gcod"] += "\\n"+"\\n".join(basiccode)
            basic_startcode = cfg["start_gcod"]

            create_logitem("--> BASIC CONFIG}")
            conf.writeconfig("printer", i, cofg)

            if cfg["sw_enable"]:
                create_logitem("--> SideWipe CONFIG}")
                cofg["start_gcod"] = basic_startcode + "\\n" + "\\n".join(swcode)
                conf.writeconfig("printer","SideWipe "+ i, cofg)

            if cfg["bb_enable"]:
                create_logitem("--> BigBrain 3D CONFIG}")
                cofg["start_gcod"] = basic_startcode + "\\n" + "\\n".join(bbcode)
                conf.writeconfig("printer", "BB3D " + i, cofg)

            if cfg["tower_enable"]:
                create_logitem("--> Tower Delta CONFIG}")
                cofg["start_gcod"] = basic_startcode + "\\n" + "\\n".join(twcode)
                conf.writeconfig("printer", "TowerDelta " + i, cofg)

            if cfg["fp_enable"]:
                create_logitem("--> Full Purge Reduction CONFIG}")
                cofg["start_gcod"] = basic_startcode + "\\n" + "\\n".join(fpcode)
                conf.writeconfig("printer", "FullPurge " + i, cofg)

        except:
            create_logitem("Missing info for {}".format(i), "red")


    for i in output_prints:
        cofg = configs["prints"][i]
        cofg["layer_gcode"] = "\\n".join(layergcode)
        if cfg["addmcf"]:
            name = cofg["output_filename_format"]
            if ".mcf." not in name:
                cofg["output_filename_format"] = cofg["output_filename_format"].replace(".gcode", ".mcf.gcode")

        create_logitem("Generating config based on  print profile {}".format(i))
        conf.create_print_config("P2PP - "+i, cofg)

    for i in output_filaments:
        cofg = configs["filaments"][i]
        create_logitem("Generating config based on  filament profile {}".format(i))
        conf.create_filament_config("P2PP - "+i, cofg)

    if error > 0:
        print("Total errors to correct: {}".format(error))





def init_gui():
    global form



    prefix = 'P2PP - '

    if sys.platform != 'darwin':
            ui = "{}\\p2ppconf.ui".format(os.path.dirname(sys.argv[0]))
    else:
        ui = "p2ppconf.ui"

    Form, Window = uic.loadUiType(ui)
    app = QApplication([])
    window = Window()
    form = Form()
    form.setupUi(window)
    # form.h.addWidget(QDroptarget("DROP\nAPP\nHERE"))

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
                configs["filament"][fil] = tmpStore
        except:
            pass

    form.exitButton.clicked.connect(on_click)
    form.applyConfig.clicked.connect(on_config)
    window.show()

    get_config()
    app.exec()
