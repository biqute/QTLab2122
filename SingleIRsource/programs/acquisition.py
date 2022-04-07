from instruments.FSW_0010 import *
from instruments.PXIe_5170R import *
import time

# IMPORTANT INFOS
# Before acquiring, we must evaluate the dependence between: sample_rate, length (record) and pulse frequency
# Usually sample_rate/length = 1e3
# Record length is sometimes smaller than set length. (Problem 1)
# We have solved the fact that the record length was sometimes less than the set length, we need to set the timeout on the fetch() function
# This solution works well (and always) for the IMMEDIATE, we need to understand the EDGE, maybe we can set a long timeout

########## Parameters that can be setted
freq        = 5.86905                # frequency chosen to study I and Q (GHz)
file_name   = 'TEST_100_1E7_10000'   # name of the file where data will be saved
records     = 1000                   # numer of records to store
channels    = [0,1]                  # list of enabled channels
sample_rate = 1e5                    # rate of points sampling of PXIe-5170R
length      = 10000                   # record length? maybe it's just the number of points it takes, if the trigger fires later it doesn't take them check what really happens, check the parameters in input to read and simulate the records to see if fill_matrix works

trigger = dict(
    trigger_type   = 'EDGE', #'EDGE', 'IMMEDIATE' or 'DIGITAL'
    trigger_source = '0',
    trigger_slope  = 'POSITIVE', #'POSITIVE' or 'NEGATIVE'
    trigger_level  = '0.1',
    trigger_delay  = '0.0'
)
##########


# Decide how many points we want based on signal length and sample_rate
# It seems that length indicates how long it is open, if it is 10k but the trigger goes off after 1000 it takes 9k (..?)

'''with FSWSynt("COM12") as synt:
    #print(synt.get_ID())
    synt.set_freq(freq)
    time.sleep(0.005) #IMPORTANT for real time communication
    print('The current frequency is: ' + synt.get_freq(freq))    #just to check if the freqency has been set correctly
'''
with PXIeSignalAcq("PXI1Slot2", trigger=trigger, records=records, channels=channels, sample_rate=sample_rate, length=length) as daq:
    daq.fetch()
    daq.fill_matrix()
    #daq.storage_hdf5(file_name + '.h5')
