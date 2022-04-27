import logging
import time

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
runnumb = 1
name        = 'scan_wide_off_' + str(runnumb)  # (scan_off, scan_res, scan_out, scan_wide_off, scan_wide_res, scan_wide_out)
path        = 'data/raw/cal_acq/'

config = {
    'runnumb'    : runnumb         ,
    'ref'        : 5.87045         ,    # expected frequency for the resonance, central point on x axis (GHz)
    'window'     : 100             ,    # length of half of the interval on x axis
    'step'       : 0.0002          ,    # length of a single step during the frequency sweep (GHz)
    'path'       : path            ,    # path where data will be saved
    'file_name'  : name                 # name of the file where data will be saved 
}

trigger = dict(
    trigger_type   = 'IMMEDIATE'   ,    #'EDGE', 'IMMEDIATE' or 'DIGITAL'
    trigger_source = '0'           ,   
    trigger_slope  = 'POSITIVE'    ,    #'POSITIVE' or 'NEGATIVE'
    trigger_level  = '0.0'         ,   
    trigger_delay  = '0.0'
)

config['trigger'] = trigger
##########

# Logging all the setting infos
logger.debug('Expected frequency resonance: '     + str(config['ref']))
logger.debug('Window: '                           + str(config['window']))
logger.debug('Step: '                             + str(config['step']))
logger.debug('Filename: '                         + config['file_name'])

for key in trigger:
    logger.debug(str(key) + ': ' + trigger[key])    

daq =  PXIeSignalAcq('PXI1Slot2', trigger=trigger, records=1, channels=[0,1], sample_rate=1e6, length=1000)
with FSWSynt('COM12') as synt:
    print(synt.get_ID())
    
    for i in range(-config['window'], config['window']):
        freq = config['ref'] + i*config['step']
        print(synt.set_freq(freq))
        time.sleep(0.005)
        #print(synt.get_freq(freq))
        #print(i)
        daq.acq()   
    
    daq.storage_hdf5(config['path'] + config['file_name'] + '.h5')

daq.close()

# save config for data analysis
import pickle
with open(config['path'] + 'config_' + config['file_name'] + '.pkl', 'wb') as f:
    pickle.dump(config, f)
logger.debug('Saved config for data analysis: config_' + config['file_name'] + '.pkl')
logger.info('END EXECUTION\n\n')