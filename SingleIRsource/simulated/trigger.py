from curses import window
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter
from scipy.ndimage import convolve
from random import randint, uniform

def gen_signal(x=np.linspace(0,1000,1000), baseline=0, amplitude=140, rise_time=40, decay_time=60, pulse_start=200, noise_lev=0.5, plot=False):
    signal = baseline+1*amplitude*(np.exp(-x/rise_time)-np.exp((-x/decay_time)))
    signal = np.interp(x, x+pulse_start, signal)
    noise = np.random.normal(scale=noise_lev, size=len(signal))

    if plot:
        plt.plot(x, signal+noise)
        plt.show()

    return signal+noise

def gen_noise(x=np.linspace(0,1000,1000), noise_lev=0.5):
    return np.random.normal(scale=noise_lev, size=len(x))

def derivative_trigger(sample, window_ma, n=2, plot=False):
    i = 0
    # Initialize an empty list to store moving averages
    weights = np.full(window_ma, 1/window_ma)
    moving_averages = convolve(sample, weights, mode='mirror')

    time = np.linspace(0,len(sample), len(sample))

    # Plot after moving average 
    if plot:
        plt.plot(time, moving_averages)
        print('Sample')
        plt.show()

    first_derivative = np.gradient(moving_averages)
    std = np.std(first_derivative[0:100])/2 #100 will become a function of length and pos_ref in pxie
    index_min = first_derivative.argmin()

    #print('index_min = ', index_min)
    
    rise_points = 0
    while first_derivative[index_min - rise_points] < -std:
        rise_points += 1
    
    #print('rise_points = ', rise_points)
    
    a = 10 #to have a window_length of 21, in this way all the windows are equal
    b = a // 2
    start = index_min - rise_points

    if start < a:
        start = a
    if start > len(sample)-a:
        start = len(sample)-1-a
    
    end = start + a + 1     # +1 to avoid the error: "window_length must be odd."
    begin = start - a if start - a > 0 else 0 # To avoid negative values for begin
    
    #print('hint start = %d, begin = %d, end = %d' %(start, begin, end))
    
    window_length = len(sample[begin:end]) #-1 if len(sample[begin:end]) % 2 == 0 else len(sample[begin:end])

    #print(window_length)

    #poly_order = window_length-1 if window_length < 14 else 12
    
    derivative_func = savgol_filter(sample[begin:end], window_length, 8, n, delta=1) #8 is the best in the tests done

    # we have to drop the first b points and the last b points of the array
    # since sth strange happens here with the derivative due to the polinomial fitting of sav_gol
    time = np.linspace(0,len(sample), len(sample))

    if plot:
        plt.scatter(time[begin:end], savgol_filter(sample[begin:end], window_length, 8, 0, delta=1), color='dodgerblue')
        plt.scatter(time[begin+b:end-b], derivative_func[b:-b], color="g")
        plt.xlabel('Time [$\mu$s]')
        plt.ylabel('Voltage [mV]')
        plt.grid()
        plt.show()

    x2 = begin+b+(derivative_func[b:-b].argmin())
    y1 = derivative_func[b+derivative_func[b:-b].argmin() - 1]
    y2 = derivative_func[b+derivative_func[b:-b].argmin()]
    y3 = derivative_func[b+derivative_func[b:-b].argmin() + 1]
    min = vertex_parabola(x2, y1, y2, y3)
    aa, bb, cc = coeff_parabola(x2, y1, y2, y3)
    if plot:
        t = time[begin:end]
        plt.scatter(t, aa*t*t + bb*t +cc, color='dodgerblue')
        plt.xlabel('Time [$\mu$s]')
        plt.ylabel('Voltage [mV]')
        plt.grid()
        plt.show()
    #min = begin+b+(derivative_func[b:-b].argmin())

    return min, x2#, derivative_func[b+derivative_func[b:-b].argmin()]
    #return print('start: ', time[begin+b+derivative_func[b:-b].argmin()])

def efficiency(index, x=np.linspace(0,1000,1000), pulse_start=200):
    d_max = 0
    d = pulse_start - index

    if d > 0:
        d_max = pulse_start
    else:
        d = -d
        d_max = len(x) - pulse_start

    return d/d_max

#to optimize the performance
def efficiency_matrix(indexes, x=np.linspace(0,1000,1000), pulse_start=200):
    normalized_distances = []

    for index in indexes:
        d_max = 0
        d = pulse_start - index

        if d > 0:
            d_max = pulse_start
        else:
            d = -d
            d_max = len(x) - pulse_start
        normalized_distances.append(d/d_max)

    return normalized_distances

def get_efficiency(eff, n_sample):
    return 1 - sum(eff)/n_sample

