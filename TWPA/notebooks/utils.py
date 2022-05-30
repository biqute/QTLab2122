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



def get_hdf5(file, name_dataset):
    with h5py.File(file, 'r') as hdf:
        dati = np.array(hdf[name_dataset])
    return dati
        
def storage_hdf5(file, dati, name_dataset):

    with h5py.File(file, 'a') as hdf:
        if name_dataset not in hdf.keys():
            hdf.create_dataset(name_dataset, data=dati, compression='gzip', compression_opts=9)
    return None


def band_info(f, d):
    N = f.size
    HPV = max(d) - 3 #da capire bene. forse max(smoothing(d))-3? A -3dB cmq la potenza è dimezzata
    for i in range(0,N):
        if d[i] > HPV:
            break
    for j in range(0,N):
        if d[N-j-1] > HPV:
            break

    bw = f[N-j] - f[i]
    gain = np.mean(d[i:N-j]) #anche qui: d va lisciato?
    return gain, bw, f[i]

def waitUntil(condition):
    wU = True
    while wU == True:
        if condition:
            wU = False
        else:
            time.sleep(0.5)

def my_plot(f, d, plot_title = None):
    plt.figure(figsize=(20,15))
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
    a = np.where(arr >= np.max(arr),arr,0)
    ind = np.nonzero(a)
    return ind