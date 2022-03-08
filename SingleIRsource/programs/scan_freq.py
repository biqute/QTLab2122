from instruments.FSW_0010 import *
from instruments.PXIe_5170R_2 import *
import time

########## parameters that can be changed
ref        = 5.87045       #expected frequency for the resonance, central point on x axis (GHz)
window     = 100           #length of half of the interval on x axis
step       = 0.0002        #length of a single step during the frequency sweep (GHz)
file_name  = 'scan_1GHz'   #name of the file where data will be saved

trigger = dict(
    trigger_type   = 'IMMEDIATE', #'EDGE', 'IMMEDIATE' or 'DIGITAL'
    trigger_source = '0',
    trigger_slope  = 'POSITIVE', #'POSITIVE' or 'NEGATIVE'
    trigger_level  = '0.0',
    trigger_delay  = '0.0'
)
##########

daq =  PXIeSignalAcq("PXI1Slot2", trigger, records=1, channels=[0,1], sample_rate=5e7, length=1000)
with FSWSynt("COM12") as synt:
    print(synt.get_ID())
    
    for i in range(-window, window):
        freq = ref + i*step
        print(synt.set_freq(freq))
        time.sleep(0.005)
        #print(synt.get_freq(freq))
        print(i)
        daq.acq()   #DA TESTARE
    
    daq.storage_hdf5(file_name + '.h5')

daq.close()