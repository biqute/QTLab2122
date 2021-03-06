#!/usr/bin/env python3  Line 1
# -*- coding: utf-8 -*- Line 2
#----------------------------------------------------------------------------
# Created By  : Celotto Andrea, Palumbo Emanuele, Zafferani Alessandro   Line 3
# Created Date: 16/02/2022 12:30
# version ='Beta 1.0'

import visa
import time

class SIM928(object):
    def __init__(self, visa_name, sim900port):
        self.rm = visa.ResourceManager()
        self.pyvisa = self.rm.open_resource(visa_name)
        self.pyvisa.timeout = 10000 # Set response timeout (in milliseconds)
        self.pyvisa.query_delay = 5 # Set extra delay time between write and read commands
        self.sim900port = sim900port
        
    #comandi fondamentali
    def read(self):
        return self.pyvisa.read()
    
    def write(self, string):
        self.pyvisa.write(string)
        
    def query(self, string):
        msg = self.pyvisa.query(string)
        #print(msg)
        return  msg
    
    def close(self):
        self.pyvisa.close()
        
        
    #comandi di connessione
    def connect(self):
        a = self.position()
        if a == 'Stanford_Research_Systems,SIM900,s/n152741,ver3.6\r\n':
            self.write('CONN ' + str(self.sim900port) + ',"esc"')
            self.position()
    
    def disconnect(self):
        a = self.position()
        if a == 'Stanford_Research_Systems,SIM928,s/n030465,ver2.2\r\n':
            self.write('CONN ' + str(self.sim900port) + ',"esc"')
            self.position()
            
    def switch_conn(self):
        self.position()
        self.write('CONN ' + str(self.sim900port) + ',"esc"')
        self.position()
    
    def position(self):
        a=self.query('*IDN?')
        print(a)
        return  a
    
    def set_output(self, output=False):
        if output==True:
            self.write('OPON') 
        else:
            self.write('OPOF')
            
    def reset(self):
        self.write('*RST')
        
    def clear_registers(self):
        self.write('*CLS')
        
    def close_all(self):
        self.clear_registers()
        self.reset()
        self.disconnect()
        self.close()

    #comandi voltaggio
    def set_voltage(self, voltage=0.0):
        self.write('VOLT ' + str(voltage))
        #self.query('*OPC?')
        time.sleep(0.005)
        
    def ask_voltage(self):
        v=self.query('VOLT?')
        #print("Voltage = " + a + " V")
        return float(v)
    
    #comandi batteria
    def battery_status(self):
        a= "A,B,x \n" + self.query('BATS?') + "\n A,B=1: in use, =2: charging, =3: ready. \n x=0: service battery indicator off, =1: it's on \n"
        print(a)
        return a
    
    def battery_override(self):
        self.write('BCOR')
        time.sleep(15)
        self.battery_status()
    
    #comandi per indagare errori
    def exe_error(self):
        a = self.query('LEXE?')
        legend = ["No execution error since last LEXE?", "Illegal value", "Wrong token", "Invalid bit"]
        print(legend[int(a)])
    
    def dev_error(self):
        a = self.query('LCME?')
        legend = ["No execution error since last LCME?", "Illegal command", "Undefined command", "Illegal query", "Illegal set", "Missing parameter-s", "Extra parameter-s", "Null parameter-s", "Parameter buffer overflow", "Bad floating-point", "Bad integer", "Bad integer toke", "Bad token value", "Bad hex block", "Unknown token"]
        print(legend[int(a)])
    
    def error(self):
        print("Execution error: \n")
        self.exe_error()
        print("Device error: \n")
        self.dev_error()