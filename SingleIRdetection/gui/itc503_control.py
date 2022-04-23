import sys
from datetime import datetime

from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtWidgets import QStyleFactory

from dialogs.dialog_send_command import Ui_Dialog as dialog_send_command
from dialogs.dialog_cryostat_panel import Ui_Dialog as dialog_cryostat_panel
from dialogs.dialog_alert_rules import Ui_Dialog as dialog_alert_rules
from dialogs.dialog_live_graphs import Ui_Dialog as dialog_live_graphs

from instruments import Fridge_handler


class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        self.fridge = Fridge_handler()
        self.logging_enabled = False
        self.alert_enabled = False

        self.timer1 = None
        self.timer2 = None
        self.my_rule_obj = None
        self.is_dialog_graphs_open = False
        self.alert_dict = None

        super(Ui, self).__init__()
        uic.loadUi('itc503_control.ui', self)

        # connect settings
        self.spinsetTemp.editingFinished.connect(self.set_temp)
        self.send_other_commands.clicked.connect(self.open_send_commands)
        self.combosetAutocontrol.currentIndexChanged.connect(self.set_autocontrol)
        self.spinsetGasOutput.editingFinished.connect(self.set_gas_output)
        self.combosetHeatersens.currentIndexChanged.connect(self.set_heater_sensor)
        self.spinsetHeaterPercent.editingFinished.connect(self.set_heater_output)
        self.spinsetProportionalID.editingFinished.connect(self.set_proportional)
        self.spinsetPIntegrationD.editingFinished.connect(self.set_integration)
        self.spinsetPIDerivative.editingFinished.connect(self.set_derivative)
        self.spin_threadinterval.editingFinished.connect(self.set_general_delta_time)

        # connect noncritical settings
        self.check_logging_enable.stateChanged.connect(self.set_logging_status)
        self.delta_time_log.editingFinished.connect(self.set_delta_time_log)
        self.check_alert_enable.stateChanged.connect(self.set_alert_status)
        self.command_open_alert_rules.clicked.connect(self.open_alert_rules)

        # connect advanced gui
        self.command_open_panel.clicked.connect(self.open_cryostat_panel)
        self.command_open_graphs.clicked.connect(self.open_live_graphs)

        # auto-update readings

        self.wait_and_update()

        self.show()

    def wait_and_update(self):
        sec1 = self.spin_threadinterval.value()
        self.timer1 = QtCore.QTimer()
        self.timer1.stop()
        self.timer1.setInterval(1000*sec1)
        self.timer1.timeout.connect(self.update_all_readings)
        self.timer1.start()

    def wait_and_log(self):
        sec2 = self.delta_time_log.value()
        self.timer2 = QtCore.QTimer()
        self.timer2.stop()
        self.timer2.setInterval(1000*sec2)
        self.timer2.timeout.connect(self.do_the_log)
        self.timer2.start()

    def update_all_readings(self):
        self.lcdTemp_set.display(self.fridge.get_sens(0))
        self.lcdTemp_sens1_K.display(self.fridge.get_sens(1))
        self.lcdTemp_sens2_K.display(self.fridge.get_sens(2))
        self.lcdTemp_sens3_K.display(self.fridge.get_sens(3))
        self.lcdTemp_err.display(self.lcdTemp_sens1_K.value() - self.lcdTemp_set.value())
        self.lcd_mix_power.display(self.fridge.get_sens(4))
        self.lcd_still_power.display(self.fridge.get_sens(5))
        self.lcd_sorb_power.display(self.fridge.get_sens(6))
        self.lcd_gauge1.display(self.fridge.get_sens(14))
        self.lcd_gauge2.display(self.fridge.get_sens(15))
        self.lcdProportionalID.display(self.fridge.get_sens(30))
        self.lcdPIntegrationD.display(self.fridge.get_sens(31))

        if self.alert_enabled:
            self.do_the_alert()

    def set_temp(self):
        print('set temp')
        self.fridge.set_temp(self.spinsetTemp.value)

    def open_send_commands(self):
        print('open_send_commands')
        self.dialog_command = QtWidgets.QDialog()
        self.dialog_command.ui = dialog_send_command(self)

    def set_autocontrol(self, value):
        command = 'A' + str(value)
        _ = self.fridge.execute(command)
        print('set_autocontrol')

    def set_gas_output(self):
        print('set_gas_output')

    def set_heater_sensor(self):
        print('set_heater_sensor')

    def set_heater_output(self):
        print('set_heater_output')

    def set_proportional(self):
        print('set_proportional')

    def set_integration(self):
        print('set_integration')

    def set_derivative(self):
        print('set_derivative')

    def set_general_delta_time(self):
        print('set_general_delta_time')
        if self.timer1 is not None:
            self.timer1.stop()
        self.wait_and_update()

    def set_logging_status(self, value):
        print('set logging status')
        if value is 0:
            self.logging_enabled = False
        else:
            self.logging_enabled = True

    def set_delta_time_log(self):
        print('set_delta_time_log')
        if self.timer2 is not None:
            self.timer2.stop()
        self.wait_and_log()

    def set_alert_status(self, value):
        print('set_alert_status')
        if value is 0:
            self.alert_enabled = False
        else:
            self.alert_enabled = True

    def open_alert_rules(self):
        print('open_alert_rules')
        self.dialog_alert = QtWidgets.QDialog()
        self.dialog_alert.ui = dialog_alert_rules(self)
        self.my_rule_obj = self.dialog_alert.ui.rule_obj
        # self.dialog_alert.finished.connect(self.save_rule_diag)

    def open_cryostat_panel(self):
        print('open_cryostat_panel')
        self.dialog_panel = QtWidgets.QDialog()
        self.dialog_panel.ui = dialog_cryostat_panel(self)

    def open_live_graphs(self):
        print('open_live_graphs')
        self.is_dialog_graphs_open = True
        self.dialog_graphs = QtWidgets.QDialog()
        self.dialog_graphs.ui = dialog_live_graphs()
        self.dialog_graphs.ui.setupUi(self.dialog_graphs, self)
        self.dialog_graphs.show()
        self.dialog_graphs.finished.connect(self.chiudi_live_graphs)

    def chiudi_live_graphs(self):
        print('chiudi_live_graphs')
        self.is_dialog_graphs_open = False

    def do_the_log(self):
        print('do_the_log')
        print(self.log_path.text())

        if self.check_logging_enable.isChecked() is False:
            return

        now = datetime.now()
        
        try:
            #not using fstring for better compatibility, in this way we can run on Python < 3.6
            f = open(self.log_path.text(), 'a')
            log_string = str(now.strftime("%d/%m/%Y %H:%M")) + ':'
            for i in range(35):
                log_string += '\n\tR{i}: {get_sensor}'.format(i=i,
                                                              get_sensor=self.fridge.get_sens(i))
            log_string += '\n'
            f.write(log_string)
            f.close()
        except:
            print('problemi nella path!')

    def do_the_alert(self):
        print('do_the_alert')
        if self.check_alert_enable.isChecked() is False:
            return
        elif self.my_rule_obj is None:
            return
        else:
            self.my_rule_obj.compute_rules()



app = QtWidgets.QApplication(sys.argv)  # Create QApplication
app.setStyle(QStyleFactory.create('Fusion'))
window = Ui()  # Create an instance of our class
app.exec_()  # Start the application
