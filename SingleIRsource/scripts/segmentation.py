import os
import numpy as np

from src.utils import *

# NOTE: before using this script, plot the data to decide threshold and debounce 
# Their values depend on the window_ma chosen!
# Remmeber to set correctly the parameters of segmentation_index(window_ma, threshold, polarity, debounce)

path      = '../data/raw/cont_acq/' #/home/aperego/Documents/QTLab2122/SingleIRsource
save_path = '../data/clean/segm_acq/'
files     = ['cont_acq_060522_183654.h5'] #os.listdir(path) 

for file in files:
    if 'config' in file:
        continue
    else:
        i1_r, q1_r, i2_r, q2_r  = get_hdf5_2(path + file)
        print('Acquisition of %d samples loaed.' %len(i1_r[0]))

        index                   = segmentation_index(q1_r, window_ma=60, threshold=-0.0001, polarity=-1, debounce=3)
        i1, q1, i2, q2          = segmentation_iq(i1_r[0], q1_r[0], i2_r[0], q2_r[0], index)
        print('Divided into %d signals of length %d.' %(len(i1), len(i1[0])))

        timestamp          = np.linspace(0, len(i1)-1, len(i1))
        storage_hdf5(save_path + 'segm_' + file.replace('cont_',''), 'i_signal_ch0', i1, 'q_signal_ch0', q1, 'timestamp_ch0', timestamp, 'i_signal_ch1', i2, 'q_signal_ch1', q2, 'timestamp_ch1', timestamp)
        
        print('Done. New file created at ', save_path + 'segm_' + file.replace('cont_',''))

# Try to understand how to remove the [0] on i_r and q_r -> if acq works it can be removed
# These methods show how to segmentate a continuous acquisition
# Remember to apply this before sav_gol and set the right threshold, length and ref_pos
# After you made the sav_gol you can correct I and Q and save them in a watson file