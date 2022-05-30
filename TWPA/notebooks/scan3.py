
def waitUntil(condition):
    wU = True
    while wU == True:
        if condition:
            wU = False
        else
            pause(0.5)
            
def band_info(f, d):
	N = f.size()
	HPV = max(d) - 3 #da capire bene. forse max(smoothing(d))-3? A -3dB cmq la potenza è dimezzata
	for i in range(0,N)
		if d[i] > HPV
			break
	
	for j in range(0,N)
		if d[N-j] > HPV
			break
	
	bw = f[N-j] - f[i]
	gain = mean(d[i:N-j]) #anche qui: d va lisciato?
	return gain, bw, fmin

bias = SIM928('COM28', '4')
pump = SMA100B('TCPIP0::169.254.2.20::inst0::INSTR') #magari cambiare sta roba nella classe dello sma
field_fox = vna('192.168.3.51')

#voltage of the sim
v0 = ..
v1 = ..
dV = ..
N_v = floor((v1-v0)/dv)

#pump power
p0 = ..
pi = ..
dp = ..
N_p = floor((p1-p0)/pv)

#pump frequency
f0 = ..
f1 = ..
df = ..
N_f = floor((f1-f0)/df)

G = np.empty((N_v, N_p, N_f))
bw = np.empty((N_v, N_p, N_f))
start = np.empty((N_v, N_p, N_f))

file = open('scanning.csv', 'w', encoding='utf-8')
file.write('Voltage (V), Pump power (dBm), Pump frequency (Hz), Gain (dB), Bandwidth (Hz), Band start (Hz)')

for i in range(0, N_v):
	bias.set_voltage(v0 + i*dv)
	waitUntil(bias.ask_voltage() == v0 + i*dv)
	for j in range(0, N_p):
	pump.set_ampl(p0 + j*dp)
		for k in range(0, N_f):
			pump.set_freq(f0 + k*df)
			f, d = field_fox.print_data()
			G[i][j][k], bw[i][j][k], start[i][j][k] = band_info(f,d)
			file.write(str(v0 +i*dv) + ',' + str(p0 +j*dp) + ',' + str(f0 +k*df) + ',' + str(G[i][j][k]) + ',' + str(bw[i][j][k]) + ',' str(start[i][j][k]))
file.close()	
	
G_max = amax(G)
G_max_pars = argmax(G)
G_avg = mean(G)
G_std_dev = std(G)

bw_max = amax(bw)
bw_max_pars = argmax(bw)
bw_avg = mean(bw)
bw_std_dev = std(bw)