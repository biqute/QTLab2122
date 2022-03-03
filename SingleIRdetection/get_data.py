from instruments import VNA_handler, Fridge_handler
import os
import time
from datetime import date, datetime

today = date.today()
d1 = today.strftime("_%d_%m")
directory = "data"+d1
dir_path=os.path.join(os.path.dirname(os.path.abspath(__file__)),directory)
if not os.path.isdir(dir_path):
    try:
        os.mkdir(directory)
    except:
        pass

VNA_lab=VNA_handler()
Fridge=Fridge_handler()
temps=[]
freqs1=[]
freqs2=[]

r = Fridge.execute("C3")
file_log = open(directory + "\\log.txt", "w")

def log_sensori():
    file_log.write(f"\n{datetime.now():%H:%M:%S}")
    for i in range(0, 36):
        file_log.write(f"\n\tsens({i}): {Fridge.get_T(i)}")

with open('temperatures_gap.txt', encoding='utf-8') as file:
    for line in file:
        line = line.replace('\n', '')
        temps.append(int(line))
    
with open('frequency_ranges_gap_1.txt', encoding='utf-8') as file:
    for line in file:
        line = line.replace('\n', '')
        splitted = [float(x) for x in line.split('\t')]
        freqs1.append(splitted)

with open('frequency_ranges_gap_2.txt', encoding='utf-8') as file:
    for line in file:
        line = line.replace('\n', '')
        splitted = [float(x) for x in line.split('\t')]
        freqs2.append(splitted)




for T in temps:
    try:
        print("Set temp: " + str(T))
        print(f"{datetime.now():%H:%M:%S}\tsens_1:{Fridge.get_T(1)}\tsens_2:{Fridge.get_T(2)}\tsens_3:{Fridge.get_T(3)}\tG1: {Fridge.get_T(14)}\tG2: {Fridge.get_T(15)}")
        log_sensori()
        time.sleep(10)
        Fridge.wait_for_T(T)
        if T >= 200:
            freqs = freqs2
        else:
            freqs = freqs1
        for idx,f in enumerate(freqs):
            file_name=str(T)+'mK_range'+str(idx+1)+'.txt'
            print("Set freqs: " + str(f[0]) + " - "+ str(f[1]))
            VNA_lab.set_sweep_freq(f[0],f[1])
            VNA_lab.inst.write('AVERREST;')
            time.sleep(40)
            VNA_lab.save_sweep_data(directory + '\\' + file_name, 'polar')
    except:
        pass


log_sensori()
Fridge.set_T(0)
log_sensori()

file_log.close()
