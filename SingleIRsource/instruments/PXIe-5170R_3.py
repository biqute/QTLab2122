import niscope as ni
import h5py
from scipy.signal import savgol_filter

class PXIeSignalAcq(object):
    def __init__(self, device_address, trigger=0, channels=[0,1], records=3, sample_rate=5e7, length=4000):
        try:
            self.session = ni.Session(device_address)
            print('Connected')
        except:
            print('Not connected')

        self.waveform, self.i_matrix, self.q_matrix = [], [], []

        self.length       = length
        self.trigger      = trigger
        self.channels     = channels
        self.records      = records

        self.session.configure_vertical(range=5, coupling=ni.VerticalCoupling.DC)
        self.session.configure_horizontal_timing(min_sample_rate=sample_rate, min_num_pts=length, ref_position=40.0, num_records=records, enforce_realtime=True)

        # When we pass trigger=0 in the constructor, we can pass all this settings
        self.session.trigger_type       = ni.TriggerType.EDGE
        self.session.trigger_source     = "0"
        self.session.trigger_slope      = ni.TriggerSlope.POSITIVE
        self.session.trigger_level      = 0.5
        self.session.trigger_delay_time = 0.0

        self.session.initiate()
    
    def __enter__(self):
        return self
    
    def __exit__(self, *exc):
        self.session.close()

    def derivative_trigger(self, index, n, limit):
        # We can focus only one signal (I in this case) and then apply the corrections on both
        sample = self.waveform[0][index].samples

        # Same problem of the following comment
        derivative_func = savgol_filter(sample[1360:1480], len(sample[1360:1480])-1, 12, n, delta=1)

        if (derivative_func.max() > limit):
            # We need to understand and automatize the centering of impulse and resizing the window length

            self.waveform[0][index].samples = self.waveform[0][index].samples[1360:1480]
            self.waveform[1][index].samples = self.waveform[1][index].samples[1360:1480]
            return True
        else:
            return False

    def read(self):
        self.waveform.extend([self.session.channels[i].read(num_samples=self.length, timeout=0) for i in self.channels])
        return None

    def fill_matrix(self):
        for i in range(self.records):
            if (self.derivative_trigger(2, i)):
                self.i_matrix.append(self.waveform[0][i].samples)
                self.q_matrix.append(self.waveform[1][i].samples)
        return None
    
    def storage_hdf5(self, name):
        with h5py.File(name, 'w') as hdf:
            hdf.create_dataset('i_signal', data=self.i_matrix, compression='gzip', compression_opts=9)
            hdf.create_dataset('q_signal', data=self.q_matrix, compression='gzip', compression_opts=9)
        return None

with PXIeSignalAcq("PXI1Slot2") as test:
    test = PXIeSignalAcq("PXI1Slot2")
    test.read()
    test.fill_matrix()
    test.storage_hdf5('signals.h5')