from src.FSW_0010   import *
import time 

########## parameters that can be changed
device_address = "COM12"       #location of the synthetizer com12 è synt1
freq           = 5.63          #frequency to set or central frequency of the scan [GHz]
scan           = False         #True = perform a scan over a frequencies interval
                               #False = set the synthetizer on a specific frequency
step           = 0.0002        #step for the frequencies scan [GHz]
num_points     = 100           #number of points for the scan
##########

with FSWSynt(device_address) as test:
    test.turn_on() #test if ok
    time.sleep(0.2)
    #print(test.get_ID())
    if scan:
        for i in range(-num_points//2,num_points//2):
            print(test.set_freq(freq + i*step))
            time.sleep(0.2)
            print('The frequency is: %d \nStep %d of %d' %(test.get_freq(), i, num_points))
            time.sleep(3)
    else:
        print(test.set_freq(freq))
        time.sleep(0.2)
        test.turn_on()
        #print(test.set_power(10))
        time.sleep(0.2)
        print('The frequency is: %f' %test.get_freq())
        time.sleep(0.2)
        #print('The power is: %f' %test.get_power())