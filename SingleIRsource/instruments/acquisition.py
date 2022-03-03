from FSW_0010 import *
from PXIe_5170R_2 import *
import time
import matplotlib.pyplot as plt

trigger = dict(
    trigger_type = 'EDGE', #'EDGE', 'IMMEDIATE' or 'DIGITAL'
    trigger_source = '0',
    trigger_slope = 'NEGATIVE', #'POSITIVE' or 'NEGATIVE'
    trigger_level = '-0.04',
    trigger_delay = '0.0'
)

daq =  PXIeSignalAcq("PXI1Slot2", trigger, records=1, channels=[0], sample_rate=5e6, length=1000)
with FSWSynt("COM12") as synt:
    print(synt.get_ID())
    freq = 5.8686
    synt.set_freq(freq)
    time.sleep(0.005)
    print(synt.get_freq(freq))    
        
    sample = daq.acq()
    #daq.fill_matrix(200)
    x = np.linspace(0,len(sample)-1,len(sample))
    plt.scatter(x, sample, marker='.')
    plt.savefig("immagine.png")
    #daq.storage_hdf5('acquisition/acquisition.h5')

    #daq.get_hdf5('frequency.h5')

daq.close()