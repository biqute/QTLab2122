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
runnumb = 42
name        = 'scan_wide_res_' + str(runnumb)  # (scan_off_, scan_res_, scan_wide_off_, scan_wide_res_)
path        = 'data/raw/cal_acq/'

config = {
    'runnumb'    : runnumb             ,
    'ref'        : [5.86622, 5.63566]  ,    # expected frequency for the resonance, central point on x axis (GHz) 5.8627 - 5.6305 - 5.63134 - 5.86446
    'window'     : 1000                ,    # length of half of the interval on x axis, 1000 wide, 250 non wide
    'step'       : 0.00002             ,    # length of a single step during the frequency sweep (GHz)
    'path'       : path                ,    # path where data will be saved
    'file_name'  : name                ,     # name of the file where data will be saved 
    'att_manop'  : '25dB'              ,
    'channels'   : [0,1,2,3]
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

daq =  PXIeSignalAcq('PXI1Slot2', trigger=trigger, records=1, channels=config['channels'], sample_rate=1e6, length=1000)
with FSWSynt('COM12') as synt, FSWSynt('COM7') as synt2: 
    print(synt.get_ID())
    print(synt2.get_ID()) 

    for i in range(-config['window'], config['window']):
        freq = config['ref'][0] + i*config['step']
        freq2 = config['ref'][1] + i*config['step'] 
        #synt.set_freq(freq)
        print(synt.set_freq(freq))
        synt2.set_freq(freq2)
        time.sleep(0.005)
        #print(i)
        daq.acq()   
        time.sleep(0.005)
    
"""    
    for i in range(-config['window'], config['window']):
        freq = config['ref'][1] + i*config['step']
        print(synt.set_freq(freq))
        time.sleep(0.005)
        #print(synt.get_freq(freq))
        #print(i)
        daq.acq2() """

daq.storage_hdf5(config['path'] + config['file_name'] + '.h5')
daq.close()

print('Done :) \nSaving..')
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