# USEFUL REFERENCES
# Code example: https://github.com/js216/CeNTREX/blob/50282c7d3dfd4d47c3f96a6cde1b1cbb539821b5/drivers/PXIe5171.py
# niscope module docs: https://nimi-python.readthedocs.io/en/master/niscope.html
# niscope module examples: https://nimi-python.readthedocs.io/en/master/niscope/examples.html
# https://manualzz.com/doc/6830056/ni-scope-software-user-manual

from operator import index
import niscope
import argparse
import sys
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.signal import savgol_filter

class PXIeSignalAcq(object):

    def __init__(self, device_address, trigger=0, channels=[0], records=3, sample_rate=5e7, length=4000):
        try:
            self.session = niscope.Session(device_address)
            print('Connesso')
        except:
            print('Non connesso')

        self.length = length
        self.trigger = trigger
        self.channels = channels
        self.records = records
        self.record_index = 0

        self.session.configure_vertical(range = 5, coupling=niscope.VerticalCoupling.DC)
        self.session.configure_horizontal_timing(min_sample_rate=sample_rate, min_num_pts=length, ref_position=40.0, num_records=records, enforce_realtime=True)

        self.session.trigger_type = niscope.TriggerType.EDGE
        self.session.trigger_source = "0"
        self.session.trigger_slope = niscope.TriggerSlope.POSITIVE
        self.session.trigger_level = 0.5
        self.session.trigger_delay_time = 0.0

        self.session.initiate()

    def derivative_trigger(self, n):
        arr = self.waveform[0][self.record_index].samples
        y = savgol_filter(arr, self.length, 70, n, delta=1)
        filtred = np.where(y[250:len(y)-250] < -0.5e-5)[0]

        if len(filtred) == 0 :
            return -1

        ref_point = filtred[0] + 250

        start = ref_point - 300 
        end = ref_point + 1600
        
        self.record_index += 1

        return arr[start:end]


    def read(self):
        wf = [] 
        wf.extend([self.session.channels[i].read(num_samples=self.length, timeout=0) for i in self.channels])
        self.waveform = wf
        #print(wf)
        return None

    def create_dataframe(self):
        index = []
        index.extend([i for i in range(0, len(self.channels) * self.records)])
        self.dataframe = pd.DataFrame(index = index, columns = ["Record", "Channel", "Samples"])
        return None

    def fill_dataframe(self):
        for i in range(self.records):
            for j in self.channels:
                self.dataframe.loc[i*len(self.channels) + j]["Record"] = i
                self.dataframe.loc[i*len(self.channels) + j]["Channel"] = j
                self.dataframe.loc[i*len(self.channels) + j]["Samples"] = list(self.waveform[j][i].samples)
        # print(self.dataframe.loc[0]["Samples"])
        return None

    def save_dataframe(self, name = "data1.json"):
        self.dataframe.to_json(name)
        return None

    def read_dataframe(self, name = "data1.json"):
        prova = pd.read_json(name)

        for i in range(self.records):
            sample = prova.loc[i]["Samples"]
            x = np.linspace(0,len(sample)-1,len(sample))
            y = savgol_filter(sample, self.length, 70, 2, delta=1)

            filtred = np.where(y[250:len(y)-250] < -0.5e-5)[0]
            # se filtred è nullo esce. no segnale. MEGA IF

            ref_point = filtred[0] + 250
            print(ref_point)

            start = ref_point - 300 
            end = ref_point + 1600
            
            final = sample[start:end]


            

            fig, ax1 = plt.subplots()
            ax2 = ax1.twinx()
           # ax1.scatter(x[start:end], sample[start:end], color='g', marker=".")
            ax2.scatter(x[start:end], final, marker=".")
            # plt.ylim(-10,10)
            # plt.scatter(x, sample)
            # plt.scatter(x, y)
            fig.savefig("imm" + str(i) + ".png")
        
    # Set records (sampling frequency, rate, length, width,...)
    # Set triggers (edge, immediate, digital, negative, positive,...)
    # Set channels (addressing each channel)
    def __enter__(self):
        return self
    def __exit__(self, *exc):
        self.session.close()

with PXIeSignalAcq("PXI1Slot2") as test:
    #test = PXIeSignalAcq("PXI1Slot2")
    test.read()
    test.create_dataframe()
    test.fill_dataframe()
    test.save_dataframe()
    test.read_dataframe()


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