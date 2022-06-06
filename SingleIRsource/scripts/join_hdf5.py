import h5py
import os 
import numpy as np 

path = ('C:/Users/kid/Documents/QTLab2122/SingleIRsource/data/raw/edge_acq/good/')
path_save = ('C:/Users/kid/Documents/QTLab2122/SingleIRsource/data/raw/')
names =  [ 'acq_170522_205935.h5', 'acq_170522_210232.h5', 'acq_170522_210601.h5', 'acq_170522_210815.h5', 'acq_170522_210919.h5']


f = h5py.File(path_save + 'final_250522_222222.h5', 'a')
for i in range(len(names)):
  I1,  Q1,  I2,  Q2 = [], [], [], []
  with h5py.File(path + names[i], 'r') as hdf:
    I1 = np.array(hdf['i_signal_ch0'])
    Q1 = np.array(hdf['q_signal_ch0'])
    #I2 = np.array(hdf['i_signal_ch1'])
    #Q2 = np.array(hdf['q_signal_ch1'])

  if i == 0:
    # Create the dataset at first
    f.create_dataset('i_signal_ch0', data=I1, compression="gzip", chunks=True, maxshape=(None,None))
    f.create_dataset('q_signal_ch0', data=Q1, compression="gzip", chunks=True, maxshape=(None,None)) 
    #f.create_dataset('i_signal_ch1', data=I2, compression="gzip", chunks=True, maxshape=(None,None))
    #f.create_dataset('q_signal_ch1', data=Q2, compression="gzip", chunks=True, maxshape=(None,None)) 
  else:
    # Append new data to it
    f['i_signal_ch0'].resize((f['i_signal_ch0'].shape[0] + I1.shape[0]), axis=0)
    f['i_signal_ch0'][-I1.shape[0]:] = I1
    f['q_signal_ch0'].resize((f['q_signal_ch0'].shape[0] + Q1.shape[0]), axis=0)
    f['q_signal_ch0'][-Q1.shape[0]:] = Q1

    #f['i_signal_ch1'].resize((f['i_signal_ch1'].shape[0] + I2.shape[0]), axis=0)
    #f['i_signal_ch1'][-I2.shape[0]:] = I2
    #f['q_signal_ch1'].resize((f['q_signal_ch1'].shape[0] + Q2.shape[0]), axis=0)
    #f['q_signal_ch1'][-Q2.shape[0]:] = Q2

  print("I am on iteration {} and 'data' chunk has shape:{}".format(i,f['i_signal_ch0'].shape))
l = f['i_signal_ch0'].shape[0]
t = np.linspace(0, l-1, l)
f.create_dataset('timestamp_ch0', data=t, compression="gzip", chunks=True, maxshape=(None,))
#f.create_dataset('timestamp_ch1', data=t, compression="gzip", chunks=True, maxshape=(None,)) 
f.close()