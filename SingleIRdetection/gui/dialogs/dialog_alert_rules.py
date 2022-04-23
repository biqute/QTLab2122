
import re
import smtplib, ssl

from PyQt5 import uic
from PyQt5.QtWidgets import QDialog

class RuleObject():
    def __init__(self, text_rules, granparent, parent):
        self.rules_text = text_rules
        self.parent = parent
        self.granparent = granparent

    def send_alert(self):
        message = 'Subject: ALERT CRIOSTATO!\n\n'
        message += 'current_rules:\n'
        message += self.rules_text
        message += '\n\n'

        for i in range(35):
            message += 'R{sens_num}: {get_sens}\n'.format(
                sens_num=i,
                get_sens=self.granparent.fridge.get_sens(i))

        context = ssl._create_default_https_context()
        with smtplib.SMTP_SSL(self.parent.sender_server.text(),
                               self.parent.sender_port.value(),
                               context=context) as server:
            server.login(self.parent.sender_email.text(),
                         self.parent.sender_pass.text())
            for rec_email in self.parent.receivers_emails.toPlainText().splitlines():
                server.sendmail(self.parent.sender_email.text(),
                                rec_email,
                                message)

    def compute_rules(self):
        res = self.wrapped_compute_rules()
        if res:
            self.send_alert()

    def wrapped_compute_rules(self):
        text = self.rules_text
        if len(text) == 0:
            raise ValueError('Insert a rule!')

        line_values = []

        for line in text.splitlines():

            if '(' in line:
                line = line.replace(' ', '')
                line = line.replace('(', ' ')
                line = line.replace(')', ' ')

                line_list = line.split()
            else:
                line_list = [line]

            do_and = False
            do_or = False
            current_line_val = False

            for el in line_list:
                el = el.replace(' ','')

                valid = True
                valid = valid and el != 'AND'
                valid = valid and el != 'OR'
                valid = valid and len(re.split(r'(^R\d*)(==|<=|>=|=<|=>|<|>)(\d*$)', el)[1:-1]) != 3
                valid = valid and len(re.split(r'(^\d*)(==|<=|>=|=<|=>|<|>)(R\d*$)', el)[1:-1]) != 3
                if valid:
                    raise ValueError('This string is weird!')

                if el == 'AND':
                    do_and = True
                    continue
                elif el == 'OR':
                    do_or = True
                    continue

                else:
                    el_or = el

                    el = re.split(r'(^R\d*)(==|<=|>=|=<|=>|<|>)(\d*$)', el) [1:-1]
                    if len(el) == 3:
                        #espressione tipo ['R44', '<=', '40']
                        sensor = self.granparent.fridge.get_sens(int(el[0].replace('R','')))
                        if int(el[0].replace('R', '')) not in range (0, 36):
                            raise ValueError('Weird Sensor!')
                        target = int(el[2])

                        if el[1] == '<':
                            res = sensor < target
                        if el[1] == '>':
                            res = sensor > target
                        if el[1] == '<=' or el[1] == '=<':
                            res = sensor <= target
                        if el[1] == '>=' or el[1] == '=>':
                            res = sensor >= target
                        if el[1] == '==':
                            res = sensor == target


                    else:
                        el = re.split(r'(^\d*)(==|<=|>=|=<|=>|<|>)(R\d*$)', el)[1:-1]
                        #espressione tipo ['40', '<=', 'R44']
                        sensor = self.granparent.fridge.get_sens(int(el[2].replace('R','')))
                        if int(el[2].replace('R', '')) not in range (0, 36):
                            raise ValueError('Weird Sensor!')

                        target = int(el[0])

                        if el[1] == '<':
                            res = sensor > target
                        if el[1] == '>':
                            res = sensor < target
                        if el[1] == '<=' or el[1] == '=<':
                            res = sensor >= target
                        if el[1] == '>=' or el[1] == '=>':
                            res = sensor <= target
                        if el[1] == '==':
                            res = sensor == target
                if do_and:
                    current_line_val = current_line_val and res
                    do_and = False
                elif do_or:
                    current_line_val = current_line_val or res
                    do_or = False
                else:
                    current_line_val = res

            line_values.append(current_line_val)

        risultato = True
        for val in line_values:
            risultato = risultato and val

        return risultato

