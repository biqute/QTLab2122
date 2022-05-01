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

########## CONFIG PARAMETERS
runnumb = 1
name        = 'scan_off_' + str(runnumb)  # (scan_off_, scan_res_, scan_wide_off_, scan_wide_res_)
path        = 'data/raw/cal_acq/'

config = {
    'runnumb'    : runnumb         ,
    'ref'        : [5.870, 5.899]  ,    # expected frequency for the resonance, central point on x axis (GHz)
    'window'     : 2500            ,    # length of half of the interval on x axis
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
logger.debug('Expected frequency resonance: ' + str(config['ref']))
logger.debug('Window: '                       + str(config['window']))
logger.debug('Step: '                         + str(config['step']))
logger.debug('Filename: '                     + str(config['file_name']))

for key in trigger:
    logger.debug(str(key) + ': ' + trigger[key])    

daq =  PXIeSignalAcq('PXI1Slot2', trigger=trigger, records=1, channels=[0,1], sample_rate=1e6, length=1000)
with FSWSynt('COM12') as synt:
    print(synt.get_ID())
    
    for i in range(-config['window'], config['window']):
        freq = config['ref'][0] + i*config['step']
        print(synt.set_freq(freq))
        time.sleep(0.005)
        #print(synt.get_freq(freq))
        #print(i)
        daq.acq()   
    
with FSWSynt('COM7') as synt:
    print(synt.get_ID())
    
    for i in range(-config['window'], config['window']):
        freq = config['ref'][1] + i*config['step']
        print(synt.set_freq(freq))
        time.sleep(0.005)
        #print(synt.get_freq(freq))
        #print(i)
        daq.acq2() 

    daq.storage_hdf5(config['path'] + config['file_name'] + '.h5')

daq.close()

"""
with h5py.File(path + config['file_name'] + '.h5', 'w') as hdf:
    hdf.create_dataset('i_signal_ch0', data=np.random.rand(config['window']*2), compression='gzip', compression_opts=9)
    hdf.create_dataset('q_signal_ch0', data=np.random.rand(config['window']*2), compression='gzip', compression_opts=9)
    hdf.create_dataset('i_signal_ch1', data=np.random.rand(config['window']*2), compression='gzip', compression_opts=9)
    hdf.create_dataset('q_signal_ch1', data=np.random.rand(config['window']*2), compression='gzip', compression_opts=9)
"""

# save config for data analysis
cfg = json.dumps(config)
with open(config['path'] + 'config_' + config['file_name'] + '.json', 'w') as f:
    f.write(cfg)

logger.debug('Saved config for data analysis: config_' + config['file_name'] + '.json')
logger.info('END EXECUTION\n\n')