import logging
import time
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

# COMMENTS
# turn on the synt
# attenuators needed
# lo from synt1 and rf from synt2

########## CONFIG PARAMETERS
freq        = 5.869050
name        = get_date(file_name = 'mix_cal_' + str(int(freq * 1e6)))
name        = 'mix_cal_' + str(int(freq * 1e6))
path        = 'data/raw/mix_cal/mixer1/'
sample_rate = 1e3              
total_time  = 1

config = {
    'freq1'       : freq                             , # frequency chosen to study I and Q (GHz)
    'freq2'       : freq + 0.000001                  , # frequency chosen to study I and Q (GHz)
    'path'        : path                             , # name of the file where data will be saved
    'file_name'   : name                             , # name of the file where data will be saved
    'records'     : 1                                , # numer of records to store
    'channels'    : [0,1]                            , # list of enabled channels
    'sample_rate' : sample_rate                      , # rate of points sampling of PXIe-5170R in Hz
    'total_time'  : total_time                       , # total acquisition time in seconds
    'length'      : int(total_time * sample_rate)      # length of the record
}

trigger = dict(
    trigger_type   = 'IMMEDIATE'                     , #'EDGE', 'IMMEDIATE' or 'DIGITAL'
    trigger_source = '0'                             , # from 0 to 3 in str format
    trigger_slope  = 'POSITIVE'                      , #'POSITIVE' or 'NEGATIVE'
    trigger_level  = '0.0'                           , # decided with threshold.py
    trigger_delay  = '0.0'
)

config['trigger'] = trigger
###########   

# Logging all the setting infos
logger.debug('Frequency 1: '         + str(config['freq1']))
logger.debug('Frequency 2: '         + str(config['freq2']))
logger.debug('Filename: '            + str(config['file_name']))
logger.debug('Records: '             + str(config['records']))
logger.debug('Channels: '            + str(config['channels']))
logger.debug('Sample rate: '         + str(config['sample_rate']))
logger.debug('Total time: '          + str(config['total_time']))
logger.debug('Length: '              + str(config['length']))

for key in trigger:
    logger.debug(str(key) + ': ' + trigger[key])      

# To simulate a programmable phase shifter we beat two synthesizers. 
# The output frequencies of the two synthesizers are set to be 1 kHz apart 
# and the IQ ellipses are digitized at a sample rate of 2 kHz for 1 second 
# (two circles are recorded)
with FSWSynt('COM7') as synt:
    #print(synt.get_ID())
    synt.set_freq(config['freq1'])
    time.sleep(0.005) #IMPORTANT for real time communication
    #synt.turn_on()
    logger.debug('The current frequency of the first synthetizer is: ' + str(synt.get_freq()))    #just to check if the freqency has been set correctly

with FSWSynt('COM12') as synt:
    #print(synt.get_ID())
    synt.set_freq(config['freq2'])
    time.sleep(0.005) #IMPORTANT for real time communication
    #synt.turn_on()
    logger.debug('The current frequency of the second synthetizer is: ' + str(synt.get_freq()))    #just to check if the freqency has been set correctly

time.sleep(1)

with PXIeSignalAcq('PXI1Slot2', trigger=trigger, records=config['records'], channels=config['channels'], sample_rate=config['sample_rate'], length=config['length']) as daq:
    daq.fetch()
    daq.fill_matrix()
    daq.storage_hdf5(config['path'] + config['file_name'] + '.h5')

with h5py.File(path + config['file_name'] + '.h5', 'w') as hdf:
    hdf.create_dataset('i_signal_ch0', data=np.random.rand(config['length'])*10, compression='gzip', compression_opts=9)
    hdf.create_dataset('q_signal_ch0', data=np.random.rand(config['length'])*8, compression='gzip', compression_opts=9)

# save config for data analysis
cfg = json.dumps(config)
with open(config['path'] + 'config_' + config['file_name'] + '.json', 'w') as f:
    f.write(cfg)
    
logger.debug('Saved config for data analysis: config_' + config['file_name'] + '.json')
logger.info('END EXECUTION\n\n')