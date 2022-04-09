# USEFUL REFERENCES
# Code example: https://github.com/js216/CeNTREX/blob/50282c7d3dfd4d47c3f96a6cde1b1cbb539821b5/drivers/PXIe5171.py
# niscope module docs: https://nimi-python.readthedocs.io/en/master/niscope.html
# niscope module examples: https://nimi-python.readthedocs.io/en/master/niscope/examples.html
# PXIe manual: https://manualzz.com/doc/6830056/ni-scope-software-user-manual

import niscope as ni
import h5py 
from scipy.signal import savgol_filter
from scipy.ndimage import convolve
import numpy as np

class PXIeSignalAcq(object):
    def __init__(self, device_address, trigger: dict, channels=[0,1], records=3, sample_rate=5e7, length=4000, ref_pos=40.0):
        try:
            self.session = ni.Session(device_address)
            print('Connected to PXIe :)')
        except:
            print('Not connected to PXIe :(')

        self.waveform, self.i_matrix, self.q_matrix = [], [], []

        self.length   = length
        self.trigger  = trigger
        self.channels = channels
        self.records  = records

        self.session.configure_vertical(range=1, coupling=ni.VerticalCoupling.DC)
        self.session.configure_horizontal_timing(min_sample_rate=sample_rate, min_num_pts=length, ref_position=ref_pos, num_records=records, enforce_realtime=True)

        if trigger["trigger_type"] == 'CONTINUOS':
            self.session.configure_trigger_software()
        else:
            self.session.trigger_type       = getattr(ni.TriggerType, trigger["trigger_type"])
            self.session.trigger_source     = trigger["trigger_source"]
            self.session.trigger_slope      = getattr(ni.TriggerSlope, trigger["trigger_slope"])
            self.session.trigger_level      = float(trigger["trigger_level"])
            self.session.trigger_delay_time = float(trigger["trigger_delay"])

        self.session.initiate()  # If fetch() don't comment, otherwise comment it

    def __enter__(self):
        return self
    
    def __exit__(self, *exc):
        self.session.close()

    def close(self):
        self.session.close()

    def vertex_parabola(x2, y1, y2, y3):
        x1 = x2 - 1
        x3 = x2 + 1
        b = x3 * x3 * (y2 - y1) + x2 * x2 * (y1 - y3) + x1 * x1 * (y3 - y2)
        a = (y2 - y3) * x1 + (y3 - y1) * x2 + (y1 - y2) * x3

        return -b/(2*a)

    def derivative_trigger_matrix(self, sample, window_ma=20, wl=60, poly=4, n=2, vertex=True):
        weights = np.full((1, window_ma), 1/window_ma)
        moving_averages = convolve(sample, weights, mode='mirror')

        index_mins = []

        for i in range(len(sample)):

            first_derivative = np.gradient(moving_averages[i])
            std = np.std(first_derivative[0:50])/2 #50 will become a function of length and pos_ref in pxie
            index_min = first_derivative.argmin()
            
            rise_points = 0

            while first_derivative[index_min - rise_points] < -std:
                rise_points += 1

            a = 10
            start = index_min - rise_points

            if start < a:
                start = a

            if start > len(sample[i])-2*a:
                start = len(sample[i])-2*a
            
            end = start + 2*a
            begin = start - a
            
            derivative_func = savgol_filter(sample[i], wl, poly, n, delta=1, mode='mirror')

            x2 = begin+1+(derivative_func[begin+1:end-1].argmin())

            if vertex:
                y1 = derivative_func[x2-1]
                y2 = derivative_func[x2]
                y3 = derivative_func[x2+1]
                min = int(np.round(self.vertex_parabola(x2, y1, y2, y3)))
            else:
                min = x2

            index_mins.append(min)

        return index_mins


    def read(self):
        self.waveform.extend([self.session.channels[i].read(num_samples=self.length, num_records=self.records, timeout=0) for i in self.channels])
        #print(np.array(self.session.channels[0].read(num_samples=self.length, timeout=0)[0].samples))
        #self.i_matrix.append(np.array(self.session.channels[2].read(num_samples=self.length, timeout=0)[0].samples))
        #self.q_matrix.append(np.array(self.session.channels[3].read(num_samples=self.length, timeout=0)[0].samples))
        return None

    def fetch(self):
        self.waveform.extend([self.session.channels[i].fetch(num_samples=self.length, timeout=10, relative_to = ni.FetchRelativeTo.PRETRIGGER) for i in self.channels])
        return None

    def continuos_acq(self, total_samples, samples_per_fetch):
        current_pos = 0
        self.waveform = [np.ndarray(total_samples, dtype=np.float64) for c in self.channels]
        while current_pos < total_samples:
            for channel, wfm in zip(self.channels, self.waveform):
                self.session.channels[channel].fetch_into(wfm[current_pos:current_pos + samples_per_fetch], relative_to=ni.FetchRelativeTo.READ_POINTER,
                                                          offset=0, record_number=0, num_records=1)
            current_pos += samples_per_fetch
        return None

    def acq(self): # NEED TEST
        self.i_matrix.append(np.array(self.session.channels[self.channels[0]].read(num_samples=self.length, timeout=0)[0].samples))
        self.q_matrix.append(np.array(self.session.channels[self.channels[1]].read(num_samples=self.length, timeout=0)[0].samples))
        return None

    def fill_matrix(self, iter=0, return_data = False):
        iter = self.records if iter == 0 else iter
        for i in range(iter):
            self.i_matrix.append(np.array(self.waveform[0][i].samples))
            self.q_matrix.append(np.array(self.waveform[1][i].samples))
        if return_data:
            return self.i_matrix, self.q_matrix
        else:
            return None
    
    def get_timestamps(self, name):
        i_time = []
        q_time = []
        for i in range(self.records):
            i_time.append(self.waveform[0][i].absolute_initial_x) #if this doesn't work, try str(waveforms[i]) for some i that can be found with 'Waveform {0} information:'.format(i)
            q_time.append(self.waveform[1][i].absolute_initial_x)
        with h5py.File(name, 'w') as hdf:
            hdf.create_dataset('i_timestamps', data=i_time, compression='gzip', compression_opts=9)
            hdf.create_dataset('q_timestamps', data=q_time, compression='gzip', compression_opts=9)
        return None
    
    def storage_hdf5(self, name):
        with h5py.File(name, 'w') as hdf:
            hdf.create_dataset('i_signal', data=self.i_matrix, compression='gzip', compression_opts=9)
            hdf.create_dataset('q_signal', data=self.q_matrix, compression='gzip', compression_opts=9)
        return None

    def get_hdf5(self, name):
        with h5py.File(name, 'r') as hdf:
            for i in range(0,self.records):
                print("Segnale I")
                print(np.array(hdf['i_signal'])[i])
                print("Segnale Q")
                print(np.array(hdf['q_signal'])[i])
        return None