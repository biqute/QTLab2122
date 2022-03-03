import serial
import time

class FSWSynt(object):

    def __init__(self, device_address):
        self.device = serial.Serial(device_address, baudrate=115200, timeout=1.5, stopbits=1, parity='N')       #stopbits

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
    
    def __enter__(self):
        return self
    
    def __exit__(self, *exc):
        return None

    def connect(self):
        return self.connect()

    def get_ref_source(self):
        return self.ask(b'ROSC:SOUR?\r')

    def switch_ref_source(self):
        self.write(b'ROSC:SOUR EXT\r' if "INT" in self.get_ref_source() else b'ROSC:SOUR INT\r')
        return "Switching to external source (EXT)" if "INT" in self.get_ref_source() else "Switching to internal source (INT)"
    
    def get_temp(self):      #Temperature in Celsius degrees
        return self.ask(b'DIAG:MEAS? 21\r')

"""with FSWSynt("COM12") as test:
    # Trovare comando ON snza aprire il programma
    #test.connect()
    #time.sleep(1)
    #print(test.get_ID())
    #for i in range(-10,10):
    i=0
    print(test.set_freq(5.8686+i*0.0002))
    time.sleep(0.2)
    print(test.get_freq(), i)
    time.sleep(3)"""