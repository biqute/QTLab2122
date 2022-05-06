import os

from src.utils import *

path = 'data/raw/edge_acq/'
files = os.listdir(path)

for file in files:
    if 'config' in file:
        continue
    else:
        I1, Q1, t1, I2, Q2, t2 = [], [], [], [], [], []
        I1, Q1, t1, I2, Q2, t2 = get_hdf5_time(file)

        # apply savgol filter and derivative trigger to align the wfms
        indexes = np.array(derivative_trigger_matrix(Q1)) # choose whether to use I or Q for the savgol filter and choose parameters

        # code to align the samples
        # e.g. take the first entry as a reference and move the other
        delta = (indexes - indexes.min()).astype(int)
        end = (indexes - indexes.max() - 1).astype(int)

        # at the end it's necessary to cut the samples to have them all of the same length
        # - 1 in end needed to avoid Q[i][sth:0] that happened when indexes=indexes.max()
        # and returned an empty array
        new_I1, new_Q1, new_t1, new_I2, new_Q2, new_t2 = [], [], [], [], [], []

        #np.where
        for i in range(len(I1)):
            new_I1.append(I1[i][delta[i]:end[i]])
            new_Q1.append(Q1[i][delta[i]:end[i]])
            new_I2.append(I2[i][delta[i]:end[i]])
            new_Q2.append(Q2[i][delta[i]:end[i]])

        # use storage hdf5 from utils to store the new matrices
        storage_hdf5(path + 'savgol_' + file + '.h5', 'i_signal_ch0', new_I1, 'q_signal_ch0', new_Q1, 'timestamp_ch0', new_t1, 'i_signal_ch1', new_I2, 'q_signal_ch1', new_Q2, 'timestamp_ch1', new_t2)