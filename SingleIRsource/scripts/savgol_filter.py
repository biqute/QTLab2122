import os

from src.utils import *

path = 'data/raw/edge_acq/'
files = os.listdir(path)

for file in files:
    if 'config' in file:
        continue
    else:
        I, Q, timestamp = [], [], []
        I, Q, timestamp = get_hdf5_time(file)

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
        storage_hdf5(path + 'savgol_' + file + '.h5', 'i_signal', new_I, 'q_signal', new_Q, 'timestamp', timestamp)