class Ui_Dialog(QDialog):
    def __init__(self, parent):
        self.parent = parent
        self.rule_obj = None

        super(Ui_Dialog, self).__init__()
        uic.loadUi('alert_settings.ui', self)

        # connect

        self.sender_email.editingFinished.connect(self.check_status_to_wait)
        self.sender_pass.editingFinished.connect(self.check_status_to_wait)

        self.check_status_sender.clicked.connect(self.check_sender)
        # self.receivers_emails.editingFinished.connect(self.change_rec_emails)
        self.rules_text.textChanged.connect(self.check_rules_to_wait)
        self.check_current_rules.clicked.connect(self.check_rules)

        self.set_all_button.clicked.connect(self.set_all_rules)

        self.finished.connect(self.save_me)

        if self.parent.alert_dict != None:
            self.set_old()

        self.show()

    def set_old(self):
        self.sender_email.setText(self.parent.alert_dict['sender_email'])
        self.sender_pass.setText(self.parent.alert_dict['sender_pass'])
        self.sender_server.setText(self.parent.alert_dict['server_url'])
        self.receivers_emails.setText(self.parent.alert_dict['receivers'])
        self.rules_text.setText(self.parent.alert_dict['rules'])
        self.sender_port.setValue(self.parent.alert_dict['server_port'])

    def save_me(self):
        self.parent.alert_dict = {
            'sender_email': self.sender_email.text(),
            'sender_pass': self.sender_pass.text(),
            'server_port': self.sender_port.value(),
            'server_url': self.sender_server.text(),
            'receivers': self.receivers_emails.toPlainText(),
            'rules': self.rules_text.toPlainText()
        }

    def check_sender(self):
        print('check_sender')
        context = ssl.create_default_context()
        server_url = self.sender_server.text()
        server_port = self.sender_port.value()
        sender_email = self.sender_email.text()
        sender_pass = self.sender_pass.text()

        try:
            server = smtplib.SMTP_SSL(server_url,
                                      server_port,
                                      context=context)
            server.login(sender_email, sender_pass)
            server.quit()
        except:
            print('Problemi di accesso!!')
            self.status_sender.setText('failed')
            self.status_sender.setStyleSheet('background-color: rgb(255, 0, 0);')
        else:
            self.status_sender.setText('connected')
            self.status_sender.setStyleSheet('background-color: rgb(167, 255, 170);')

    def check_status_to_wait(self):
        self.status_sender.setText('waiting')
        self.status_sender.setStyleSheet('background-color: rgb(255, 255, 127);')
        self.rule_obj = None
        
    def check_rules_to_wait(self):
        self.current_rules_status.setText('waiting')
        self.current_rules_status.setStyleSheet('background-color: rgb(255, 255, 127);')
        self.rule_obj = None

    def check_rules(self):
        print('check_rules')
        try:
            test_value = self.parse_text_and_test(self.rules_text.toPlainText())
        except Exception as e:
            print(e)
            self.current_rules_status.setText('failed')
            self.current_rules_status.setStyleSheet('background-color: rgb(255, 0, 0);')
        else:
            self.current_rules_status.setText('passed')
            self.current_rules_status.setStyleSheet('background-color: rgb(167, 255, 170);')

    def check_receivers(self):
        if len(self.receivers_emails.toPlainText()) > 0:
            res = True
        else:
            return False
        for email in self.receivers_emails.toPlainText().splitlines():
            pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            if (not re.fullmatch(pattern, email)):
                return False
        return res

    def set_all_rules(self):
        print('set_all_rules')
        self.check_sender()
        self.check_rules()

        sender = self.status_sender.text() == 'connected'
        rules = self.current_rules_status.text() == 'passed'
        receiver = self.check_receivers() == True

        if sender and rules and receiver:
            self.parent.my_rule_obj = RuleObject(self.rules_text.toPlainText(), self.parent, self)
        else:
            print('Something is wrong!')

    def parse_text_and_test(self, text):
        line_values = []
        if len(text) == 0:
            raise ValueError('Insert a rule!')

        for line in text.splitlines():

            if '(' in line:
                line = line.replace(' ', '')
                line = line.replace('(', ' ')
                line = line.replace(')', ' ')

                line_list = line.split()
            else:
                line_list = [line]

            do_and = False
            do_or = False
            current_line_val = False

            for el in line_list:
                el = el.replace(' ','')

                valid = True
                valid = valid and el != 'AND'
                valid = valid and el != 'OR'
                valid = valid and len(re.split(r'(^R\d*)(==|<=|>=|=<|=>|<|>)(\d*$)', el)[1:-1]) != 3
                valid = valid and len(re.split(r'(^\d*)(==|<=|>=|=<|=>|<|>)(R\d*$)', el)[1:-1]) != 3
                if valid:
                    raise ValueError('This string is weird!')

                if el == 'AND':
                    do_and = True
                    continue
                elif el == 'OR':
                    do_or = True
                    continue

                else:
                    el_or = el

                    el = re.split(r'(^R\d*)(==|<=|>=|=<|=>|<|>)(\d*$)', el) [1:-1]
                    if len(el) == 3:
                        #espressione tipo ['R44', '<=', '40']
                        #sensor = parent.fridge.get_sensor(int(el[0].replace('R','')))
                        if int(el[0].replace('R', '')) not in range (0, 36):
                            raise ValueError('Weird Sensor!')
                        sensor = 1
                        target = int(el[2])

                        if el[1] == '<':
                            res = sensor < target
                        if el[1] == '>':
                            res = sensor > target
                        if el[1] == '<=' or el[1] == '=<':
                            res = sensor <= target
                        if el[1] == '>=' or el[1] == '=>':
                            res = sensor >= target
                        if el[1] == '==':
                            res = sensor == target


                    else:
                        el = re.split(r'(^\d*)(==|<=|>=|=<|=>|<|>)(R\d*$)', el)[1:-1]
                        #espressione tipo ['40', '<=', 'R44']
                        #sensor = parent.fridge.get_sensor(int(el[2].replace('R','')))
                        if int(el[2].replace('R', '')) not in range (0, 36):
                            raise ValueError('Weird Sensor!')

                        sensor = 1
                        target = int(el[0])

                        if el[1] == '<':
                            res = sensor > target
                        if el[1] == '>':
                            res = sensor < target
                        if el[1] == '<=' or el[1] == '=<':
                            res = sensor >= target
                        if el[1] == '>=' or el[1] == '=>':
                            res = sensor <= target
                        if el[1] == '==':
                            res = sensor == target
                if do_and:
                    current_line_val = current_line_val and res
                    do_and = False
                elif do_or:
                    current_line_val = current_line_val or res
                    do_or = False
                else:
                    current_line_val = res

            line_values.append(current_line_val)

        risultato = True
        for val in line_values:
            risultato = risultato and val

        return risultato




        
