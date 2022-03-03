from FSW_0010 import *
from PXIe_5170R_2 import *
import time
import matplotlib.pyplot as plt

trigger = dict(
    trigger_type = 'IMMEDIATE', #'EDGE', 'IMMEDIATE' or 'DIGITAL'
    trigger_source = '0',
    trigger_slope = 'POSITIVE', #'POSITIVE' or 'NEGATIVE'
    trigger_level = '0.0',
    trigger_delay = '0.0'
)

#con rate diverso da 5e7 e length diversa da 1000 non scatta il trigger..
#bisogna decidere quanti punti vogliamo in base alla lunghezza del segnale e al sample_rate


"""with FSWSynt("COM12") as synt:
    print(synt.get_ID())
    freq = 5.86905
    synt.set_freq(freq)
    time.sleep(0.005)
    print(synt.get_freq(freq))    
        """
with PXIeSignalAcq("PXI1Slot2", trigger, records=1, channels=[2,3], sample_rate=1e7, length=10000) as daq:
    daq.read()
    #daq.fill_matrix(200)
    daq.storage_hdf5('acq.h5')

    #daq.get_hdf5('frequency.h5')
