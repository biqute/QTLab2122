from FSW_0010 import *
from PXIe_5170R_2 import *
import time

trigger = dict(
    trigger_type = 'IMMEDIATE', #'EDGE', 'IMMEDIATE' or 'DIGITAL'
    trigger_source = '0',
    trigger_slope = 'POSITIVE', #'POSITIVE' or 'NEGATIVE'
    trigger_level = '0.0',
    trigger_delay = '0.0'
)

daq =  PXIeSignalAcq("PXI1Slot2", trigger, records=1, channels=[0,1], sample_rate=5e7, length=1000)
with FSWSynt("COM12") as synt:
    print(synt.get_ID())
    ref = 5.8686
    #ref = 5.7
    for i in range(-2500,2500):
        freq = ref + i*0.0002
        print(synt.set_freq(freq))
        time.sleep(0.005)
        #print(synt.get_freq(freq))
        print(i)
        daq.read()
    #daq.fill_matrix(200)
    daq.storage_hdf5('scan_2_1GhZ.h5')

    #daq.get_hdf5('frequency.h5')

daq.close()