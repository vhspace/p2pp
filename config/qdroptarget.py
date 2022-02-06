__author__ = 'Tom Van den Eede'
__copyright__ = 'Copyright 2018-2022, Palette2 Splicer Post Processing Project'
__credits__ = ['Tom Van den Eede']
__license__ = 'GPLv3 '
__maintainer__ = 'Tom Van den Eede'
__email__ = 'P2PP@pandora.be'

from PyQt5.QtWidgets import QPushButton
from PyQt5 import QtCore
import config.prusaconfig as prusaconfig
import sys


class QDropTarget(QPushButton):

    def __init__(self, parent):
        super(QDropTarget, self).__init__(parent)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        data = event.mimeData()
        urls = data.urls()
        if urls and urls[0].scheme() == 'file':
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        data = event.mimeData()
        urls = data.urls()
        if urls and urls[0].scheme() == 'file':
            event.acceptProposedAction()

    def dropEvent(self, event):
        data = event.mimeData()
        urls = data.urls()
        if urls and urls[0].scheme() == 'file':
            filepath = str(urls[0].path())
            if sys.platform != 'darwin':
                filepath = filepath[1:]
            pp = prusaconfig.omega_inspect(filepath)
            event.acceptProposedAction()



