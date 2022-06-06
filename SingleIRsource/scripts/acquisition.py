import logging
import json
import time
import sys

from logging.config import dictConfig
from logging_config import LOGGING_CONFIG
from src.FSW_0010   import *
from src.PXIe_5170R import *
from src.utils      import *

# LOG SYSTEM
dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)
logger.info('START EXECUTION')

# IMPORTANT INFOS
# Before acquiring, we must evaluate the dependence between: sample_rate, length (record) and pulse frequency
# Usually sample_rate/length = 1e3
# Record length is sometimes smaller than set length. (Problem 1)
# We have solved the fact that the record length was sometimes less than the set length, we need to set the timeout on the fetch() function
# This solution works well (and always) for the IMMEDIATE, we need to understand the EDGE, maybe we can set a long timeout
# I on channel 0, Q on channel 1

########## CONFIG PARAMETERS
name = get_date(file_name = 'noise')
path = 'data/raw/edge_acq/'

config = {
    'freq'        : [5.86512, 5.63622]      ,        # frequency chosen to study I and Q (GHz)
    'file_name'   : name                    ,        # name of the file where data will be saved
    'records'     : 10000                   ,        # number of records to store
    'channels'    : [0,1,2,3]               ,        # list of enabled channels
    'sample_rate' : 5e7                     ,        # rate of points sampling of PXIe-5170R
    'length'      : 6000                    ,        # record length
    'resonators'  : [0,1]                   ,        # list of resonators used, it's probably a useless variable
    'source_rate' : 700 #diode rate in hz
}               

trigger = dict(
    trigger_type   = 'EDGE',         #'EDGE', 'IMMEDIATE' or 'DIGITAL'
    trigger_source = '1',
    trigger_slope  = 'POSITIVE',          #'POSITIVE' or 'NEGATIVE'
    trigger_level  = '-0.031',
    trigger_delay  = '0.0'
)

config['trigger'] = trigger
config['ADCmax']  =  5
config['ADCmin']  = -5
config['ADCnbit'] = 14

###########

# Logging all the setting infos
logger.debug('Frequency: '     + str(config['freq']))
logger.debug('Filename: '      + str(config['file_name']))
logger.debug('Records: '       + str(config['records']))
logger.debug('Channels: '      + str(config['channels']))
logger.debug('Sample rate: '   + str(config['sample_rate']))
logger.debug('Length: '        + str(config['length']))

for key in trigger:
    logger.debug(str(key) + ': '   + trigger[key])

# Decide how many points we want based on signal length and sample_rate
# It seems that length indicates how long it is open, if it is 10k but the trigger goes off after 1000 it takes 9k (..?)

with FSWSynt("COM12") as synt:
    synt.set_freq(config['freq'][0])
    time.sleep(0.005) #IMPORTANT for real time communication
    synt.turn_on()
    print('The current frequency of ' + str(synt.get_ID()) + ' is: ' + str(synt.get_freq()))    #just to check if the freqency has been set correctly

with FSWSynt("COM7") as synt:
    synt.set_freq(config['freq'][1])
    time.sleep(0.005) #IMPORTANT for real time communication
    synt.turn_on()
    print('The current frequency of ' + str(synt.get_ID()) + ' is: ' + str(synt.get_freq()))    #just to check if the freqency has been set correctly

time.sleep(0.1)

with PXIeSignalAcq('PXI1Slot2', trigger=trigger, records=config['records'], channels=config['channels'], sample_rate=config['sample_rate'], length=config['length'], ref_pos=20.0) as daq:
    daq.fetch(timeout=10)
    daq.fill_matrix()
    daq.storage_hdf5(path + config['file_name'] + '.h5')

# save config for data analysis
cfg = json.dumps(config)
with open(path + 'config_' + config['file_name'] + '.json', 'w') as f:
    f.write(cfg)

logger.debug('Saved config for data analysis: config_' + config['file_name'] + '.json')
logger.info('END EXECUTION\n\n')