def vertex_parabola(x2, y1, y2, y3):
    x1 = x2 - 1
    x3 = x2 + 1
    b = x3 * x3 * (y2 - y1) + x2 * x2 * (y1 - y3) + x1 * x1 * (y3 - y2)
    a = (y2 - y3) * x1 + (y3 - y1) * x2 + (y1 - y2) * x3
    #den = (x1-x2)*(x1-x3)*(x3-x2)
    return -b/(2*a)

def coeff_parabola(x2, y1, y2, y3):
    x1 = x2 - 1
    x3 = x2 + 1
    den = (x1 - x2) * (x1 - x3) * (x3 - x2)
    b = (x3 * x3 * (y2 - y1) + x2 * x2 * (y1 - y3) + x1 * x1 * (y3 - y2)) / den
    a = ((y2 - y3) * x1 + (y3 - y1) * x2 + (y1 - y2) * x3) / den
    c = ((x2 * x3 * y1 * (x3 - x2) + x3 * x1* y2  * (x1 - x3) + x1 * x2 * y3 * (x2 - x1))) / den

    return a, b, c

# Moving average based on cumsum
def moving_average(matrix, window_ma) :
    ret = np.cumsum(matrix, axis=1, dtype=float)
    ret[:, window_ma:] = ret[:, window_ma:] - ret[:, :-window_ma]
    return ret[:, window_ma - 1:]

def derivative_trigger_matrix(sample, window_ma, n=2, mv='convolve', vertex = True, plot=False): #now sample is a matrix of all of the samples
    
    if mv == 'convolve':
        weights = np.full((1, window_ma), 1/window_ma)
        moving_averages = convolve(sample, weights, mode='mirror')

    if mv == 'cumsum':
        moving_averages = moving_average(sample, window_ma)

    index_mins = []
    for ii in range(len(sample)):
        time = np.linspace(0,len(sample[ii]), len(sample[ii]))

        # Plot after moving average 
        if plot:
            plt.plot(time, moving_averages[ii])
            print('Sample: ', ii)
            plt.show()

        first_derivative = np.gradient(moving_averages[ii])
        std = np.std(first_derivative[0:100])/2 #100 will become a function of length and pos_ref in pxie
        index_min = first_derivative.argmin()

        #print('index_min = ', index_min)
        
        rise_points = 0
        while first_derivative[index_min - rise_points] < -std:
            rise_points += 1
        
        #print('rise_points = ', rise_points)

        a = 10 #to have a window_length of 21, in this way all the windows are equal
        b = a // 2
        start = index_min - rise_points

        if start < a:
            start = a
        if start > len(sample[ii])-a:
            start = len(sample[ii])-1-a
        
        end = start + a + 1     # +1 to avoid the error: "window_length must be odd."
        begin = start - a if start - a > 0 else 0 # To avoid negative values for begin
        
        #print('hint start = %d, begin = %d, end = %d' %(start, begin, end))
        
        window_length = len(sample[ii][begin:end]) #-1 if len(sample[begin:end]) % 2 == 0 else len(sample[begin:end])

        #print(window_length)

        #poly_order = window_length-1 if window_length < 14 else 12
        
        derivative_func = savgol_filter(sample[ii][begin:end], window_length, 8, n, delta=1) #8 is the best in the tests done

        '''if plot:
            plt.scatter(time[begin+b:end-b], derivative_func[b:-b], color="g")
            plt.xlabel('Time [$\mu$s]')
            plt.ylabel('Voltage [mV]')
            plt.grid()
            plt.show()'''

        x2 = begin+b+(derivative_func[b:-b].argmin())
        if vertex:
            y1 = derivative_func[b+derivative_func[b:-b].argmin() - 1]
            y2 = derivative_func[b+derivative_func[b:-b].argmin()]
            y3 = derivative_func[b+derivative_func[b:-b].argmin() + 1]
            min = vertex_parabola(x2, y1, y2, y3)
        else:
            min = x2
        #min = begin+b+(derivative_func[b:-b].argmin())
        # we have to drop the first b points and the last b points of the array
        # since sth strange happens here with the derivative due to the polinomial fitting of sav_gol
        index_mins.append(min)

    return index_mins

def good_plot(x, y, title = 'title', x_label = 'x', y_label = 'y', good = False):
    if good:
        fig = plt.figure(dpi = 300)
        fig.patch.set_facecolor('white')       
    plt.plot(x, y)
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.grid()
    plt.show()

def multiple_plots(x, *args, title = 'title', x_label = 'x', y_label = 'y', good = True):
    if good:
        fig = plt.figure(dpi = 300)
        fig.patch.set_facecolor('white')     
    for i in range(0, len(args), 2):  
        plt.plot(x, args[i], label=args[i+1])
    plt.title(title)
    plt.legend()
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.grid()
    plt.show()