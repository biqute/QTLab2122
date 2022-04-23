import numpy as np
import csv

from datetime import datetime

from PyQt5 import uic, QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QDialog

import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

matplotlib.use('Qt5Agg')

class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super(MplCanvas, self).__init__(self.fig)

    def my_plot(self, x, y):
        self.axes.cla()
        self.axes.plot(x, y, 'r')
        self.axes.set_xlabel('t')
        self.fig.canvas.draw_idle()

class Ui_Dialog(QDialog):

    def setupUi(self, Dialog, parent):
        self.parent = parent
        Dialog.setObjectName("Dialog")
        Dialog.resize(639, 530)
        self.gridLayout = QtWidgets.QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.resetButton = QtWidgets.QPushButton(Dialog)
        self.resetButton.setMinimumSize(QtCore.QSize(0, 52))
        self.resetButton.setObjectName("resetButton")
        self.gridLayout.addWidget(self.resetButton, 0, 1, 1, 1)
        self.groupBox = QtWidgets.QGroupBox(Dialog)
        self.groupBox.setMinimumSize(QtCore.QSize(411, 122))
        self.groupBox.setMaximumSize(QtCore.QSize(411, 159))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.groupBox.setFont(font)
        self.groupBox.setTitle("")
        self.groupBox.setAlignment(QtCore.Qt.AlignBottom|QtCore.Qt.AlignJustify)
        self.groupBox.setCheckable(False)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout.setContentsMargins(-1, 9, -1, -1)
        self.verticalLayout.setSpacing(6)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.combo_reading = QtWidgets.QComboBox(self.groupBox)
        self.combo_reading.setObjectName("combo_reading")
        self.combo_reading.addItem("")
        self.combo_reading.addItem("")
        self.combo_reading.addItem("")
        self.combo_reading.addItem("")
        self.combo_reading.addItem("")
        self.combo_reading.addItem("")
        self.combo_reading.addItem("")
        self.combo_reading.addItem("")
        self.combo_reading.addItem("")
        self.combo_reading.addItem("")
        self.combo_reading.addItem("")
        self.combo_reading.addItem("")
        self.combo_reading.addItem("")
        self.combo_reading.addItem("")
        self.combo_reading.addItem("")
        self.combo_reading.addItem("")
        self.combo_reading.addItem("")
        self.combo_reading.addItem("")
        self.combo_reading.addItem("")
        self.combo_reading.addItem("")
        self.combo_reading.addItem("")
        self.combo_reading.addItem("")
        self.combo_reading.addItem("")
        self.combo_reading.addItem("")
        self.combo_reading.addItem("")
        self.combo_reading.addItem("")
        self.combo_reading.addItem("")
        self.combo_reading.addItem("")
        self.combo_reading.addItem("")
        self.combo_reading.addItem("")
        self.combo_reading.addItem("")
        self.combo_reading.addItem("")
        self.combo_reading.addItem("")
        self.combo_reading.addItem("")
        self.combo_reading.addItem("")
        self.combo_reading.addItem("")
        self.combo_reading.addItem("")
        self.combo_reading.setItemText(36, "")
        self.horizontalLayout.addWidget(self.combo_reading)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_2 = QtWidgets.QLabel(self.groupBox)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_2.addWidget(self.label_2)
        self.path_save_graph = QtWidgets.QLineEdit(self.groupBox)
        font = QtGui.QFont()
        font.setFamily("Sans Serif")
        font.setItalic(False)
        self.path_save_graph.setFont(font)
        self.path_save_graph.setObjectName("path_save_graph")
        self.horizontalLayout_2.addWidget(self.path_save_graph)
        self.save_graph_button = QtWidgets.QPushButton(self.groupBox)
        self.save_graph_button.setObjectName("save_graph_button")
        self.horizontalLayout_2.addWidget(self.save_graph_button)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_3 = QtWidgets.QLabel(self.groupBox)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_3.addWidget(self.label_3)
        self.path_save_data = QtWidgets.QLineEdit(self.groupBox)
        self.path_save_data.setObjectName("path_save_data")
        self.horizontalLayout_3.addWidget(self.path_save_data)
        self.save_data_button = QtWidgets.QPushButton(self.groupBox)
        self.save_data_button.setObjectName("save_data_button")
        self.horizontalLayout_3.addWidget(self.save_data_button)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.gridLayout.addWidget(self.groupBox, 0, 3, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 0, 0, 1, 1)
        self.delta_time_box = QtWidgets.QSpinBox(Dialog)
        self.delta_time_box.setProperty("value", 60)
        self.delta_time_box.setObjectName("delta_time_box")
        self.delta_time_box.setProperty("maximum", 10000)
        self.gridLayout.addWidget(self.delta_time_box, 0, 5, 1, 1)
        self.label_4 = QtWidgets.QLabel(Dialog)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 0, 4, 1, 1)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem2, 0, 6, 1, 1)
        self.widget = MplCanvas(Dialog)
        self.widget.setMinimumSize(QtCore.QSize(0, 384))
        self.widget.setObjectName("widget")
        self.gridLayout.addWidget(self.widget, 2, 0, 1, 7)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.resetButton.setText(_translate("Dialog", "Reset"))
        self.label.setText(_translate("Dialog", "Currently reading:"))
        self.combo_reading.setItemText(0, _translate("Dialog", "R0: SET POINT T FOR SORB"))
        self.combo_reading.setItemText(1, _translate("Dialog", "R1: SORB TEMP"))
        self.combo_reading.setItemText(2, _translate("Dialog", "R2: 1 K POT TEMP"))
        self.combo_reading.setItemText(3, _translate("Dialog", "R3: MIX CHAMBER TEMP"))
        self.combo_reading.setItemText(4, _translate("Dialog", "R4: MIX CHAMBER POWER"))
        self.combo_reading.setItemText(5, _translate("Dialog", "R5: STILL POWER"))
        self.combo_reading.setItemText(6, _translate("Dialog", "R6: SORB POWER"))
        self.combo_reading.setItemText(7, _translate("Dialog", "R7: STEPPER V6 TARGET"))
        self.combo_reading.setItemText(8, _translate("Dialog", "R8: STEPPER V12 TARGET"))
        self.combo_reading.setItemText(9, _translate("Dialog", "R9: STEPPER N/V TARGET"))
        self.combo_reading.setItemText(10, _translate("Dialog", "R10: TEMP REGISTER"))
        self.combo_reading.setItemText(11, _translate("Dialog", "R11: CH1 FREQ/4"))
        self.combo_reading.setItemText(12, _translate("Dialog", "R12: CH2 FREQ/4"))
        self.combo_reading.setItemText(13, _translate("Dialog", "R13: CH3 FREQ/4"))
        self.combo_reading.setItemText(14, _translate("Dialog", "R14: A/D I/P GAUGE G1"))
        self.combo_reading.setItemText(15, _translate("Dialog", "R15: A/D I/P GAUGE G2"))
        self.combo_reading.setItemText(16, _translate("Dialog", "R16: A/D I/P GAUGE G3"))
        self.combo_reading.setItemText(17, _translate("Dialog", "R17: A/D I/P 4 (SPARE)"))
        self.combo_reading.setItemText(18, _translate("Dialog", "R18: A/D I/P 5 (SPARE)"))
        self.combo_reading.setItemText(19, _translate("Dialog", "R19: A/D I/P 6 (SPARE)"))
        self.combo_reading.setItemText(20, _translate("Dialog", "R20: A/D I/P PIRANI P1"))
        self.combo_reading.setItemText(21, _translate("Dialog", "R21: A/D I/P PIRANI P2"))
        self.combo_reading.setItemText(22, _translate("Dialog", "R22: RAW A/D I/P 1"))
        self.combo_reading.setItemText(23, _translate("Dialog", "R23: RAW A/D I/P 2"))
        self.combo_reading.setItemText(24, _translate("Dialog", "R24: RAW A/D I/P 3"))
        self.combo_reading.setItemText(25, _translate("Dialog", "R25: RAW A/D I/P 4"))
        self.combo_reading.setItemText(26, _translate("Dialog", "R26: RAW A/D I/P 5"))
        self.combo_reading.setItemText(27, _translate("Dialog", "R27: RAW A/D I/P 6"))
        self.combo_reading.setItemText(28, _translate("Dialog", "R28: RAW A/D I/P 7"))
        self.combo_reading.setItemText(29, _translate("Dialog", "R29: RAW A/D I/P 8"))
        self.combo_reading.setItemText(30, _translate("Dialog", "R30: MIX CHAMBER PROP BAND"))
        self.combo_reading.setItemText(31, _translate("Dialog", "R31: MIX CHAMBER INT ACT TIME"))
        self.combo_reading.setItemText(32, _translate("Dialog", "R32: MIX CHAMBER TEMP"))
        self.combo_reading.setItemText(33, _translate("Dialog", "R33: MIX CHAMBER SET POINT"))
        self.combo_reading.setItemText(34, _translate("Dialog", "R34: MIX CHAMBER SENSOR COND"))
        self.combo_reading.setItemText(35, _translate("Dialog", "R35: MIX CHAMBER SENSOR RES"))
        self.label_2.setText(_translate("Dialog", "Path: "))
        self.path_save_graph.setText(_translate("Dialog", "current_graph.png"))
        self.save_graph_button.setText(_translate("Dialog", "Save graph"))
        self.label_3.setText(_translate("Dialog", "Path: "))
        self.path_save_data.setText(_translate("Dialog", "current_data.txt"))
        self.save_data_button.setText(_translate("Dialog", "Save data"))
        self.label_4.setText(_translate("Dialog", "Wait\ntime [s]"))
         
        #
        # ---------------------------------------------------------------------------
        #

        self.timer1 = None
        self.data = [[] for i in range(35)]

        # connect buttons

        self.combo_reading.currentIndexChanged.connect(self.index_modified)
        self.save_graph_button.clicked.connect(self.save_graph)
        self.save_data_button.clicked.connect(self.save_data)
        self.resetButton.clicked.connect(self.reset_graph)
        self.delta_time_box.editingFinished.connect(self.set_delta_time)

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.wait_and_update()

    def wait_and_update(self):
        sec1 = self.delta_time_box.value()
        self.timer1 = QtCore.QTimer(self)
        self.timer1.stop()
        self.timer1.setInterval(1000*sec1)
        self.timer1.timeout.connect(self.update_data_and_plot)
        self.timer1.start()

    def update_data_and_plot(self):
        if self.parent.is_dialog_graphs_open is False:
            return

        print('update_plot')
        for idx, mylist in enumerate(self.data):
            mylist.append(self.parent.fridge.get_sens(idx))

        y = self.data[self.combo_reading.currentIndex()]
        x = range(len(y))
        self.widget.axes.cla()
        self.widget.axes.plot(x, y, 'r')
        self.widget.axes.set_xlabel('t')
        self.widget.draw()

    def save_graph(self):
        print('save_graph')
        self.widget.axes.set_title(self.combo_reading.currentText())
        self.widget.fig.savefig(self.path_save_graph.text())

    def temp_clear(self):
        self.widget.axes.cla()
        self.widget.draw()
        
    def save_data(self):
        print('save_data')

        now = datetime.now()

        if True:
            f = open(self.path_save_data.text(), 'a')
            f.write('\n')
            f.write(str(now.strftime("%d/%m/%Y %H:%M")) + ':')

            for i in range(len(self.data)):
                f.write('\nR{}\t['.format(i))
                for j in self.data[i]:
                    f.write('{}, '.format(j))
                f.write(']')
            f.close()
        else:
            print('problem detected! Is the path ok?')

    def reset_graph(self):
        print('reset_graph')
        self.temp_clear()
        self.data = [[] for i in range(35)]

    def index_modified(self):
        self.temp_clear()
        self.set_mock_delta_time()

    def set_mock_delta_time(self):
        print('set_delta_time')
        if self.timer1 is not None:
            self.timer1.stop()
        self.wait_and_update()

    def set_delta_time(self):
        print('set_delta_time')
        self.reset_graph()
        if self.timer1 is not None:
            self.timer1.stop()
        self.wait_and_update()
