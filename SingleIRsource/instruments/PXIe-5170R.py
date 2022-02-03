# USEFUL REFERENCES
# Code example: https://github.com/js216/CeNTREX/blob/50282c7d3dfd4d47c3f96a6cde1b1cbb539821b5/drivers/PXIe5171.py
# niscope module docs: https://nimi-python.readthedocs.io/en/master/niscope.html
# niscope module examples: https://nimi-python.readthedocs.io/en/master/niscope/examples.html

import niscope
import argparse
import sys
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

class PXIeSignalAcq(object):

    def __init__(self, device_address, trigger=0, channels=[0,1], records=3, sample_rate=5e7, length=3000):
        try:
            self.session = niscope.Session(device_address)
            print('Connesso')
        except:
            print('Non connesso')

        self.length = length
        self.trigger = trigger
        self.channels = channels
        self.records = records
        self.session.configure_vertical(range = 5, coupling=niscope.VerticalCoupling.DC)
        self.session.configure_horizontal_timing(min_sample_rate=sample_rate, min_num_pts=length, ref_position=50.0, num_records=records, enforce_realtime=True)

    def read(self):
        wf = [] 
        wf.extend([self.session.channels[i].read(num_samples=self.length) for i in self.channels])
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
        print(self.dataframe.loc[0]["Samples"])
        return None

    # Set records (sampling frequency, rate, length, width,...)
    # Set triggers (edge, immediate, digital, negative, positive,...)
    # Set channels (addressing each channel)
    
    def close(self):
        return self.session.close()

test = PXIeSignalAcq("PXI1Slot2")
test.read()
test.create_dataframe()
test.fill_dataframe()
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