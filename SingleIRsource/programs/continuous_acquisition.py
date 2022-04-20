from instruments.FSW_0010 import *
from instruments.PXIe_5170R import *
from instruments.utils import *

########## parameters that can be changed
freq              = 5.86905       #frequency chosen to study I and Q (GHz)
file_name         = 'cont_acq'    #name of the file where data will be saved
records           = 1             #numer of records to store
channels          = [0,1]         #list of enabled channels
sample_rate       = 1e6           #rate of points sampling of PXIe-5170R in Hz
total_acq_time    = 0.1            #total acquisition time in seconds
total_samples     = int(total_acq_time * sample_rate)
samples_per_fetch = 1000          #number of points sampled at a time during the acquisition
waveforms         = [np.ndarray(total_samples, dtype=np.float64) for c in channels]
                                  #prepare an empty array in which the waveform will be stored
trigger = dict(
    trigger_type   = 'CONTINUOS'
)
##########

'''with FSWSynt("COM12") as synt:
    #print(synt.get_ID())
    synt.set_freq(freq)
    time.sleep(0.005) #IMPORTANT for real time communication
    print('The current frequency is: ' + synt.get_freq(freq))'''    #just to check if the freqency has been set correctly

with PXIeSignalAcq("PXI1Slot2", trigger=trigger, records=records, channels=channels, sample_rate=sample_rate, length=1, ref_pos=0.0) as daq:
    daq.continuous_acq(total_samples, samples_per_fetch)
    daq.storage_hdf5(file_name + '.h5')

i_r, q_r = get_hdf5(file_name + '.h5')
index = segmentation_index(i_r[0], threshold=0.01)
i_matrix, q_matrix = segmentation_iq(i_r[0], q_r[0], index)

# Try to understand how to remove the [0] on i_r and q_r
# These methods show how to segmentate a continuous acquisition
# Remember to apply this before sav_gol and set the right threshold, length and ref_pos
# After you made the sav_gol you can correct I and Q and save them in a watson file

#https://nimi-python.readthedocs.io/en/master/niscope/examples.html#niscope-fetch-forever-py