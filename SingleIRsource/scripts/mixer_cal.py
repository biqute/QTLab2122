import logging
import time

from logging.config import dictConfig
from logging_config import LOGGING_CONFIG
from src.FSW_0010 import *
from src.PXIe_5170R import *

# LOG SYSTEM
dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)
logger.info('START EXECUTION')

# turn on the synt
# attenuators needed
# lo from synt1 and rf from synt2

# Parameters that can be setted
config = {
    'freq1'       : 5.869050     ,     # frequency chosen to study I and Q (GHz)
    'freq2'       : 5.869051     ,     # frequency chosen to study I and Q (GHz)
    'path'        : 'data/mixer/',     # name of the file where data will be saved
    'file_name'   : 'mix_amp6'   ,     # name of the file where data will be saved
    'records'     : 1            ,     # numer of records to store
    'channels'    : [0,1]        ,     # list of enabled channels
    'sample_rate' : 1e3          ,     # rate of points sampling of PXIe-5170R in Hz
    'total_time'  : 1            ,     # total acquisition time in seconds
    'length'      : int(1 * 2e3)       # 'total_time' * 'sample_rate'
}

trigger = dict(
    trigger_type   = 'IMMEDIATE',      #'EDGE', 'IMMEDIATE' or 'DIGITAL'
    trigger_source = '0',
    trigger_slope  = 'POSITIVE',       #'POSITIVE' or 'NEGATIVE'
    trigger_level  = '0.0',
    trigger_delay  = '0.0'
)

# Logging all the setting infos
logger.debug('Frequency 1: '         + str(config['freq1']))
logger.debug('Frequency 2: '         + str(config['freq2']))
logger.debug('Filename: '            + config['file_name'])
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

time.sleep(2)

with PXIeSignalAcq('PXI1Slot2', trigger=trigger, records=config['records'], channels=config['channels'], sample_rate=config['sample_rate'], length=config['length']) as daq:
    daq.fetch()
    daq.fill_matrix()
    daq.storage_hdf5(config['path'] + config['file_name'] + '.h5')

# save config for data analysis
import pickle
with open(config['path'] + 'config_' + config['file_name'] + '.pkl', 'wb') as f:
    pickle.dump(config, f)
logger.debug('Saved config for data analysis: config_' + config['file_name'] + '.pkl')
logger.info('END EXECUTION\n\n')