# USEFUL REFERENCES
# Code example: https://github.com/js216/CeNTREX/blob/50282c7d3dfd4d47c3f96a6cde1b1cbb539821b5/drivers/PXIe5171.py
# niscope module docs: https://nimi-python.readthedocs.io/en/master/niscope.html
# niscope module examples: https://nimi-python.readthedocs.io/en/master/niscope/examples.html
# PXIe manual: https://manualzz.com/doc/6830056/ni-scope-software-user-manual

import h5py 
import logging
import niscope as ni
import numpy as np

from sys import exit

class PXIeSignalAcq(object):

    logger = logging.getLogger(__name__)

    def __init__(self, device_address, trigger: dict, channels=[0,1], records=3, sample_rate=5e7, length=4000, ref_pos=20.0):
        
        try:
            self.session = ni.Session(device_address)

            self.logger.debug('Connected to PXIe')
        except:
            self.logger.debug('Not connected to PXIe')
 
        self.waveform = []
        self.i_matrix_ch0, self.q_matrix_ch0, self.timestamp_ch0 = [], [], []
        self.i_matrix_ch1, self.q_matrix_ch1, self.timestamp_ch1 = [], [], []

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

        self.get_status()

    def __enter__(self):
        return self
    
    def __exit__(self, *exc):
        self.logger.debug('Closed session')
        try:
            self.session.close()
        except ni.errors.DriverError as err:
            self.logger.error(str(err))
            exit() 

    def close(self):
        self.logger.debug('Closed session')
        try:
            self.session.close()
        except ni.errors.DriverError as err:
            self.logger.error(str(err))
            exit() 

    def read(self):
        try:
            self.waveform.extend([self.session.channels[i].read(num_samples=self.length, num_records=self.records, timeout=5) for i in self.channels])
        except ni.errors.DriverError as err:
            self.logger.error(str(err))
            exit()

        self.get_status()
        # Check if now works or still have problems with ni constants
        self.logger.debug('Time from the trigger event to the first point in the waveform record: ' + str(self.session.acquisition_start_time))
        self.logger.debug('Actual number of samples acquired in the record: ' + str(self.session.points_done))
        self.logger.debug('Number of records that have been completely acquired: ' + str(self.session.records_done))

        return None

    def fetch(self, timeout=10):
        try:
            self.session.initiate()
        except ni.errors.DriverError as err:
            self.logger.error(str(err))
            exit()

        self.get_status()

        self.waveform.extend([self.session.channels[i].fetch(num_samples=self.length, timeout=timeout, relative_to=ni.FetchRelativeTo.PRETRIGGER, num_records=self.records) for i in self.channels])
        """ try:
            self.waveform.extend([self.session.channels[i].fetch(num_samples=self.length, timeout=5, relative_to=ni.FetchRelativeTo.PRETRIGGER, num_records=self.records) for i in self.channels])
        except ni.errors.DriverError as err:
            self.logger.error(str(err))
            print('no')"""
            #it doesn't print anything MARCO

        # Check if now works or still have problems with ni constants -> now it works
        self.logger.debug('Time from the trigger event to the first point in the waveform record: ' + str(self.session.acquisition_start_time))
        self.logger.debug('Actual number of samples acquired in the record: ' + str(self.session.points_done))
        self.logger.debug('Number of records that have been completely acquired: ' + str(self.session.records_done))
        
        self.get_status()

        return None

    def continuous_acq(self, total_samples, samples_per_fetch):
        try:
            self.session.initiate()
        except ni.errors.DriverError as err:
            self.logger.error(str(err))
            exit()
        
        current_pos = 0
        self.waveform = [np.ndarray(total_samples, dtype=np.float64) for c in self.channels]

        self.get_status()

        while current_pos < total_samples:
            for channel, wfm in zip(self.channels, self.waveform):
                self.session.channels[channel].fetch_into(wfm[current_pos:current_pos + samples_per_fetch], relative_to=ni.FetchRelativeTo.READ_POINTER, offset=0, record_number=0, num_records=1)
                """try:
                    self.session.channels[channel].fetch_into(wfm[current_pos:current_pos + samples_per_fetch], relative_to=ni.FetchRelativeTo.READ_POINTER, offset=0, record_number=0, num_records=1)
                except ni.errors.DriverError as err:
                    self.logger.error(str(err))"""

            current_pos += samples_per_fetch

        #TEST
        self.i_matrix_ch0 = np.array(self.waveform[0])
        self.q_matrix_ch0 = np.array(self.waveform[1])
        self.i_matrix_ch1 = np.array(self.waveform[2])
        self.q_matrix_ch1 = np.array(self.waveform[3])

        #self.i_matrix_ch0.append(np.array(self.waveform[0]))
        #self.q_matrix_ch0.append(np.array(self.waveform[1]))
        #self.i_matrix_ch1.append(np.array(self.waveform[2]))
        #self.q_matrix_ch1.append(np.array(self.waveform[3]))

        self.logger.debug('Raw data I and Q were collected for continuous acquisition')

        return None

    def acq(self): # use this for frequencies scan, for each frequency takes some points and averages over them
        self.logger.debug('Scanning frequencies')
        self.i_matrix_ch0.append(np.array(self.session.channels[self.channels[0]].read(num_samples=self.length, timeout=5)[0].samples).mean())
        self.q_matrix_ch0.append(np.array(self.session.channels[self.channels[1]].read(num_samples=self.length, timeout=5)[0].samples).mean())
        self.i_matrix_ch1.append(np.array(self.session.channels[self.channels[2]].read(num_samples=self.length, timeout=5)[0].samples).mean())
        self.q_matrix_ch1.append(np.array(self.session.channels[self.channels[3]].read(num_samples=self.length, timeout=5)[0].samples).mean())

        return None

    def acq2(self): # use this for frequencies scan, for each frequency takes some points and averages over them
        self.logger.debug('Scanning frequencies')
        self.i_matrix.append(np.array(self.session.channels[self.channels[2]].read(num_samples=self.length, timeout=5)[0].samples).mean())
        self.q_matrix.append(np.array(self.session.channels[self.channels[3]].read(num_samples=self.length, timeout=5)[0].samples).mean())

        return None

    def fill_matrix(self, return_data=False):
        for i in range(self.records):
            self.i_matrix_ch0.append(np.array(self.waveform[0][i].samples))
            self.q_matrix_ch0.append(np.array(self.waveform[1][i].samples))
            self.timestamp_ch0.append(self.waveform[0][i].absolute_initial_x)
            self.i_matrix_ch1.append(np.array(self.waveform[2][i].samples))
            self.q_matrix_ch1.append(np.array(self.waveform[3][i].samples))
            self.timestamp_ch1.append(self.waveform[2][i].absolute_initial_x)
            
        self.logger.debug("Raw data I and Q were collected for trigger acquisition")

        if return_data:
            return self.i_matrix, self.q_matrix, self.timestamp
        else:
            return None
    
    def storage_hdf5(self, name):
        with h5py.File(name, 'w') as hdf:
            hdf.create_dataset('i_signal_ch0', data=self.i_matrix_ch0, compression='gzip', compression_opts=9)
            hdf.create_dataset('q_signal_ch0', data=self.q_matrix_ch0, compression='gzip', compression_opts=9)
            hdf.create_dataset('i_signal_ch1', data=self.i_matrix_ch1, compression='gzip', compression_opts=9)
            hdf.create_dataset('q_signal_ch1', data=self.q_matrix_ch1, compression='gzip', compression_opts=9)
            
            try:
                hdf.create_dataset('timestamp_ch0', data=self.timestamp_ch0, compression='gzip', compression_opts=9)
                hdf.create_dataset('timestamp_ch1', data=self.timestamp_ch1, compression='gzip', compression_opts=9)
            except:
                pass

        self.logger.debug("Raw data I and Q were stored in an HDF5 file: " + name)

        return None

    def get_hdf5(self, name): #only one channel
        with h5py.File(name, 'r') as hdf:
            I = np.array(hdf['i_signal_ch0'])
            Q = np.array(hdf['q_signal_ch0'])
            timestamp = np.array(hdf['timestamp_ch0'])

        self.logger.debug("Load the HDF5 file: " + name)

        return I, Q, timestamp

    def get_status(self):
        self.logger.debug("Acquisition status: " + str(self.session.acquisition_status())) # Understand why is print all this stuff in log
        return None