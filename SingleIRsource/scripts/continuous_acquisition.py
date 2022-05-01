#https://nimi-python.readthedocs.io/en/master/niscope/examples.html#niscope-fetch-forever-py

import logging
import json

from logging.config import dictConfig
from logging_config import LOGGING_CONFIG
from src.FSW_0010   import *
from src.PXIe_5170R import *
from src.utils      import *

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
logger.debug('Filename: '          + str(config['file_name']))
logger.debug('Records: '           + str(config['records']))
logger.debug('Channels: '          + str(config['channels']))
logger.debug('Sample rate: '       + str(config['sample_rate']))
logger.debug('Total samples: '     + str(config['total_samples']))
logger.debug('Total time: '        + str(total_acq_time))

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

"""with h5py.File(path + config['file_name'] + '.h5', 'w') as hdf:
    hdf.create_dataset('i_signal_ch0', data=np.random.rand(config['total_samples'])*10, compression='gzip', compression_opts=9)
    hdf.create_dataset('q_signal_ch0', data=np.random.rand(config['total_samples'])*8, compression='gzip', compression_opts=9)
    hdf.create_dataset('i_signal_ch1', data=np.random.rand(config['total_samples'])*10, compression='gzip', compression_opts=9)
    hdf.create_dataset('q_signal_ch1', data=np.random.rand(config['total_samples'])*8, compression='gzip', compression_opts=9)"""

#save config for data analysis
cfg = json.dumps(config)
with open(path + 'config_' + config['file_name'] + '.json','w') as f:
    f.write(cfg)

logger.info('END EXECUTION\n\n')