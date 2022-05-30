import visa
import time

class SMA100B(object):
    
    # initialization
    
    def __init__(self, visa_name):
        self.rm = visa.ResourceManager()
        self.pyvisa = self.rm.open_resource('TCPIP0::' + str(visa_name) + '::inst0::INSTR')
        #self.pyvisa = self.rm.open_resource('TCPIP0::' + str(visa_name) + '::INSTR')
        #self.pyvisa.timeout = 10000 # Set response timeout (in milliseconds)
        #self.pyvisa.query_delay = 5 # Set extra delay time between write and read commands
    
    # main command
    
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

        
    # reset initial value
    
    def reset(self):
        sim.write('*RST')
        
    # TO SET FREQUENCY AND AMPLITUDE OF WAVES 
    # frequency
    
    def set_freq(self, freq):
        self.write('SOURce1:FREQuency:CW ' + str(freq))
        self.query('*OPC?')
        
    def set_freq_off(self, off): 
        self.write('SOURce1:FREQuency:OFFSet'+ str(off) )
    
    def set_freq_mult(self, mult): 
        self.write('SOURce1:FREQuency:MULTiplier '+ str(mult))
    
    def ask_freq(self):
        f = self.query('SOURce1:FREQuency:CW?')
        return float(f)
        
    
    # amplitude
    
    def set_ampl(self, ampl):
        self.write('SOURce1:POWer:LEVel:IMMediate:AMPLitude ' + str(ampl))
        self.query('*OPC?')
        
        
    def ask_ampl(self):
        a = self.query('SOURce1:POWer:LEVel:IMMediate:AMPLitude?')
        return float(a)
        
    # shape
    
    def set_shape(self, s):
        self.write('SOURce1:LFOutput1:SHAPe ' + str(s))