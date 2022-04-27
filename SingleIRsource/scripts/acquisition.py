import logging
import sys

from logging.config import dictConfig
from logging_config import LOGGING_CONFIG
from src.FSW_0010 import *
from src.PXIe_5170R import *
from src.utils import *

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
name = get_date(file_name = 'acq')
path = 'data/raw/edge_acq/'

config = {
    'freq'        : [5.86905]      ,        # frequency chosen to study I and Q (GHz)
    'file_name'   : name           ,        # name of the file where data will be saved
    'records'     : 100            ,        # numer of records to store
    'channels'    : [0,1]          ,        # list of enabled channels
    'sample_rate' : 1e7            ,        # rate of points sampling of PXIe-5170R
    'length'      : 1000           ,        # record length? maybe it's just the number of points it takes, if the trigger fires later it doesn't take them check what really happens, check the parameters in input to read and simulate the records to see if fill_matrix works
    'resonators'  : [0]                     # list of resonators used, it's probably a useless variable
}               

trigger = dict(
    trigger_type   = 'EDGE',         #'EDGE', 'IMMEDIATE' or 'DIGITAL'
    trigger_source = '0',
    trigger_slope  = 'POSITIVE',     #'POSITIVE' or 'NEGATIVE'
    trigger_level  = '0.1',
    trigger_delay  = '0.0'
)

config['trigger'] = trigger
config['ADCmax']  =  5
config['ADCmin']  = -5
config['ADCnbit'] = 14

###########

# Logging all the setting infos
logger.debug('Frequency: '         + str(config['freq']))
logger.debug('Filename: '          + config['file_name'])
logger.debug('Records: '           + str(config['records']))
logger.debug('Channels: '          + str(config['channels']))
logger.debug('Sample rate: '       + str(config['sample_rate']))
logger.debug('Length: '            + str(config['length']))

for key in trigger:
    logger.debug(str(key) + ': '   + trigger[key])

# Decide how many points we want based on signal length and sample_rate
# It seems that length indicates how long it is open, if it is 10k but the trigger goes off after 1000 it takes 9k (..?)

'''
with FSWSynt("COM12") as synt:
    #print(synt.get_ID())
    synt.set_freq(freq[0])
    time.sleep(0.005) #IMPORTANT for real time communication
    #synt.turn_on()
    print('The current frequency is: ' + synt.get_freq())    #just to check if the freqency has been set correctly

with FSWSynt("COM7") as synt:
    #print(synt.get_ID())
    synt.set_freq(freq[1])
    time.sleep(0.005) #IMPORTANT for real time communication
    #synt.turn_on()
    print('The current frequency is: ' + synt.get_freq())    #just to check if the freqency has been set correctly
'''

I, Q, timestamp = [], [], []

with PXIeSignalAcq('PXI1Slot2', trigger=trigger, records=config['records'], channels=config['channels'], sample_rate=config['sample_rate'], length=config['length']) as daq:
    daq.fetch()
    daq.fill_matrix()
    daq.storage_hdf5(config['file_name'] + '.h5')

# CREATE A NEW FILe FOR SAVGOL

    I, Q, timestamp = daq.get_hdf5(config['file_name'] + '.h5')

# apply savgol filter and derivative trigger to align the wfms
indexes = np.array(derivative_trigger_matrix(I)) # choose whether to use I or Q for the savgol filter and choose parameters

# code to align the samples
# e.g. take the first entry as a reference and move the other
delta = (indexes - indexes.min()).astype(int)
end = (indexes - indexes.max() - 1).astype(int)

# at the end it's necessary to cut the samples to have them all of the same length
# - 1 in end needed to avoid Q[i][sth:0] that happened when indexes=indexes.max()
# and returned an empty array
new_I, new_Q = [], []

for i in range(len(I)):
    new_I.append(I[i][delta[i]:end[i]])
    new_Q.append(Q[i][delta[i]:end[i]])

# use storage hdf5 from utils to store the new matrices
storage_hdf5(config['file_name'] + '_savgol.h5', 'i_signal', new_I, 'q_signal', new_Q)

# save config for data analysis
import pickle
with open('config_' + config['file_name'] + '.pkl', 'wb') as f:
    pickle.dump(config, f)

logger.debug('Saved config for data analysis: config_' + config['file_name'] + '.pkl')
logger.info('END EXECUTION\n\n')