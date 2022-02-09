import visa 
import numpy as np
import serial
import time

print('Bella zi')

class SIM928(object):
	def __init__(self, visa_name, sim900port):
		self.rm = visa.ResourceManager()
		#print(self.rm.list_resources())
		self.pyvisa = self.rm.open_resource(visa_name)
		self.pyvisa.timeout = 10000 # Set response timeout (in milliseconds)
		self.pyvisa.query_delay = 5 # Set extra delay time between write and read commands
		self.sim900port = sim900port
		# Anything else here that needs to happen on initialization
		#self.pyvisa.query('CONN ' + self.sim900port + ',\"we\"')
		
	#comandi fondamentali
	def read(self):
		return self.pyvisa.read()
    
	def write(self, string):
		self.pyvisa.write(string)

	def query(self, string):
		msg = self.pyvisa.query(string)
		print(msg)
		return  msg

	def close(self):
		self.pyvisa.close()
	
	#comandi di interfaccia
	def write_simport(self, message):
		write_str = 'SNDT ' + str(self.sim900port) + ', \"' + message + '\"'
        # print write_str
		self.write(write_str) # Format of 'SNDT 4,\"GAIN 10\"'
		print(write_str)
	def query_simport(self, message):
		write_str = 'CONN ' + str(self.sim900port) + ', \"' + message + '\"'
		return self.query(write_str) # Format of 'SNDT 4,\"GAIN 10\"'
		
	def reset(self):
		self.write_simport('*RST')
	
	#comandi di istruzione	
	def set_voltage(self, voltage=0.0):
       # In a string, %0.4e converts a number to scientific notation
		#self.write_simport('VOLT ' + str(voltage))
		self.write('VOLT ' + str(voltage))
	def set_output(self, output=False):
		if output==True:
			self.write('OPON') 
		else:
			self.write('OPOF')  # Only uses "OPOF" or "OPON": "OPOFF" does not work
	

	
sim = SIM928('COM28', '4')

#sim.query('CONN ' + sim.sim900port)

time.sleep(2)
print('prima')
id=sim.query('*IDN?')
time.sleep(2)

if id == 'Stanford_Research_Systems,SIM900,s/n152741,ver3.6':
	'''sim.query('CONN ' + str(sim.sim900port) + ', \"\"')
	
	time.sleep(2)
	id = sim.query('*IDN?')'''
	print('seconda')
	sim.query_simport('*IDN?')

	time.sleep(2)

	sim.set_voltage(4e-3)

	time.sleep(2)

sim.query('VOLT?')

'''print('seconda')
#sim.query('CONN ' + str(sim.sim900port) + ', \"*IDN?\"')
sim.query_simport('*IDN?')
time.sleep(2)'''


'''print('terza')
sim.query('*IDN?')'''

#sim.query_simport('*IDN?')




