
from PyQt5 import uic
from PyQt5.QtWidgets import QDialog

import resources


class Ui_Dialog(QDialog):
    def __init__(self, parent):
        self.parent = parent
        super(Ui_Dialog, self).__init__()
        uic.loadUi('send_commands.ui', self)

        # connect buttons

        self.send_monitor.clicked.connect(self.send_mon)
        self.send_control.clicked.connect(self.send_con)
        self.send_system.clicked.connect(self.send_sys)
        self.send_specialist.clicked.connect(self.send_spec)
        self.send_custom.clicked.connect(self.send_cust)

        self.show()

    def send_mon(self):
        print('send monitor command')
        command = self.combo_monitor.currentText()
        command += self.par_monitor.text()
        res = self.parent.fridge.execute(command)

        self.par_response.setText(res)
        self.sent_command.setText(command)

    def send_con(self):
        print('send control command')
        command = self.combo_control.currentText()
        command += self.par_control.text()
        res = self.parent.fridge.execute(command)

        self.par_response.setText(res)
        self.sent_command.setText(command)

    def send_sys(self):
        print('send system command')
        command = self.combo_system.currentText()
        command += self.par_system.text()
        res = self.parent.fridge.execute(command)

        self.par_response.setText(res)
        self.sent_command.setText(command)

    def send_spec(self):
        print('send specialist command')
        command = self.combo_specialist.currentText()
        command += self.par_specialist.text()
        res = self.parent.fridge.execute(command)

        self.par_response.setText(res)
        self.sent_command.setText(command)

    def send_cust(self):
        print('send custom command')
        command = self.par_custom.text()
        res = self.parent.fridge.execute(command)

        self.par_response.setText(res)
        self.sent_command.setText(command)
