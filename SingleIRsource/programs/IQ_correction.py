from instruments.FSW_0010 import *
from instruments.PXIe_5170R import *

########## Parameters that can be setted
freq1       = 5.869050          # frequency chosen to study I and Q (GHz)
freq2       = 5.869051          # frequency chosen to study I and Q (GHz)
file_name   = 'IQ_correction'   # name of the file where data will be saved
records     = 1                 # numer of records to store
channels    = [0,1]             # list of enabled channels
sample_rate = 2e3               # rate of points sampling of PXIe-5170R in Hz
total_time  = 1                 #total acquisition time in seconds
length      = int(total_time * sample_rate)

trigger = dict(
    trigger_type   = 'IMMEDIATE', #'EDGE', 'IMMEDIATE' or 'DIGITAL'
    trigger_source = '0',
    trigger_slope  = 'POSITIVE', #'POSITIVE' or 'NEGATIVE'
    trigger_level  = '0.0',
    trigger_delay  = '0.0'
)
###########      

# To simulate a programmable phase shifter we beat two synthesizers. 
# The output frequencies of the two synthesizers are set to be 1 kHz apart 
# and the IQ ellipses are digitized at a sample rate of 2 kHz for 1 second 
# (two circles are recorded)
with FSWSynt("COM7") as synt:
    #print(synt.get_ID())
    synt.set_freq(freq1)
    time.sleep(0.005) #IMPORTANT for real time communication
    print('The current frequency is: ' + synt.get_freq())    #just to check if the freqency has been set correctly

with FSWSynt("COM12") as synt:
    #print(synt.get_ID())
    synt.set_freq(freq2)
    time.sleep(0.005) #IMPORTANT for real time communication
    print('The current frequency is: ' + synt.get_freq())    #just to check if the freqency has been set correctly

I, Q = []
with PXIeSignalAcq("PXI1Slot2", trigger=trigger, records=records, channels=channels, sample_rate=sample_rate, length=length) as daq:
    daq.fetch()
    I, Q = daq.fill_matrix(return_data = True)

# fit of I and Q with an ellipse to retrieve a, b, phi 
# https://github.com/bdhammel/least-squares-ellipse-fitting
# https://pypi.org/project/lsq-ellipse/#description
a, b, phi = 0, 0, 0
# From these we can determine A_I, A_Q, gamma, the parameters that characterize a non-ideal IQ mixer
# The center of the ellipse is at (I0, Q0)

# From F.3
A_I = ((a*np.cos(phi))**2 + (b*np.sin(phi))**2)**0.5
A_Q = ((a*np.sin(phi))**2 + (b*np.cos(phi))**2)**0.5
alpha_1 = np.arctan(b*np.sin(phi)/a/np.cos(phi))
alpha_2 = np.pi - np.arctan(b*np.cos(phi)/a/np.sin(phi))
gamma = alpha_1 - alpha_2 

# See F.1 and F.2 for the expected I, Q signals

with open('IQ_mixer_calibration.csv','a+') as o:
    o.seek(0)
    header = 'frequency;A_I;A_Q;gamma;alpha_1;alpha_2'
    for line in o:
        if line.rstrip('\n\r') == header:
           break
    else: 
        o.write(header + '\n')
    o.write("{};{};{};{};{};{}\n".format(freq1, A_I, A_Q, gamma, alpha_1, alpha_2))
    print('done')

# we have to test also different powers?
# loop on power and frequencies -> in this case no with, open the channel only once