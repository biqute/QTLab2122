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
daq =  PXIeSignalAcq("PXI1Slot2", trigger, records=1, sample_rate=5e7, length=1000)

with FSWSynt("COM12") as synt:
    print(synt.get_ID())
    ref = 5.87045 
    #for i in range(-1,2):
    #    freq = ref + i*0.0002
    #    print(synt.set_freq(freq))
    #    time.sleep(0.2)
    #    print('ciao')
    #    print(synt.get_freq())
    #    daq.read()
    #    print('quasi quasi fatto')
    #    daq.fill_matrix()
    #    print('quasi fatto')
    #    daq.storage_hdf5('frequency.h5')

    daq.get_hdf5('frequency.h5')

daq.close()