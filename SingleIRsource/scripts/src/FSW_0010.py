# REFERENCES
# https://pyserial.readthedocs.io/en/latest/pyserial_api.html
# http://ni-microwavecomponents.com/manuals/5580510-01.pdf

import logging
import serial

class FSWSynt(object):

    logger = logging.getLogger(__name__) # Understand what can be useful to log for the synthesizer because we have return in each functions

    def __init__(self, device_address):
        try:
            self.device = serial.Serial(device_address, baudrate=115200, timeout=1.5, stopbits=1, parity='N')       #stopbits
            self.logger.debug('Connected to FSWSynt')
            print(':)')
        except:
            self.logger.debug('Not connected to FSWSynt')
            print(':(')

    def write(self, msg):
        self.device.write(bytes(msg))
        return True

    def read(self):
        return self.device.readline().decode()

    def ask(self, msg):
        self.write(msg)
        return self.read()

    def get_ID(self):
        return self.ask(b'*IDN?\r')
    
    def get_freq(self, G=True):
        freq = self.ask(b'FREQ?\r')
        return float(freq)/1e12 if G else freq

    def set_freq(self,freq):     # default units in GHz
        if (freq < 0.5 or freq > 10):
            return "Invalid frequency! FSW-0010 supports [0.5 GHZ, 10 GHz]"
        cmd_string = 'FREQ ' + str(freq) + 'GHz\r'
        self.write(str.encode(cmd_string))
        return "Frequency set to "+str(freq)+" GHz."

    def get_power(self): # Value in dBm
        pow = self.ask(b'POW?\r')
        return float(pow)

    def set_power(self,pow):     # default units in dB
        #if (pow < -25 or pow > 15):
        #    return "Invalid power! FSW-0010 supports [-25 dBm, +15 dBm]" # step of 0.01
        cmd_string = 'POW ' + str(pow) + '\r' # not sure about the \r
        self.write(str.encode(cmd_string))
        return "Power set to "+str(pow)+" dBm."

    def __enter__(self):
        return self
    
    def __exit__(self, *exc):
        return None

    def turn_on(self):
        return self.ask(b'OUTP:STAT ON\r') 

    def turn_off(self):
        return self.ask(b'OUTP:STAT OFF\r') 

    def connect(self):
        return self.connect()

    def get_ref_source(self):
        return self.ask(b'ROSC:SOUR?\r')

    def switch_ref_source(self):
        self.write(b'ROSC:SOUR EXT\r' if "INT" in self.get_ref_source() else b'ROSC:SOUR INT\r')
        return "Switching to external source (EXT)" if "INT" in self.get_ref_source() else "Switching to internal source (INT)"
    
    def get_temp(self):      #Temperature in Celsius degrees
        return self.ask(b'DIAG:MEAS? 21\r')