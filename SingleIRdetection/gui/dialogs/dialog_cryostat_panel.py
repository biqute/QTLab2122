
from PyQt5 import uic
from PyQt5.QtWidgets import QDialog

import resources


class Ui_Dialog(QDialog):
    def __init__(self, parent):
        self.parent = parent
        super(Ui_Dialog, self).__init__()
        uic.loadUi('cryostat_panel.ui', self)

        self.show()
