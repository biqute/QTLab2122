# USEFUL REFERENCES
# Code example: https://github.com/js216/CeNTREX/blob/50282c7d3dfd4d47c3f96a6cde1b1cbb539821b5/drivers/PXIe5171.py
# niscope module docs: https://nimi-python.readthedocs.io/en/master/niscope.html
# niscope module examples: https://nimi-python.readthedocs.io/en/master/niscope/examples.html

import niscope

class PXIeSignalAcq(object):

    def __init__(self, device_address):
        self.session = niscope.Session(device_address)
    
    # Set records (sampling frequency, rate, lenght, width,...)
    # Set triggers (edge, immediate, digital, negative, positive,...)
    # Set channels (addressing each channel)
    
    def close(self):
        return self.session.close()