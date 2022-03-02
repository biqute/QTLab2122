# USEFUL REFERENCES
# Code example: https://github.com/js216/CeNTREX/blob/50282c7d3dfd4d47c3f96a6cde1b1cbb539821b5/drivers/PXIe5171.py
# niscope module docs: https://nimi-python.readthedocs.io/en/master/niscope.html
# niscope module examples: https://nimi-python.readthedocs.io/en/master/niscope/examples.html
# https://manualzz.com/doc/6830056/ni-scope-software-user-manual

import niscope as ni
import h5py 
from scipy.signal import savgol_filter
import numpy as np

class PXIeSignalAcq(object):
    def __init__(self, device_address, trigger: dict, channels=[0,1], records=3, sample_rate=5e7, length=4000):
        try:
            self.session = ni.Session(device_address)
            print('Connected')
        except:
            print('Not connected')

        self.waveform, self.i_matrix, self.q_matrix = [], [], []

        self.length     = length
        self.trigger    = trigger
        self.channels   = channels
        self.records    = records

        self.session.configure_vertical(range=5, coupling=ni.VerticalCoupling.DC)
        self.session.configure_horizontal_timing(min_sample_rate=sample_rate, min_num_pts=length, ref_position=40.0, num_records=records, enforce_realtime=True)

        self.session.trigger_type       = getattr(ni.TriggerType, trigger["trigger_type"])
        self.session.trigger_source     = trigger["trigger_source"]
        self.session.trigger_slope      = getattr(ni.TriggerSlope, trigger["trigger_slope"])
        self.session.trigger_level      = float(trigger["trigger_level"])
        self.session.trigger_delay_time = float(trigger["trigger_delay"])

        self.session.initiate()

    def __enter__(self):
        return self
    
    def __exit__(self, *exc):
        self.session.close()

    def close(self):
        self.session.close()

    def derivative_trigger(self, index, n=2):
        # We can focus only one signal (channel 0 in this case) and then apply the corrections on both
        sample = self.waveform[0][index].samples

        first_derivative = np.diff(sample, n = 1)
        n_points, i = 0, 0
        std = np.std(sample[0:1000])/2 
        max = sample.argmax()
        tot = max
        
        while(sample[max])>std:
            max -= 1
        tot = tot - max

        while(n_points<tot): #si può aumentare n_points
            n_points = n_points + 1 if (sample[i] > std) else 0
            i += 1

        start = i - tot
        end = start + 100 #numero a caso, si intende la lunghezza di salita e una parte di discesa

        #problema: la derivata seconda fatta solo dove inizia l'impulso è inutile secondo me
        #si può, una volta trovato l'inizio, fare la derivata solo per salita e una parte di discesa
        #a questo punto ha senso parlare del massimo della derivata seconda sopra un certo limite
        #in realtà minimo perchè la derivata seconda è negativa dove interessa a noi

        derivative_func = savgol_filter(sample[begin:end], len(sample[begin:end])-1, 12, n, delta=1)

        #limite di -0.5 da valutare..
        under_threshold = np.count_nonzero(derivative_func < -0.5)
        if (under_threshold > 50): #altro numero a caso, da capire
            # We need to understand and automatize the centering of impulse and resizing the window length
            begin = start - 200 #quanti punti prima dell'inizio?
            end = start + 2000 #quanto è lungo l'impulso?
            self.waveform[0][index].samples = self.waveform[0][index].samples[begin:end]
            self.waveform[1][index].samples = self.waveform[1][index].samples[begin:end]
            return True
        else:
            return False

    def read(self):
        self.waveform.extend([self.session.channels[i].read(num_samples=self.length, timeout=0) for i in self.channels])
        #print(np.array(self.session.channels[0].read(num_samples=self.length, timeout=0)[0].samples))
        self.i_matrix.append(np.array(self.session.channels[0].read(num_samples=self.length, timeout=0)[0].samples))
        self.q_matrix.append(np.array(self.session.channels[1].read(num_samples=self.length, timeout=0)[0].samples))
        return None

    def fill_matrix(self, iter = 0):
        iter = self.records if iter == 0 else iter
        for i in range(iter):
            #if (self.derivative_trigger(2, i)):
            self.i_matrix.append(np.array(self.waveform[0][i].samples))
            self.q_matrix.append(np.array(self.waveform[1][i].samples))
        return None
    
    def storage_hdf5(self, name):
        with h5py.File(name, 'w') as hdf:
            hdf.create_dataset('i_signal', data=self.i_matrix, compression='gzip', compression_opts=9)
            hdf.create_dataset('q_signal', data=self.q_matrix, compression='gzip', compression_opts=9)
        return None

    def get_hdf5(self, name):
        with h5py.File(name, 'r') as hdf:
            for i in range(0,3):
                print("Segnale I")
                print(np.array(hdf['i_signal'])[i])
                print("Segnale Q")
                print(np.array(hdf['q_signal'])[i])
        return None

