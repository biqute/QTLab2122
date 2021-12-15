import serial
#import time

class Synthetizer:

    def __init__(self, device_address):
        self.device = serial.Serial(device_address, baudrate=115200, timeout=1.5, stopbits=1, parity='N') #stopbits

    def write(self, msg):
        self.device.write(bytes(msg))
        return True

    def read(self):
        return self.device.readline().decode()

    def ask(self, msg):
        self.write(msg)
        return self.read()

    def getID(self):
        return self.ask(b'*IDN?\r')
    
    def getFreq(self, G=True):
        freq = self.ask(b'FREQ?\r')
        #print(freq)
        if G:
            freq = float(freq)/1e12
        return freq

    def setFreq(self,freq):  # default units in GHz
        if (freq < 0.5 or freq > 10):
            return "Invalid frequency! FSW-0010 supports [0.5 GHZ, 10 GHz]"
        cmd_string = 'FREQ ' + str(freq) + 'GHz\r'
        self.write(str.encode(cmd_string))
        return "Frequency set to "+str(freq)+" GHz."

    def close(self):
        return self.close()

    def connect(self):
        return self.connect()

    def getRefSource(self):
        return self.ask(b'ROSC:SOUR?\r')

    def switchRefSource(self):
        if "INT" in self.getRefSource():
            self.write(b'ROSC:SOUR EXT\r')
            return "Switching to external source (EXT)"
        else: 
            self.write(b'ROSC:SOUR INT\r')
            return "Switching to internal source (INT)"
    
    def getTemp(self):    #Temperature in Celsius degrees
        return self.ask(b'DIAG:MEAS? 21\r')