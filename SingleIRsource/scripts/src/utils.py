#useful functions for plot, derivatives...

import h5py
import logging
import numpy              as np
import matplotlib.pyplot  as plt
from   ellipse            import LsqEllipse # install lsq-ellipse
from   matplotlib.patches import Ellipse
from   datetime           import datetime
from   scipy.signal       import savgol_filter
from   scipy.ndimage      import convolve
logger = logging.getLogger(__name__)

# Get current date and time to have unique file names
def get_date(file_name = None):
    now = datetime.now()
    date= now.strftime("%d%m%y")
    hour = now.strftime("%H%M%S")
    name = file_name + '_' + date + '_' + hour
    return (date, hour) if file_name == None else name

#store data in hdf5 file
#first pass the file name, then the name of the dataset and the matrix to store. Repeat the last two steps for each matrix
def storage_hdf5(file, *args):
    with h5py.File(file, 'w') as hdf:
        for i in range(0, len(args), 2):  
            hdf.create_dataset(args[i], data=args[i+1], compression='gzip', compression_opts=9)
            #hdf.create_dataset('q_signal', data=q_matrix, compression='gzip', compression_opts=9)
    logging.debug('Stored data in an HDF5 file: ' + file)
    return None

#returns two matrices, I and Q
#useful for acquisition, where many records are acquired
def get_hdf5(name): 
    with h5py.File(name, 'r') as hdf:
        I = np.array(hdf['i_signal'])
        Q = np.array(hdf['q_signal'])
    logger.debug("Load the HDF5 file: " + name)
    return I, Q

def get_hdf5_2(name): 
    with h5py.File(name, 'r') as hdf:
        I1 = np.array(hdf['i_signal_ch0'])
        Q1 = np.array(hdf['q_signal_ch0'])
        I2 = np.array(hdf['i_signal_ch1'])
        Q2 = np.array(hdf['q_signal_ch1'])
    logger.debug("Load the HDF5 file: " + name)
    return I1, Q1, I2, Q2

#returns two matrices, I and Q and their timestamps
#useful for acquisition, where many records are acquired
def get_hdf5_time(name): 
    with h5py.File(name, 'r') as hdf:
        I1 = np.array(hdf['i_signal_ch0'])
        Q1 = np.array(hdf['q_signal_ch0'])
        t1 = np.array(hdf['timestamp_ch0'])
        I2 = np.array(hdf['i_signal_ch1'])
        Q2 = np.array(hdf['q_signal_ch1'])
        t2 = np.array(hdf['timestamp_ch1'])
    logger.debug("Load the HDF5 file with timestamp: " + name)
    return I1, Q1, t1, I2, Q2, t2

#use this after the frequncies scan
#for each frequencies n points are taken, this function returns the points mean 
def get_mean(name):
    I, Q = get_hdf5(name)
    length = check_length(I, Q)
    I_mean, Q_mean = [], []
    for i in range(length):
        I_mean.append(I[i].mean())
        Q_mean.append(Q[i].mean())
    return I_mean, Q_mean

#sometimes I and Q are not of the same length
def check_length(I, Q):
    length = len(I) if len(I) <= len(Q) else len(Q)
    if len(I) != len(Q):
        logger.debug('Lengths of I and Q are different! I = %d, Q = %d' %(len(I),len(Q)))
        print('Lengths of I and Q are different! I = %d, Q = %d' %(len(I),len(Q)))
    return length

#only to set start and end of the arrays
def set_begin_end(begin, end, length):
    begin = 0   if begin==-1 else begin
    end   = length if end==-1   else end
    return begin, end

#when multiple records are taken use this function to plot one of them, chosen with the index i
def plot_hdf5(name, i = 0, begin=-1, end=-1, save = False):
    with h5py.File(name, 'r') as hdf:
        I = np.array(hdf['i_signal'])[i]
        Q = np.array(hdf['q_signal'])[i]
        
        length = check_length(I, Q)

        x = np.linspace(0,length,length)

        begin, end = set_begin_end(begin, end, length)
        
        fig, axs = plt.subplots(1, 2, figsize=(12, 5))
        fig.suptitle(str(name))
        axs[0].scatter(x[begin:end], I[begin:end], marker='.')
        axs[0].set_title("I")
        #axs[0].set_xlabel('t')
        #axs[0].set_ylabel("I")
        axs[1].scatter(x[begin:end], Q[begin:end], marker='.')
        axs[1].set_title("Q")
        #axs[1].set_xlabel('t')
        #axs[1].set_ylabel("Q")
        fig.tight_layout()
        fig.patch.set_facecolor('white')
        if save:
            fig.savefig('../plot/' + str(name) + '.png', dpi=300)                
    return None

