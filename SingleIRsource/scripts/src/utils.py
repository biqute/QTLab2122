#useful functions for plot, derivatives...

import h5py
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter
from scipy.ndimage import convolve

#store data in hdf5 file
#first pass the file name, then the name of the dataset and the matrix to store. Repeat the last two steps for each matrix
def storage_hdf5(file, *args):
    with h5py.File(file, 'w') as hdf:
        for i in range(0, len(args), 2):  
            hdf.create_dataset(args[i], data=args[i+1], compression='gzip', compression_opts=9)
            #hdf.create_dataset('q_signal', data=q_matrix, compression='gzip', compression_opts=9)
    return None

#returns two matrices, I and Q
#useful for acquisition, where many records are acquired
def get_hdf5(name): 
    with h5py.File(name, 'r') as hdf:
        I, Q = [], []
        for i in range(len(np.array(hdf['i_signal']))):
            I.append(np.array(hdf['i_signal'])[i])
            Q.append(np.array(hdf['q_signal'])[i])
    return I, Q

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
    weights = np.full((1, window_ma), 1/window_ma)
    moving_averages = convolve(sample, weights, mode='mirror')

    index_mins = []

    for i in range(len(sample)):

        first_derivative = np.gradient(moving_averages[i])
        std = np.std(first_derivative[0:50])/2 #50 will become a function of length and pos_ref in PXIe
        index_min = first_derivative.argmax() if polarity == 1 else first_derivative.argmin()
        
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
            min = int(np.round(vertex_parabola(x2, y1, y2, y3)))
        else:
            min = x2

        index_mins.append(min)

    return index_mins

def segmentation_index(sample, window_ma=20, polarity=1, threshold=0):
    weights = np.full(window_ma, 1/window_ma)
    moving_averages = convolve(sample, weights, mode='mirror')
    first_derivative = np.gradient(moving_averages)
    i = 0
    count = 0
    index = []

    if polarity == 1:
        while i < len(first_derivative):

            if first_derivative[i] > threshold:
                count += 1
            else:
                count = 0

            if count == 4:
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

            if count == 5:
                index.append(i)
                count = 0

                while(first_derivative[i] < threshold):
                    i += 1
            i += 1
    return index

def segmentation_iq(i, q, index, ref_pos=0.3, length=10):
    i_matrix = []
    q_matrix = []

    pre = int(ref_pos*length)
    post = int((1-ref_pos)*length)
    k = 0

    while k < len(index):
        j = index[k]

        i_matrix.append(i[j-pre:j+post])
        q_matrix.append(q[j-pre:j+post])

        if (k+1 < len(index)) and ((index[k+1]-j) < 50):
            k += 1
        k += 1
    

    return i_matrix, q_matrix