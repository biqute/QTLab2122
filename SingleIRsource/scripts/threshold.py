import numpy as np
import matplotlib.pyplot as plt
from src.utils import *

# Open h5 file from acquisition with a low trigger and get the waveform matrices
I, Q = get_hdf5('scan_freq.h5')

#Choose on which channel apply the trigger (e.g. I)
min = np.amin(I)
max = np.amax(I)
threshold = np.linspace(min, max, 1000)

counts = np.zeros(len(threshold))
    
plt.figure(dpi = 300)

#### to check if the signal is positive or negative
mean = np.mean(I[0][0:10])
positive = True if np.abs(mean-I[0].min()) < np.abs(mean-I[0].max()) else False
####

#check if the signal/noise is under the threshold 
if positive:
    for i in range(0, len(I)):
        j=0
        for thr in threshold:
            if I[i].max() > thr: 
                counts[j] += 1
            j+=1
    plt.ylabel('# of waveforms over threshold')
else:
    for i in range(0, len(I)):
        j=0
        for thr in threshold:
            if I[i].min() < thr:  
                counts[j] += 1
            j+=1
    plt.ylabel('# of waveforms under threshold')

plt.scatter(threshold, counts, s=1, c='red') # Nice color

plt.title('Evaluating different thresholds to find the best one')
plt.xlabel('Threshold values')
plt.legend()
plt.grid()
plt.savefig('threshold.png')

# return also a file w/ counts VS threshold?
# with open('thresholds.csv', 'a') as file:
#     for i in range(len(threshold)):
#         file.write('{};{}\n'.format(threshold[i], counts[i]))