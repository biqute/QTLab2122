import numpy as np
import matplotlib.pyplot as plt
from trigger import *
import h5py

n_sample = 1000
amplitude = np.linspace(10, 1000, 100)
moving_average = np.linspace(3, 9, 7)

for amp in amplitude:
    data = []
    avg = []
    for j in range(n_sample):
        signal = gen_signal(baseline=-10, amplitude=amp, noise_lev=1) #pulse_start = np.random.uniform(pulse_start-0.5,pulse_start+0.5)
        data.append(signal)
        moving_averages = []
        window_size = 15
        i=0
        while i < len(signal) - window_size + 1:
            window = signal[i : i + window_size]
            window_average = round(sum(window) / window_size, 2)
            moving_averages.append(window_average)
            i += 1
        avg.append(moving_averages)

    fname = 'data_sim/signal_amp_' + str(int(amp)) + '.h5'
    with h5py.File(fname, 'w') as hdf:
            hdf.create_dataset('signal', data=data, compression='gzip', compression_opts=9)
            hdf.create_dataset('moving_average', data=avg, compression='gzip', compression_opts=9)