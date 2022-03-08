from instruments.FSW_0010 import *
from instruments.PXIe_5170R_2 import *
import time

########## parameters that can be changed
freq        = 5.86905       #frequency chosen to study I and Q (GHz)
file_name   = 'acq'         #name of the file where data will be saved
records     = 1             #numer of records to store
channels    = [0,1]         #list of enabled channels
sample_rate = 1e7           #rate of points sampling of PXIe-5170R
length      = 10000         #record length?? forse è solo il numero di punti che prende, se il trigger scatta dopo non li prende
                            #verificare cosa accade davvero, check dei parametri in input a read e simulazione dei record per vedere se fill_matrix funziona

trigger = dict(
    trigger_type   = 'IMMEDIATE', #'EDGE', 'IMMEDIATE' or 'DIGITAL'
    trigger_source = '0',
    trigger_slope  = 'POSITIVE', #'POSITIVE' or 'NEGATIVE'
    trigger_level  = '0.0',
    trigger_delay  = '0.0'
)
##########


#bisogna decidere quanti punti vogliamo in base alla lunghezza del segnale e al sample_rate
#sembra che length indichi quanto tempo sta aperto, se è 10k ma il trigger scatta dopo 1000 ne prende 9k (..?)

with FSWSynt("COM12") as synt:
    #print(synt.get_ID())
    synt.set_freq(freq)
    time.sleep(0.005) #IMPORTANT for real time communication
    print('The current frequency is: ' + synt.get_freq(freq))    #just to check if the freqency has been set correctly

with PXIeSignalAcq("PXI1Slot2", trigger, records, channels, sample_rate, length) as daq:
    daq.read()
    daq.fill_matrix()
    daq.storage_hdf5(file_name + '.h5')
