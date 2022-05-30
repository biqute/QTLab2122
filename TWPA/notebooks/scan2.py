def band_info(f, d):
    N = f.size()
    HPV = max(d) - 3 
    for i in range(0,N)
        if d[i] > HPV
            break
    for j in range(0,N)
        if d[N-j] > HPV
            break

    bw = f[N-j] - f[i]
    gain = mean(d[i:N-j])
    return gain, bw, fmin

pump = SMA100B('TCPIP0::169.254.2.20::inst0::INSTR') #magari cambiare sta roba nella classe dello sma
field_fox = vna('192.168.3.51')

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

G = np.empty((N_p, N_f))
bw = np.empty((N_p, N_f))
start = np.empty((N_p, N_f))

file = open('scanning.csv', 'w', encoding='utf-8')
file.write('Pump power (dBm), Pump frequency (Hz), Gain (dB), Bandwidth (Hz), Band start (Hz)')
for j in range(0, N_p):
pump.set_ampl(p0 + j*dp)
    for k in range(0, N_f):
        pump.set_freq(f0 + k*df)
        f, d = field_fox.print_data()
        G[j][k], bw[j][k], start[j][k] = band_info(f,d)
        file.write(str(p0 +j*dp) + ',' + str(f0 +k*df) + ',' + str(G[j][k]) + ',' + str(bw[j][k]) + ',' str(start[j][k]))
file.close()

G_max = amax(G)
G_max_pars = argmax(G)
G_avg = mean(G)
G_std_dev = std(G)

bw_max = amax(bw)
bw_max_pars = argmax(bw)
bw_avg = mean(bw)
bw_std_dev = std(bw)