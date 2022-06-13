import visa 
import numpy as np
import serial
import time
import os
import math
import h5py
import matplotlib.pyplot as plt
import csv
from pathlib import Path
path = os.getcwd()
path = Path(path)
print(Path(str(path.parent) + '\\Classes\\') )

import sys
sys.path.append(str(path.parent) + '\\Classes\\')
from SMA100B import *
from vna import *
from SIM928 import *



def get_hdf5(file, name_dataset):
    with h5py.File(file, 'r') as hdf:
        dati = np.array(hdf[name_dataset])
    return dati
        
def storage_hdf5(file, dati, name_dataset):

    with h5py.File(file, 'a') as hdf:
        if name_dataset not in hdf.keys():
            hdf.create_dataset(name_dataset, data=dati, compression='gzip', compression_opts=9)
    return None


def bump(k):
    if k % 100 == 0:
        return int(k/100) + 1
    else:
        return 1

def band_info(f, d):
    N = f.size
    gain = max(d)
    bw = f[d.argmax()+1]- f[d.argmax()]
    start = f[d.argmax()]
    for k in range(0, 100000):
        HPV = gain - 3 * bump(k)
        for i in range(0,N):
            if d[i] > HPV:
                break
        for j in range(0,N):
            if d[N-j-1] > HPV:
                break
        bw_new = f[N-j] - f[i]
        gain_new = np.mean(d[i:N-j])
        start = f[i]
        if abs(bw_new - bw)/bw < 0.001 and abs((gain_new-gain)/gain) < 0.001 and bw_new > 2e9:
            print('converged at %dth iteration!' % k)
            break
        else:
            gain = gain_new
            bw = bw_new
    return gain_new, bw_new, start

def band_width_info(f, d):
    N = f.size
    gain = max(d)
    bw = f[d.argmax()+1]- f[d.argmax()]
    start = f[d.argmax()]
    for k in range(0, 100000):
        HPV = gain - 3 * bump(k)
        for i in range(0,N):
            if d[i] > HPV:
                break
        for j in range(0,N):
            if d[N-j-1] > HPV:
                break
        bw_new = f[N-j] - f[i]
        gain_new = np.mean(d[i:N-j])
        i1 = i
        i2 = N-j
        if abs(bw_new - bw)/bw < 0.001 and abs((gain_new-gain)/gain) < 0.001 and bw_new > 2e9:
            #print('converged at %dth iteration!' % k)
            break
        else:
            gain = gain_new
            bw = bw_new
    return bw_new, i1, i2 #the band-width, and the indexes of the array f corresponding to its limits

def waitUntil(condition):
    wU = True
    while wU == True:
        if condition:
            wU = False
        else:
            time.sleep(0.5)

def my_plot(f, d, plot_title = None):
        #plt.figure(figsize=(20,15))
    f = f * 1e-9
    plt.plot(f,d)
    plt.grid()
    plt.xlabel('Frequencies (GHz)', fontsize=20)
    plt.ylabel('Power (dB)', fontsize=20)
    if plot_title != None:
        plt.title(plot_title, fontsize=24)
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)
    #plt.savefig(folder + '\\' + plot_title + '.png')
    plt.show()

def import_csv(folder, filename):  #filename w/o extension  
    data = []
    with open(r'C:\Users\oper\Desktop\labparamp\QTLab2122\TWPA\notebooks\data' + '\\' + folder + '\\' + filename + '.csv') as csvfile:
        reader = csv.reader(csvfile, quoting=csv.QUOTE_NONNUMERIC) # change contents to floats
        for row in reader: # each row is a list
            data.append(row)
    f = np.array(data[0])
    d = np.array(data[1])
    my_plot(f, d, filename)
    #my_plot(f, d, folder, filename)
    return f, d

def indexes_of_max(arr):
    return np.where(arr >= np.max(arr))

def envelopes(s, dmin=1, dmax=1, split=False):
    """
    Input :
    s: 1d-array, data signal from which to extract high and low envelopes
    dmin, dmax: int, optional, size of chunks, use this if the size of the input signal is too big
    split: bool, optional, if True, split the signal in half along its mean, might help to generate the envelope in some cases
    Output :
    s_low, s_high : low and high envelope of input signal s
    """

    # locals min      
    lmin = (np.diff(np.sign(np.diff(s))) > 0).nonzero()[0] + 1 
    # locals max
    lmax = (np.diff(np.sign(np.diff(s))) < 0).nonzero()[0] + 1 


    if split:
      # s_mid is zero if s centered around x-axis or more generally mean of signal
      s_mid = np.mean(s) 
      # pre-sorting of locals min based on relative position with respect to s_mid 
      lmin = lmin[s[lmin]<s_mid]
      # pre-sorting of local max based on relative position with respect to s_mid 
      lmax = lmax[s[lmax]>s_mid]


    # global max of dmax-chunks of locals max 
    lmin = lmin[[i+np.argmin(s[lmin[i:i+dmin]]) for i in range(0,len(lmin),dmin)]]
    # global min of dmin-chunks of locals min 
    lmax = lmax[[i+np.argmax(s[lmax[i:i+dmax]]) for i in range(0,len(lmax),dmax)]]


    t = np.arange(s.size)
    s_low = np.interp(t, t[lmin], s[lmin])
    s_high = np.interp(t, t[lmax], s[lmax])
    return s_low, s_high
