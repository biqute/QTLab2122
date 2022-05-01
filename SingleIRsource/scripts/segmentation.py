import os
import numpy as np

from src.utils import *

path      = 'data/raw/cont_acq/'
save_path = 'data/clean/segm_acq/'
files     = os.listdir(path)

for file in files:
    if 'config' in file:
        continue
    else:
        i_r, q_r           = get_hdf5(file)
        index              = segmentation_index(i_r[0], threshold=0.01)
        i_matrix, q_matrix = segmentation_iq(i_r[0], q_r[0], index)
        timestamp          = np.linspace(0, len(i_matrix)-1, len(i_matrix))
        
        storage_hdf5(save_path + 'split_' + file + '.h5', 'i_signal', i_matrix, 'q_signal', q_matrix, 'timestamp', timestamp)

# Try to understand how to remove the [0] on i_r and q_r
# These methods show how to segmentate a continuous acquisition
# Remember to apply this before sav_gol and set the right threshold, length and ref_pos
# After you made the sav_gol you can correct I and Q and save them in a watson file