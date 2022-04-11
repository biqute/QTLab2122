# USEFUL REFERENCES
# Code example: https://github.com/js216/CeNTREX/blob/50282c7d3dfd4d47c3f96a6cde1b1cbb539821b5/drivers/PXIe5171.py
# niscope module docs: https://nimi-python.readthedocs.io/en/master/niscope.html
# niscope module examples: https://nimi-python.readthedocs.io/en/master/niscope/examples.html
# PXIe manual: https://manualzz.com/doc/6830056/ni-scope-software-user-manual

import logging
import niscope as ni
import h5py 
import numpy as np
from datetime import datetime
import time 

date = datetime.now().strftime("%m-%d-%Y")

class PXIeSignalAcq(object):

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(funcName)s - %(levelname)s - %(message)s', "%Y-%m-%d %H:%M:%S")

    file_handler = logging.FileHandler('logs/session_' + date + '.log')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.DEBUG)
    logger.addHandler(console_handler)

    def __init__(self, device_address, trigger: dict, channels=[0,1], records=3, sample_rate=5e7, length=4000, ref_pos=40.0):
        
        try:
            self.session = ni.Session(device_address)

            self.logger.info('Connected to PXIe')
        except:
            self.logger.info('Not connected to PXIe')

        self.waveform, self.i_matrix, self.q_matrix, self.timestamp = [], [], [], []

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

    def read(self):
        self.waveform.extend([self.session.channels[i].read(num_samples=self.length, num_records=self.records, timeout=0) for i in self.channels])
        #print(np.array(self.session.channels[0].read(num_samples=self.length, timeout=0)[0].samples))
        #self.i_matrix.append(np.array(self.session.channels[2].read(num_samples=self.length, timeout=0)[0].samples))
        #self.q_matrix.append(np.array(self.session.channels[3].read(num_samples=self.length, timeout=0)[0].samples))
        return None

    def fetch(self):
        start = time.time()
        try:
            self.waveform.extend([self.session.channels[i].fetch(num_samples=self.length, timeout=10, relative_to = ni.FetchRelativeTo.PRETRIGGER) for i in self.channels])
        except ni.errors.DriverError as err:
            self.logger.error(str(err))
        self.logger.info(time.time()-start)
        return None

    def continuos_acq(self, total_samples, samples_per_fetch):
        current_pos = 0
        self.waveform = [np.ndarray(total_samples, dtype=np.float64) for c in self.channels]
        while current_pos < total_samples:
            for channel, wfm in zip(self.channels, self.waveform):
                self.session.channels[channel].fetch_into(wfm[current_pos:current_pos + samples_per_fetch], relative_to=ni.FetchRelativeTo.READ_POINTER,
                                                          offset=0, record_number=0, num_records=1)
            current_pos += samples_per_fetch
        self.i_matrix.append(np.array(self.waveform[0]))
        self.q_matrix.append(np.array(self.waveform[1]))

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
            self.timestamp.append(self.waveform[0][i].absolute_initial_x)
        if return_data:
            return self.i_matrix, self.q_matrix, self.timestamp
        else:
            return None
    
    def storage_hdf5(self, name):
        with h5py.File(name, 'w') as hdf:
            hdf.create_dataset('i_signal', data=self.i_matrix, compression='gzip', compression_opts=9)
            hdf.create_dataset('q_signal', data=self.q_matrix, compression='gzip', compression_opts=9)
            try:
                hdf.create_dataset('timestamp', data=self.timestamp, compression='gzip', compression_opts=9)
            except:
                pass
        return None

    def get_hdf5(self, name):
        with h5py.File(name, 'r') as hdf:
            I = np.array(hdf['i_signal'])
            Q = np.array(hdf['q_signal'])
            timestamp = np.array(hdf['timestamp'])
        return I, Q, timestamp