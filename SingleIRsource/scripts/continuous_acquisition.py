#https://nimi-python.readthedocs.io/en/master/niscope/examples.html#niscope-fetch-forever-py

import logging

from logging.config import dictConfig
from logging_config import LOGGING_CONFIG
from src.FSW_0010 import *
from src.PXIe_5170R import *
from src.utils import *

# LOG SYSTEM
dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)
logger.info('START EXECUTION')

########## CONFIG PARAMETERS
total_acq_time      = 0.1
sample_rate         = 1e6
name                = get_date(file_name = 'cont_acq')
path                = 'data/raw/cont_acq/'

config = {
'freq'              : [5.86905]                           ,  # frequency chosen to study I and Q (GHz)
'file_name'         : name                                ,  # name of the file where data will be saved
'records'           : 1                                   ,  # numer of records to store
'channels'          : [0,1]                               ,  # list of enabled channels
'sample_rate'       : sample_rate                         ,  # rate of points sampling of PXIe-5170R in Hz
'total_acq_time'    : total_acq_time                      ,  # total acquisition time in seconds
'total_samples'     : int(total_acq_time * sample_rate)   ,  # total number of points sampled
'samples_per_fetch' : 1000                                ,  # number of points sampled at a time during the acquisition
'resonators'        : [0]                                    # list of resonators used
}

#prepare an empty array in which the waveform will be stored
waveforms           = [np.ndarray(config['total_samples'], dtype=np.float64) for c in config['channels']]

trigger = dict(
    trigger_type    = 'CONTINUOS'
)

config['trigger'] = trigger
##########

# Logging all the setting infos
logger.debug('Frequency: '         + str(config['freq']))
logger.debug('Filename: '          + config['file_name'])
logger.debug('Records: '           + str(config['records']))
logger.debug('Channels: '          + str(config['channels']))
logger.debug('Sample rate: '       + str(config['sample_rate']))
logger.debug('Length: '            + str(config['length']))
logger.debug('Total time: '          + str(total_acq_time))
logger.debug('Total samples: '       + str(config['total_samples']))

for key in trigger:
    logger.debug(str(key) + ': ' + trigger[key]) 

'''with FSWSynt("COM12") as synt:
    #print(synt.get_ID())
    synt.set_freq(freq[0])
    time.sleep(0.005) #IMPORTANT for real time communication
    print('The current frequency is: ' + synt.get_freq(freq))

with FSWSynt("COM7") as synt:
    #print(synt.get_ID())
    synt.set_freq(freq[1])
    time.sleep(0.005) #IMPORTANT for real time communication
    #synt.turn_on()
    print('The current frequency is: ' + synt.get_freq())    #just to check if the freqency has been set correctly
'''

with PXIeSignalAcq("PXI1Slot2", trigger=trigger, records=config['records'], channels=config['channels'], sample_rate=sample_rate, length=1, ref_pos=0.0) as daq:
    daq.continuous_acq(config['total_samples'], config['samples_per_fetch'])
    daq.storage_hdf5(path + config['file_name'] + '.h5')

# NEW FILE
i_r, q_r = get_hdf5(path + config['file_name'] + '.h5')
index = segmentation_index(i_r[0], threshold=0.01)
i_matrix, q_matrix = segmentation_iq(i_r[0], q_r[0], index)

# Try to understand how to remove the [0] on i_r and q_r
# These methods show how to segmentate a continuous acquisition
# Remember to apply this before sav_gol and set the right threshold, length and ref_pos
# After you made the sav_gol you can correct I and Q and save them in a watson file


#save config for data analysis
import pickle
with open(path + 'config_' + config['file_name'] + '.pkl', 'wb') as f:
    pickle.dump(config, f)

logger.info('END EXECUTION\n\n')