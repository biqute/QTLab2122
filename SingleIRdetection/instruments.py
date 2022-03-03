import pyvisa
import os
import numpy as np
from time import sleep
from qcodes import VisaInstrument
import array
import struct
import smtplib, ssl

port = 465  # For SSL
smtp_server = "smtp.gmail.com"
sender_email = "criokids2022@gmail.com"  # Enter your address

email_1 = "r.carobene@campus.unimib.it"  # Enter receiver address
email_2 = "e.cipelli@campus.unimib.it"  # Enter receiver address
email_3 = "p.campana1@campus.unimib.it"  # Enter receiver address

password = input("Inserici la password: ")  #ATTENZIONE A NON CARICARE SU GITHUB
message = """\
Subject: CRIOSTATO A PRESSIONE ALTA!

yei."""


class VNA_handler:
    def __init__(self):
        rm = pyvisa.ResourceManager()
        self.inst = rm.open_resource('GPIB0::16::INSTR')       

        #self.inst.write('HOLD;')        #takes instrument out of free-run mode
        self.inst.write('FORM2;')        #outputs number in 4bytes mode (float?) with 4-byte header

        self.inst.write('S21;')

        self.inst.write('AVERFACT16;')       #turns on sample averaging
        self.inst.write('AVEROON;')       #turns on sample averaging
        self.inst.write('AVERREST;')       #turns on sample averaging
        self.inst.write('IFBW1000;')

    def set_sweep_freq(self, start_f,stop_f):
        self.inst.write('LINFREQ;')
        self.inst.write('POIN 1601;')                       #set number of points
        self.inst.write('STAR '+str(start_f)+' GHZ;')       #set start frequency
        self.inst.write('STOP '+str(stop_f)+' GHZ;')        #set stop frequency
        self.inst.write('CONT;')     

    def get_sweep_data(self, format_data='polar', format_out='formatted data'):

        self.set_format(format_data)
        request_msg = self.get_request_from_format_out(format_out)

        self.inst.write('POIN?;')
        num_points = int(float((self.inst.read('\n'))))


        self.inst.write(request_msg)
        num_bytes = 8*int(num_points)+4
        raw_bytes = self.inst.read_bytes(num_bytes)

        #print(raw_bytes)

        trimmed_bytes = raw_bytes[4:]
        tipo='>'+str(2*num_points)+'f'
        x = struct.unpack(tipo, trimmed_bytes)
        #x.byteswap()
        
        #del x[1::2]
        return list(x)

    def save_sweep_data(self, filename, format_data='linear magnitude'):
        amp_q = self.get_sweep_data(format_data)
        amp_i = amp_q.copy()
        del amp_i[1::2]
        del amp_q[0::2]

        self.inst.write('STAR?')
        start = float(self.inst.read('\n'))
        self.inst.write('STOP?')
        stop = float(self.inst.read('\n'))
        self.inst.write('POIN?')
        num_points = int(float(self.inst.read('\n')))

        freq = list(np.linspace(start, stop, num_points))
        del freq[0]

        zipped_data = zip(freq, amp_i, amp_q)

        with open(filename, 'w') as file:
            for el in zipped_data:
                file.write(f'{el[0]},\t{el[1]},\t{el[2]}\n')
        

    def get_request_from_format_out(self, format):
        if format == 'raw data array 1':
            msg = 'OUTPRAW1;'
        elif format == 'raw data array 2':
            msg = 'OUTPRAW2;'
        elif format == 'raw data array 3':
            msg = 'OUTPRAW3;'
        elif format == 'raw data array 4':
            msg = 'OUTPRAW4;'
        elif format == 'error-corrected data':
            msg = 'OUTPDATA;'
        elif format == 'error-corrected trace memory':
            msg = 'OUTPMEMO;'
        elif format == 'formatted data':
            msg = 'DISPDATA;OUTPFORM'
        elif format == 'formatted memory':
            msg = 'DISPMEMO;OUTPFORM'
        elif format == 'formatted data/memory':
            msg = 'DISPDDM;OUTPFORM'
        elif format == 'formatted data-memory':
            msg = 'DISPDMM;OUTPFORM'
        return msg

    def set_format(self, format):
        if format == 'polar':
            write_string = 'POLA;'
        elif format == 'log magnitude':
            write_string = 'LOGM;'
        elif format == 'phase':
            write_string = 'PHAS;'
        elif format == 'delay':
            write_string = 'DELA;'
        elif format == 'smith chart':
            write_string = 'SMIC;'
        elif format == 'linear magnitude':
            write_string = 'LINM;'
        elif format == 'standing wave ratio':
            write_string = 'SWR;'
        elif format == 'real':
            write_string = 'REAL;'
        elif format == 'imaginary':
            write_string = 'IMAG;'

        self.inst.write(write_string)


class Fridge_handler(VisaInstrument):
    def __init__(self, **kwargs):
        super().__init__("name", 'ASRL1::INSTR' , **kwargs)
        rm = pyvisa.ResourceManager()
        #self.inst = rm.open_resource('ASRL1::INSTR')
        self.visa_handle.set_visa_attribute(pyvisa.constants.VI_ATTR_ASRL_STOP_BITS,
                                            pyvisa.constants.VI_ASRL_STOP_TWO)
        self.visa_handle.write('Q2\r')

    def execute(self, mes):
        self.visa_handle.write(mes+'\r')
        sleep(20e-2)
        bytes_in_buffer = self.visa_handle.bytes_in_buffer
        return self.visa_handle.read(str(bytes_in_buffer)+'\r')

    def set_T(self, T):
        n='E'
        if T<=35:
            n+='1'
        elif T<=55:
            n+='2'
        elif T<=140:
            n+='3'
        elif T<=400:
            n+='4'
        else:
            n+='5'

        res = self.execute(n)
        res = self.execute('A2')
        res = self.execute('T'+str(10*T))

    def get_sens(self, sensor = 3):
        res = self.execute('R'+str(sensor))
        res = res.replace("\r", "")
        res = res.replace("\n", "")
        res = res.replace("R", "")
        return int(float(res))

    def send_alert_mail(self):
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, email_1, message)
            server.sendmail(sender_email, email_2, message)
            server.sendmail(sender_email, email_3, message)

    def check_press(self):
        res = self.get_sens(14) < 2800 and self.get_sens(15) < 2880
        if(not res):
            print("PRESSIONE ALTA!")
            self.send_alert_mail()
            sleep(60*10)
        return res

    def wait_for_T(self, T, tol=2):
        self.set_T(T)
        check=0
        while check<20 and self.check_press():
            T_now = self.get_T(3)
            os.system('cls')
            print(T_now)
            if T_now not in range(T-tol, T+tol):
                check=0
            else:
                check+=1
            sleep(3)
        print("Fridge is ready!")
            
