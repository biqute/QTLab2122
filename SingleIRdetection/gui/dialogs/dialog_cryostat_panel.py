
from PyQt5 import uic
from PyQt5.QtWidgets import QDialog

import resources

import numpy as np


class Ui_Dialog(QDialog):
    def __init__(self, parent):
        self.parent = parent
        super(Ui_Dialog, self).__init__()
        uic.loadUi('cryostat_panel.ui', self)

        # connect valve
        self.valve_1.clicked.connect(
            lambda: self.change_valve(self.valve_1, 10))
        self.valve_2.clicked.connect(
            lambda: self.change_valve(self.valve_2, 16))
        self.valve_3.clicked.connect(
            lambda: self.change_valve(self.valve_3, 13))
        self.valve_4.clicked.connect(
            lambda: self.change_valve(self.valve_4, 12))
        self.valve_5.clicked.connect(
            lambda: self.change_valve(self.valve_5, 11))
        # self.valve_6.clicked.connect(
        #    lambda: self.change_valve(self.valve_6, 16))
        self.valve_7.clicked.connect(
            lambda: self.change_valve(self.valve_7, 3))
        self.valve_8.clicked.connect(
            lambda: self.change_valve(self.valve_8, 2))
        self.valve_9.clicked.connect(
            lambda: self.change_valve(self.valve_9, 1))
        self.valve_10.clicked.connect(
            lambda: self.change_valve(self.valve_10, 15))
        self.valve_11_A.clicked.connect(
            lambda: self.change_valve(self.valve_11_A, 4))
        self.valve_11_B.clicked.connect(
            lambda: self.change_valve(self.valve_11_B, 7))
        # self.valve_12_A.clicked.connect(
        #    lambda: self.change_valve(self.valve_12_A, 04))
        self.valve_12_B.clicked.connect(
            lambda: self.change_valve(self.valve_12_B, 8))
        self.valve_13_A.clicked.connect(
            lambda: self.change_valve(self.valve_13_A, 5))
        self.valve_13_B.clicked.connect(
            lambda: self.change_valve(self.valve_13_B, 6))
        self.valve_14.clicked.connect(
            lambda: self.change_valve(self.valve_14, 14))

        self.valve_1_A.clicked.connect(
            lambda: self.change_valve(self.valve_1_A, 18))
        self.valve_2_A.clicked.connect(
            lambda: self.change_valve(self.valve_2_A, 17))
        self.valve_3_A.clicked.connect(
            lambda: self.change_valve_3A(self.valve_3_A, 21))
        self.valve_4_A.clicked.connect(
            lambda: self.change_valve(self.valve_4_A, 20))
        self.valve_5_A.clicked.connect(
            lambda: self.change_valve(self.valve_5_A, 19))

        # set pumps
        self.pump_4he.toggled.connect(
            lambda: self.change_pump(self.pump_4he, 9))
        self.pump_3he.toggled.connect(
            lambda: self.change_pump(self.pump_3he, 24))
        self.pump_roots.toggled.connect(
            lambda: self.change_pump(self.pump_roots, 22))
        self.pump_noname.toggled.connect(
            lambda: self.change_pump(self.pump_noname, 23))

        self.read_and_update()

        self.show()

    def read_and_update(self):
        answer = self.parent.fridge.execute('X')
        answer = answer[9:15]
        answer = int(answer, 16)
        bin = format(answer, '0>24b')[::-1]

        valve_map = {
            0: self.valve_9,
            1: self.valve_8,
            2: self.valve_7,
            3: self.valve_11_A,
            4: self.valve_13_A,
            5: self.valve_13_B,
            6: self.valve_11_B,
            7: self.valve_12_B,
            8: self.pump_4he,
            9: self.valve_1,
            10: self.valve_5,
            11: self.valve_4,
            12: self.valve_3,
            13: self.valve_14,
            14: self.valve_10,
            15: self.valve_2,
            16: self.valve_2_A,
            17: self.valve_1_A,
            18: self.valve_5_A,
            19: self.valve_4_A,
            20: self.valve_3_A,
            21: self.pump_roots,
            22: self.pump_noname,
            23: self.pump_3he
        }

        for idx, i in enumerate(bin):
            if idx in [8, 21, 22, 23]:
                self.set_status_pump(valve_map[idx], i)
            else:
                self.set_status(valve_map[idx], i)

    def set_status_pump(self, button, status):
        if status == '0':
            button.setChecked(False)
        elif status == '1':
            button.setChecked(True)

    def set_status(self, button, status):
        if status == '0':
            button.setText('\nC')
            button.setStyleSheet("""
                border-image: url(:/main_path/images/valve_closed.png);
                """)
        elif status == '1':
            button.setText('\nO')
            button.setStyleSheet("""
                border-image: url(:/main_path/images/valve_open.png);
                """)

    def change_pump(self, pump, number):
        if pump.isChecked():
            self.parent.fridge.execute('P'+str(2*number))
        else:
            self.parent.fridge.execute('P'+str(2*number+1))

    def change_valve(self, button, number):
        if button.text() == '\nC':
            button.setText('\nO')
            button.setStyleSheet("""
                border-image: url(:/main_path/images/valve_open.png);
                """)
            self.parent.fridge.execute('P'+str(2*number))
        else:
            button.setText('\nC')
            button.setStyleSheet("""
                border-image: url(:/main_path/images/valve_closed.png);
                """)
            self.parent.fridge.execute('P'+str(2*number+1))

    def change_valve_3A(self, button, number):
        if button.text() == '\nO':
            button.setText('\nC')
            button.setStyleSheet("""
                border-image: url(:/main_path/images/valve_closed.png);
                """)
            self.parent.fridge.execute('P'+str(2*number))
        else:
            button.setText('\nO')
            button.setStyleSheet("""
                border-image: url(:/main_path/images/valve_open.png);
                """)
            self.parent.fridge.execute('P'+str(2*number+1))