"""
trigger = dict(
    trigger_type = 'IMMEDIATE', # 'EDGE' or 'IMMEDIATE', 'DIGITAL'
    trigger_source = '0',
    trigger_slope = 'POSITIVE', # or 'NEGATIVE'
    trigger_level = '0.0',
    trigger_delay = '0.0'
)
with PXIeSignalAcq("PXI1Slot2", trigger) as test:
    test = PXIeSignalAcq("PXI1Slot2", trigger)
    test.read()
    test.fill_matrix()
    test.storage_hdf5('signals.h5')
    test.get_hdf5('signals.h5')



##########################


import numpy as np
import matplotlib.pyplot as plt


class PXIeSignalAcq(object):

    def derivative_trigger(self, n, arr):
        # arr = self.waveform[0][self.record_index].samples
        y = savgol_filter(arr, self.length, 70, n, delta=1)
        filtred = np.where(y[250:len(y)-250] < -0.5e-5)[0]

        if len(filtred) == 0 : #no signal
            return -1

        ref_point = filtred[0] + 250

        start = ref_point - 300 
        end   = ref_point + 1600
        # window_length = 2000
        # pre_trigger   = 0.2
        # post_trigger  = 1- pre_trigger
        # start = ref_point - (pre_trigger * window_length) 
        # end   = ref_point + (post_trigger * window_length) 

        self.record_index += 1

        return arr[start:end]
    
    def plot_waveform(self):
        for i in range(self.records):
            sample = self.dataframe.loc[i]["Samples"]
            x = np.linspace(0,len(sample)-1,len(sample))
            
            # plt.ylim(-10,10)
            plt.scatter(x, sample)
            plt.savefig("imm" + str(i) + ".png")
        """

"""
def example(resource_name, channels, options, length, voltage):
    with niscope.Session(resource_name=resource_name, options=options) as session:
        session.configure_vertical(range=voltage, coupling=niscope.VerticalCoupling.DC)
        session.configure_horizontal_timing(min_sample_rate=50000000, min_num_pts=length, ref_position=50.0, num_records=1, enforce_realtime=True)
        wave_info = session.channels[channels].read(num_samples=length)
        for i in range(len(wave_info)):
            print('Waveform {0} information:'.format(i))
            print(str(wave_info[i]) + '\n\n')
            sample = list(wave_info[i].samples)
        
        x = np.linspace(0,len(sample)-1,len(sample))
        plt.scatter(x, sample)
        plt.savefig("imm1.png")


def _main(argsv):
    parser = argparse.ArgumentParser(description='Acquires one record from the given channels.', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-n', '--resource-name', default='PXI1Slot2', help='Resource name of a National Instruments Digitizer')
    parser.add_argument('-c', '--channels', default='0', help='Channel(s) to use')
    parser.add_argument('-l', '--length', default=10000, type=int, help='Measure record length')
    parser.add_argument('-v', '--voltage', default=2, type=float, help='Voltage range (V)')
    parser.add_argument('-op', '--option-string', default='', type=str, help='Option string')
    args = parser.parse_args(argsv)
    example(args.resource_name, args.channels, args.option_string, args.length, args.voltage)

def main():
    _main(sys.argv[1:])

main()"""