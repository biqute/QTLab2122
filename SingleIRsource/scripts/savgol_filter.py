import os

from src.utils import *
import numpy as np

# NOTE: do some tests to decide the best value for window_ma
# wl and poly are parameters for the savgol filter. They have already been optimized with simulated data
# Set the rigth POLARITY
# Apply derivative_trigger_matrix on the channel with the highest signal

path  = 'C:/Users/kid/Documents/QTLab2122/SingleIRsource/data/raw/edge_acq/good/'
path_save = 'C:/Users/kid/Documents/QTLab2122/SingleIRsource/data/savgol/'
files = os.listdir(path)


new_I1, new_Q1, new_I2, new_Q2 = [], [], [], []
for file in files:
    if 'config' in file:
        continue
    else:
        #I1, Q1, t1, I2, Q2, t2 = get_hdf5_time(path + file)
        I1, Q1, I2, Q2 = [], [], [], []
        I1, Q1, I2, Q2 = get_hdf5_2(path + file)

        print('Data from ', file, ' loaded. Apply savgol..')
        # apply savgol filter and derivative trigger to align the wfms
        indexes = np.array(derivative_trigger_matrix(Q1, window_ma=20, wl=60, poly=4, polarity=1)) # choose whether to use I or Q for the savgol filter and choose parameters
        print('Applied. Now the indexes..')
        #print(indexes)
        # code to align the samples
        # e.g. take the first entry as a reference and move the other
        delta = (indexes - indexes.min()).astype(int)
        end = delta + (indexes - indexes.max() - 1).astype(int) # or fixed, eg delta + 5000 

        print(len(I1[0][delta[0]:end[0]]))
        if (end[0]-delta[0])%2!=0:
            end = end -1

        # at the end it's necessary to cut the samples to have them all of the same length
        # - 1 in end needed to avoid Q[i][sth:0] that happened when indexes=indexes.max()
        # and returned an empty array
        
        #np.where could speed up the process
        for i in range(len(I1)):
            new_I1.append(I1[i][delta[i]:end[i]])
            new_Q1.append(Q1[i][delta[i]:end[i]])
            new_I2.append(I2[i][delta[i]:end[i]])
            new_Q2.append(Q2[i][delta[i]:end[i]])

        print('Done.')

    print('Done. Loading..')

    # use storage hdf5 from utils to store the new matrices
    t = np.linspace(0, len(new_Q1)-1, len(new_Q1))
    storage_hdf5(path_save + 'savgol_' + file, 'i_signal_ch0', new_I1, 'q_signal_ch0', new_Q1, 'timestamp_ch0', t, 'i_signal_ch1', new_I2, 'q_signal_ch1', new_Q2, 'timestamp_ch1', t)
    print('Done :)')
    
    """
    #this part joins signal and noise for OF
    path2  = '../data/raw/edge_acq/'
    file2 = 'noise_180522_183913.h5' #os.listdir(path)

    NI1, NQ1, Nt1, NI2, NQ2, Nt2 = get_hdf5_time(path2 + file2)

    a = np.concatenate((np.array(new_I1), np.array(NI1[:,:len(new_I1[0])])), axis=0)
    b = np.concatenate((np.array(new_Q1), np.array(NQ1[:,:len(new_I1[0])])), axis=0)
    c = np.concatenate((np.array(new_I2), np.array(NI2[:,:len(new_I1[0])])), axis=0)
    d = np.concatenate((np.array(new_Q2), np.array(NQ2[:,:len(new_I1[0])])), axis=0)
    t = np.linspace(0, len(a)-1, len(a))

    storage_hdf5('../data/clean/total/' + 'tot_' + file, 'i_matrix_ch0', a, 'q_matrix_ch0', b, 'i_matrix_ch1', c, 'q_matrix_ch1', d, 'timestamp_ch0', t, 'timestamp_ch1', t )

    print('Done :)')"""
    