#given two arrays it returns the point where they both vary as much as possible
def der_IQ(x, I, Q, begin=-1, end=-1, plot = False):
    length = check_length(I, Q)
    begin, end = set_begin_end(begin, end, length)
    
    der_i = np.diff(I[begin:end])
    der_q = np.diff(Q[begin:end])
    tot = der_i + der_q
    if plot:
        plt.plot(x[begin:(end-1)], tot)
    if -tot.min() > tot.max():
        print('Point found during the falling at position %d with a frequency of %.5f.' %(begin + np.argmin(tot), x[begin + np.argmin(tot)])) # For the max in falling
        return begin + np.argmin(tot)
    else:
        print('Point found during the rising at position %d with a frequency of %.5f.' %(begin + np.argmax(tot), x[begin + np.argmax(tot)])) # For the max in rising
        return begin + np.argmax(tot)

def plot_all_from_array(i1, q1, i2, q2, freq, step, begin = -1, end = -1, name = 'test', save = False):
    begin, end = set_begin_end(begin, end, len(i1))
    big_plot_from_array(i1, q1, freq[0], step, begin, end, name = 'test1', save = False)
    big_plot_from_array(i2, q2, freq[1], step, begin, end, name = 'test2', save = False)
    return

#plot of I, Q, IQ, module from the arrays of I and Q
def big_plot_from_array(I, Q, ref, step, begin = -1, end = -1, name = 'test', save = False):
    length = check_length(I, Q)
    begin, end = set_begin_end(begin, end, length)
    x = []
    for i in range(-length//2, length//2): 
        x.append(ref + i*step)
    fig, axs = plt.subplots(2, 2, figsize=(10, 8))
    #fig.suptitle('Plot of '+ file_name)
    axs[0, 0].scatter(x[begin:end], I[begin:end], marker='.')
    axs[0, 0].set_title("I")
    axs[0, 0].set_xlabel('freq[GHz]')
    axs[0, 0].set_ylabel("I")
    axs[1, 0].scatter(x[begin:end],Q[begin:end], marker='.')
    axs[1, 0].set_title("Q")
    axs[1, 0].set_xlabel('freq[GHz]')
    axs[1, 0].set_ylabel("Q")
    axs[0, 1].scatter(Q[begin:end], I[begin:end], marker='.')
    axs[0, 1].set_title("IQ plane")
    axs[0, 1].set_xlabel('Q')
    axs[0, 1].set_ylabel("I")
    axs[1, 1].scatter(x[begin:end],((np.array(Q)**2+np.array(I)**2)**0.5)[begin:end], marker='.') # Not reliable because I,Q normalization
    axs[1, 1].set_title("sqrt(I^2 + Q^2)") 
    axs[1, 1].set_xlabel('freq[GHz]')
    #axs[0, 0].set_ylabel("AU")
    fig.tight_layout()
    if save:
        fig.patch.set_facecolor('white')
        fig.savefig('../plot/' + name + '.png', dpi=300)
    return None

#plot of I, Q, IQ, module from the hdf5 file
def big_plot_from_file(file, ref, step, record = 0, begin = -1, end = -1, save = False):
    I, Q = get_hdf5(file)
    I = I[record]
    Q = Q[record]
    length = check_length(I, Q)
    begin, end = set_begin_end(begin, end, length)
    x = []
    for i in range(-length//2, length//2): 
        x.append(ref + i*step)
    fig, axs = plt.subplots(2, 2, figsize=(10, 8))
    #fig.suptitle('Plot of '+ file_name)
    axs[0, 0].scatter(x[begin:end], I[begin:end], marker='.')
    axs[0, 0].set_title("I")
    axs[0, 0].set_xlabel('freq[GHz]')
    axs[0, 0].set_ylabel("I")
    axs[1, 0].scatter(x[begin:end],Q[begin:end], marker='.')
    axs[1, 0].set_title("Q")
    axs[1, 0].set_xlabel('freq[GHz]')
    axs[1, 0].set_ylabel("Q")
    axs[0, 1].scatter(Q[begin:end], I[begin:end], marker='.')
    axs[0, 1].set_title("Piano IQ")
    axs[0, 1].set_xlabel('Q')
    axs[0, 1].set_ylabel("I")
    axs[1, 1].scatter(x[begin:end],((np.array(Q)**2+np.array(I)**2)**0.5)[begin:end], marker='.') # Not reliable because I,Q normalization
    axs[1, 1].set_title("sqrt(I^2 + Q^2)")
    axs[1, 1].set_xlabel('freq[GHz]')
    #axs[1, 1].set_ylabel("AU")
    fig.tight_layout()
    if save:
        fig.patch.set_facecolor('white')
        fig.savefig('../plot/' + file + '.png', dpi=300)
    return None

def vertex_parabola(x2, y1, y2, y3):
    x1 = x2 - 1
    x3 = x2 + 1
    b = x3 * x3 * (y2 - y1) + x2 * x2 * (y1 - y3) + x1 * x1 * (y3 - y2)
    a = (y2 - y3) * x1 + (y3 - y1) * x2 + (y1 - y2) * x3

    return -b/(2*a)

def derivative_trigger_matrix(sample, window_ma=20, wl=60, poly=4, n=2, polarity=1, vertex=True):
    logger.debug('Find the critical points where the signal starts in such a way as to align every signal using the Savitzky-Golay filter')
    weights = np.full((1, window_ma), 1/window_ma)
    moving_averages = convolve(sample, weights, mode='mirror')

    index_mins = []

    for i in range(len(sample)):

        first_derivative = np.gradient(moving_averages[i])
        std = np.std(first_derivative[0:100]) #100 will become a function of length and pos_ref in PXIe
        index_min = first_derivative.argmax() if polarity == 1 else first_derivative.argmin()
        
        rise_points = 0

        if polarity == 1:
            while first_derivative[index_min - rise_points] > std:
                rise_points += 1
        else:
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
            min = int(np.round(vertex_parabola(x2, y1, y2, y3)))
        else:
            min = x2

        index_mins.append(min)

    return index_mins

def segmentation_index(sample, window_ma=20, polarity=1, threshold=0, debounce=5):
    logger.debug('Find the indexes in order to segment the continuous acquisition using also a debouncing')
    weights = np.full((1, window_ma), 1/window_ma)
    moving_averages = convolve(sample, weights, mode='mirror')
    first_derivative = np.gradient(moving_averages[0])
    i = 0
    count = 0
    index = []

    if polarity == 1:
        while i < len(first_derivative):

            if first_derivative[i] > threshold:
                count += 1
            else:
                count = 0

            if count == debounce:
                index.append(i)
                count = 0

                while(first_derivative[i] > threshold):
                    i += 1

            i += 1

    else:
        while i < len(first_derivative):
            if first_derivative[i] < threshold:
                count += 1
            else:
                count = 0

            if count == debounce:
                index.append(i)
                count = 0

                while(first_derivative[i] < threshold):
                    i += 1
            i += 1
    return index

def segmentation_iq(i1, q1, i2, q2, index, ref_pos=0.2, length = 2000):
    logger.debug('Segmentation of continuous acquisition for I and Q signals')
    i1_matrix = []
    q1_matrix = []
    i2_matrix = []
    q2_matrix = []

    pre = int(ref_pos*length)
    post = int((1-ref_pos)*length)
    k = 0

    while k < len(index):
        j = index[k]

        i1_matrix.append(i1[j-pre:j+post])
        q1_matrix.append(q1[j-pre:j+post])
        i2_matrix.append(i2[j-pre:j+post])
        q2_matrix.append(q2[j-pre:j+post])

        if (k+1 < len(index)) and ((index[k+1]-j) < 50):
            k += 1
        k += 1

    return i1_matrix, q1_matrix, i2_matrix, q2_matrix

def ellipse_fit(I, Q, plot=False, run = 1):
    X   = np.array(list(zip(I, Q))) 
    #print('X=',X)
    par = LsqEllipse().fit(X)
    center, width, height, phi = par.as_parameters()
    # center = coordinates of ellipse center
    # width  = Total length (diameter) of horizontal axis (a, the largest)
    # height = Total length (diameter) of vertical axis (b, the smallest)
    # angle  = Rotation in degrees anti-clockwise (radians)

    # print(f'center: {center[0]:.3f}, {center[1]:.3f}')
    # print(f'width: {width:.3f}')
    # print(f'height: {height:.3f}')
    # print(f'phi: {phi:.3f}')

    if plot:
        fig = plt.figure(figsize=(6, 6))
        ax  = plt.subplot()
        ax.axis('equal')
        ax.plot(I ,Q, 'ro', zorder=1)
        ellipse = Ellipse(
            xy=center, width=2*width, height=2*height, angle=np.rad2deg(phi), edgecolor='b', fc='None', lw=2, label='Fit', zorder=2
        )
        ax.add_patch(ellipse)

        plt.xlabel('I')
        plt.ylabel('Q')

        plt.legend()
        #plt.savefig('IQfit_ellipse' + str(run) + '.png') 
    
    return center, width, height, phi