__author__ = 'Tom Van den Eede'
__copyright__ = 'Copyright 2018-2021, Palette2 Splicer Post Processing Project'
__credits__ = ['Tom Van den Eede']
__license__ = 'GPLv3'
__maintainer__ = 'Tom Van den Eede'
__email__ = 'P2PP@pandora.be'

import sys
import os
import ftplib
import p2pp.variables as v
import p2pp.gui as gui
from PyQt5 import uic, QtCore
# from PyQt5 import QtWebEngineWidgets


def uploadfile(localfile, p3file):
    _error = None

    v.retry_state = True

    while v.p3_hostname == "":
        form.label_5.setText("Please specify hostname or IP.\nP3_HOSTNAME config parameter missing.")
        form.RetryButton.setText("Upload")
        window.show()
        gui.app.exec()
        v.p3_hostname = form.hostname.text()

    form.RetryButton.setText("Retry")



    gui.create_logitem("Sending file {}  to P3 ({})".format(p3file, v.p3_hostname), "blue")
    gui.app.sync()
    while v.retry_state:
        try:

            ftp = ftplib.FTP(v.p3_hostname, timeout=10)
            ftp.login()

            gui.create_logitem("Logged in to :{} ".format(v.p3_hostname))
            gui.app.sync()

            try:
                zipfile = open(localfile, "rb")
                gui.create_logitem("Uploading {}".format(p3file))
                ftp.storbinary("STOR {}".format(p3file), zipfile)
                gui.create_logitem("Upload Completed")
                v.retry_state = False

            except ftplib.all_errors:

                gui.log_warning("Could not send file ({}) to P3 ({})".format(p3file, v.p3_hostname))
                gui.app.sync()
                _error = "Connected to Device but Failed to send file to P3\nFilename: {}".format(p3file)

            except IOError:
                gui.log_warning("Could not send file ({}) to P3 ({})".format(p3file, v.p3_hostname))
                gui.app.sync()
                _error = "Could not open local output file"

            ftp.quit()

            # if v.showwebbrowser:
            #     try:
            #         # todo - change to supplied hostname:5000
            #         # tgtName = "http://{}:5000".format(v.p3_hostname)
            #
            #         tgtName = "http://{}:5000".format("0PLM-P3P")
            #         webform.webBrowser.load(QtCore.QUrl("http://192.168.3.201:5000"))
            #         webwindow.show()
            #         gui.app.exec()
            #
            #     except Exception as e:
            #         gui.logexception(e)

        except ftplib.all_errors:
            gui.log_warning("Could not connect to P3 ({})".format(v.p3_hostname))
            gui.log_warning("Make sure P3 is turned on and connected to the Netwoek")
            gui.app.sync()
            _error = "Cound not connect to P3 ({})\nMake Sure the P3 is turned on and connected to the network".format(v.p3_hostname)

        if _error is not None:
            form.label_5.setText(_error)
            window.show()
            gui.app.exec()
            window.show()
            gui.app.exec()
            v.p3_hostname = form.hostname.text()

    gui.close_button_enable()



def on_clickretry():
    v.retry_state = True
    window.hide()
    # webwindow.hide()
    gui.app.quit()


def on_clickclose():
    # webwindow.hide()
    gui.close_button_enable()


def on_clickabort():
    v.retry_state = False
    gui.create_logitem("Upload aborted by user")
    gui.close_button_enable()
    window.hide()



# LOAD FORM

if sys.platform == 'darwin':
    if len(os.path.dirname(sys.argv[0])) > 0:
        ui = "{}/SendError.ui".format(os.path.dirname(sys.argv[0]))
    else:
        ui = "SendError.ui"
else:
    ui = "SendError.ui"
    if len(os.path.dirname(sys.argv[0])) > 0:
        ui = "{}\\SendError.ui".format(os.path.dirname(sys.argv[0]))
    else:
        ui = "SendError.ui"

Form, Window = uic.loadUiType(ui)
window = Window()
form = Form()
form.setupUi(window)
form.AbortButton.clicked.connect(on_clickabort)
form.RetryButton.clicked.connect(on_clickretry)

# if sys.platform == 'darwin':
#     if len(os.path.dirname(sys.argv[0])) > 0:
#         ui = "{}/p3browser.ui".format(os.path.dirname(sys.argv[0]))
#     else:
#         ui = "p3browser.ui"
# else:
#     ui = "p3browser.ui"
#     if len(os.path.dirname(sys.argv[0])) > 0:
#         ui = "{}\\p3browser.ui".format(os.path.dirname(sys.argv[0]))
#     else:
#         ui = "p3browser.ui"
#
# WebForm, WebWindow = uic.loadUiType(ui)
# webwindow = WebWindow()
#
# webwindow.setWindowFlags(webwindow.windowFlags() | QtCore.Qt.CustomizeWindowHint)
# webwindow.setWindowFlags(webwindow.windowFlags() & ~QtCore.Qt.WindowCloseButtonHint)
#
# webform = WebForm()
# webform.setupUi(webwindow)
# webform.closeButton.clicked.connect(on_clickclose)



