import os

from src.utils import *
import numpy as np

# NOTE: do some tests to decide the best value for window_ma
# wl and poly are parameters for the savgol filter. They have already been optimized with simulated data
# Set the rigth POLARITY
# Apply derivative_trigger_matrix on the channel with the highest signal

new_I1, new_Q1, new_I2, new_Q2 = get_hdf5_2('/home/aperego/Documents/QTLab2122/SingleIRsource/data/raw/cont_acq_mix.h5')

#this part joins signal and noise for OF
path2  = '/home/aperego/Documents/QTLab2122/SingleIRsource/data/raw/cont_noise_1.h5'

NI1, NQ1, NI2, NQ2 = get_hdf5_2(path2)

a = np.concatenate((np.array(new_I1), np.array(NI1[:,:len(new_I1[0])])), axis=0)
b = np.concatenate((np.array(new_Q1), np.array(NQ1[:,:len(new_I1[0])])), axis=0)
c = np.concatenate((np.array(new_I2), np.array(NI2[:,:len(new_I1[0])])), axis=0)
d = np.concatenate((np.array(new_Q2), np.array(NQ2[:,:len(new_I1[0])])), axis=0)
t = np.linspace(0, len(a)-1, len(a))

storage_hdf5('/home/aperego/Documents/QTLab2122/SingleIRsource/data/clean/total/cont_acq_noise.h5', 'i_signal_ch0', a, 'q_signal_ch0', b, 'i_signal_ch1', c, 'q_signal_ch1', d, 'timestamp_ch0', t, 'timestamp_ch1', t )

print('Done :)')
        