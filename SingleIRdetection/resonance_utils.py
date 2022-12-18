from typing import List
import numpy as np
from iminuit import cost, Minuit
from scipy.constants import k, hbar
from scipy.special import kv, iv

from matplotlib import pyplot as plt
import matplotlib
matplotlib.rcParams.update({'font.size': 14})
matplotlib.rcParams['mathtext.fontset'] = 'stix'
matplotlib.rcParams['font.family'] = 'STIXGeneral'

class ResonanceKid():
    """
    Class to automate and simplify the handling of resonance data and fitting.
    Current main functionalities:
        plotting
        fitting
    """
    def __init__(
        self, 
        data = None, 
        polyorder: int = 3, 
        init_parameters: List[float] = None, 
        normalize: bool = True, 
        shift: bool = True, 
        fit_phase: bool = False
    ):
        
        self.polyorder = polyorder
        self.normalize = normalize
        self.shift = shift
        self.fit_phase = fit_phase
        self.fit_result = None
        self.bonus_plot = False

        if init_parameters is not None:
            self.init_parameters = init_parameters
        else:
            self.init_parameters = [1]*(self.polyorder+1)+[1e4, 0.5, 1, 0]
  
        if data is not None:
            if type(data) == str:
                self.readfile(data)
            if type(data) == list or type(data) == np.ndarray:
                self.load_data(data)
            self.estimate_sigma()
        self.residuals = 0
        self.min_obj = self.minuit_obj()


    def readfile(self, filename):
        self.freqs = []
        self.amp_i = []
        self.amp_q = []
        freqs = []
        amp_i = []
        amp_q = []
        with open(filename, encoding = 'utf-8') as file:
            for idx, line in enumerate(file):
                if idx == 0:
                    continue
                line = line.replace(',', '')
                line = line.replace('\n', '')

                splitted = [float(x) for x in line.split('\t')]
                freqs.append(splitted[0])
                amp_i.append(splitted[1])
                amp_q.append(splitted[2])
        self.load_data(np.array([freqs, amp_i, amp_q])) 


    def load_data(self, data): 

        if len(data) != 3:
            raise TypeError('Data must be an array of arrays containing frequencies, I and Q')     

        self.freqs = np.array(data[0])
        self.amp_i = np.array(data[1])
        self.amp_q = np.array(data[2])
        self.amps = np.abs(self.amp_i+1j*self.amp_q)
        self.phases = np.unwrap(np.angle(self.amp_i+1j*self.amp_q))

        self.min_freq = self.freqs[np.argmin(self.amps)]
        self.amp_max = max(self.amps)

        if self.normalize == True:
            self.amps = self.amps / self.amp_max
        elif type(self.normalize) != bool:
            self.amps = self.amps / self.normalize

        self.err_amps = np.array([0.01]*len(self.amps))

        if self.shift:
            self.freqs = (self.freqs - self.min_freq)/self.min_freq
        
        self.mask = np.array([True]*len(self.freqs))

    # Estimate error on data from rms around a polinomial fit of the first tenth of points
    def estimate_sigma(self):
        len_fit = int(np.floor(len(self.amps)/10))
        pol_amp = np.polyfit(self.freqs[:len_fit], self.amps[:len_fit], 2)
        self.amp_rms = np.sqrt(np.mean((np.polyval(pol_amp, self.freqs[:len_fit])-self.amps[:len_fit])**2))        


        len_fit = int(np.floor(len(self.phases)/10))
        pol_ph = np.polyfit(self.freqs[:len_fit], self.phases[:len_fit], 2)
        self.phase_rms = np.sqrt(np.mean((np.polyval(pol_ph, self.freqs[:len_fit])-self.phases[:len_fit])**2))

        if self.bonus_plot == True:
            tol = 5
            plt.figure(figsize = (5.5, 3.5), dpi = 200)
            if self.fit_phase is True:
                textstr = 'RMS = '+str(round(float(self.phase_rms), tol))
                plt.scatter(self.freqs[:len_fit], self.phases[:len_fit], s = 0.5, color = 'purple', label = 'data')
                plt.plot(self.freqs[:len_fit], np.polyval(pol_ph, self.freqs[:len_fit]), color = 'orange', label = 'fit')
            else:
                textstr = 'RMS = '+str(round(float(self.amp_rms), tol))
                plt.scatter(self.freqs[:len_fit], self.amps[:len_fit], s = 0.5, color = 'purple', label = 'data')
                plt.plot(self.freqs[:len_fit], np.polyval(pol_amp, self.freqs[:len_fit]), color = 'orange', label = 'fit')
            plt.ticklabel_format(axis = 'x', style = 'scientific', scilimits = [-1, 2])     
            lgd = plt.legend(loc = 'upper center', bbox_to_anchor = (0.5, 1.3), markerscale = 10)
            plt.xlabel('x', fontsize = 22)
            plt.ylabel('$\\frac{|S_{21}|}{|S_{21}|_{max}}$', fontsize = 22)
            plt.savefig('EstimateRMS.pdf', bbox_extra_artists = (lgd, ), bbox_inches = 'tight')    
        
    def resonance_model(self, x, pars):
        return 1-pars[1]*np.exp(1j*pars[2])/(1+1j*((2*x*pars[0])-pars[3]))

    def model(self, x, pars):
            pol = np.polyval(pars[:self.polyorder+1], x)
            res = self.resonance_model(x, pars[self.polyorder+1:])
            if self.fit_phase is True:
                return np.unwrap(np.angle(res))+pol
            else:
                
                return np.abs(res)+pol

    @property 
    def fit_function(self):  
        return self.model

    @property 
    def LS_cost_function(self):
        if self.fit_phase is True:
            return cost.LeastSquares(self.freqs[self.mask], self.phases[self.mask], self.phase_rms, self.fit_function)
        else:
            return cost.LeastSquares(self.freqs[self.mask], self.amps[self.mask], self.amp_rms, self.fit_function)

    def chi2(self):
        if self.fit_result is None:
            print("No fit found: doing it now")
            self.fit()
        return self.fit_result.fval / (len(self.amps) - self.fit_result.npar)

    @property
    def chi2_function(self):
        return self.chi2_model

    def chi2_model(self, rms):
        if self.fit_phase is True:
             self.phase_rms = rms       
        else:
            self.amp_rms = rms
        self.min_obj = self.minuit_obj()
        self.fit()
        return (1-self.chi2())**2

    def optimize_rms(self):    
        chi_min = Minuit(self.chi2_function, self.amp_rms)
        chi_min.limits[0] = (1e-6, 1)
        self.chi_fit_result = chi_min.scipy()
            
    def minuit_obj(self):
        min_obj = Minuit(self.LS_cost_function, self.init_parameters)
        min_obj.limits[self.polyorder+1] = (1e2, 1e7)
        min_obj.limits[self.polyorder+2] = (1e-6, 1)
        return min_obj

    # Only fit between min and max
    def set_freq_cut(self, min, max):
        self.mask = (min<self.freqs)&(self.freqs<max)

    # Limit the parameters of the fit passing a dictionary. The keys must be the parameter's numbers
    # 0 to polyorder for polynomial, polyorder+1 to polyorder+5 for resonance
    # Set the arguments to 'fix' to keep the parameter fixed, otherwise pass a tuple/list with the limits (min, max) 
    def set_fit_limits(self, dict):
        for key in dict:
            if dict[key] == 'fix':
                self.min_obj.fixed[key] = True
            else:
                self.min_obj.limits[key] = (dict[key][0], dict[key][1])

    # Fit and find 
    def fit(self):
        result = self.min_obj
        self.fit_result = result.migrad(ncall = 10000, iterate = 1000)
        Q = self.fit_result.values[self.polyorder+1]
        R = self.fit_result.values[self.polyorder+2]
        phi = self.fit_result.values[self.polyorder+3]
        invQi = (1-R*(np.cos(phi)))/Q
        invQc = R*(np.cos(phi))/Q

        QErr = self.fit_result.errors[self.polyorder+1]
        RErr = self.fit_result.errors[self.polyorder+2]
        phiErr = self.fit_result.errors[self.polyorder+3]

        QRCov = self.fit_result.covariance[self.polyorder+1, self.polyorder+2]
        QPhiCov = self.fit_result.covariance[self.polyorder+1, self.polyorder+3]
        RPhiCov = self.fit_result.covariance[self.polyorder+2, self.polyorder+3]

        covErrQi = 2*((invQi*np.cos(phi)/(Q**2)*QRCov) - (invQi*R*(np.sin(phi))/(Q**2)*QPhiCov) - (R*np.sin(phi)*np.cos(phi)/(Q**2)*RPhiCov))
        invQiErr = np.sqrt(((invQi*QErr/Q)**2)+((RErr*(np.cos(phi))/Q)**2)+((phiErr*R*(np.sin(phi))/Q)**2)+covErrQi)

        covErrQc = 2*((invQc*np.cos(phi)/(Q**2)*QRCov) - (invQc*R*(np.sin(phi))/(Q**2)*QPhiCov) - (R*np.sin(phi)*np.cos(phi)/(Q**2)*RPhiCov))
        invQcErr = np.sqrt(((invQc*QErr/Q)**2)+((RErr*(np.cos(phi))/Q)**2)+((phiErr*R*(np.sin(phi))/Q)**2)+covErrQc)

        self.invQvalues = [1/Q, invQi, invQc]
        self.invQerrors = [QErr, invQiErr, invQcErr]

        self.Qvalues = [Q, 1/invQi, 1/invQc] 
        self.Qerrors = [QErr, invQiErr/(invQi)**2, invQcErr/(invQc**2)]  
        self.bkg = np.polyval(self.fit_result.values[:self.polyorder+1], self.freqs[self.mask])

    def f0_from_fit(self):
        if self.fit_result is None:
            print("No fit found: doing it now")
            self.fit()      
        self.f0_fit = (self.freqs[np.argmin(np.abs(self.resonance_model(self.freqs, self.fit_result.values[self.polyorder+1:])))]*self.min_freq)+self.min_freq

    # Basic fit plot
    def plot_fit(self):
        plt.figure()
        if self.fit_phase is True:
            plt.scatter(self.freqs, self.phases, s = 0.5)
        else:
            plt.scatter(self.freqs, self.amps, s = 0.5)

        if self.fit_result is None:
            print("No fit found: doing it now")
            self.fit()
        plt.plot(self.freqs[self.mask], self.model(self.freqs[self.mask], self.fit_result.values), color = 'red', label = 'fit')
        plt.show()

    # Better fit plot
    def nice_plot_fit(self):
        plt.figure(figsize = (7, 4), dpi = 200)
        if self.fit_phase is True:
            plt.scatter(self.freqs, self.phases, s = 0.5, color = 'purple', label = 'data')
        else:
            plt.scatter(self.freqs, self.amps, s = 0.5, color = 'purple', label = 'data')

        if self.fit_result is None:
            print("No fit found: doing it now")
            self.fit()
        self.f0_from_fit()

        plt.plot(self.freqs[self.mask], self.model(self.freqs[self.mask], self.fit_result.values), color = 'orange', label = 'fit')
        plt.vlines([(self.f0_fit-self.min_freq)/self.min_freq], ymin = 0.1, ymax = 1.05, color = 'blue', linestyle = 'dashed', alpha = 0.5)

        lgd = plt.legend(loc = 'upper center', bbox_to_anchor = (0.5, 1.3), markerscale = 10)
        plt.xlabel('x', fontsize = 18)
        plt.ylabel('$\\frac{|S_{21}|}{|S_{21}|_{max}}$', fontsize = 18)
        #plt.savefig('ResonanceFit.pdf', bbox_extra_artists = (lgd, ), bbox_inches = 'tight')
        tol = 1
        print(f'* Q = {round(float(self.Qvalues[0]), tol)} ± {round(float(self.Qerrors[0]), tol)}')
        print(f'* Qi = {round(float(self.Qvalues[1]), tol)} ± {round(float(self.Qerrors[1]), tol)}')
        print(f'* Qc = {round(float(self.Qvalues[2]), tol)} ± {round(float(self.Qerrors[2]), tol)}\n')
        print('* fmin = ', round(float(self.min_freq), tol))
        print('* fit_fmin_2 = ', round(float(self.f0_fit), tol))
        print(self.fit_result)

    def plot_residuals(self):
        if self.fit_result is None:
            print("No fit found: doing it now")
            self.fit()
        if self.fit_phase is True:
            self.residuals = (self.phases[self.mask]-self.model(self.freqs[self.mask], self.fit_result.values))/self.phase_rms
        else:
            self.residuals = (self.amps[self.mask]-self.model(self.freqs[self.mask], self.fit_result.values))/self.amp_rms

        left, width = 0.1, 0.65
        bottom, height = 0.1, 1
        left_h = left + width + 0.04

        rect_scatter = [left, bottom, width, height]
        rect_histy = [left_h, bottom, 0.2, height]

        plt.figure(figsize = (9, 2.5), dpi = 200)
        axScatter = plt.axes(rect_scatter)
        axHisty = plt.axes(rect_histy)
        axScatter.set_xlabel('x', fontsize = 14)
        axScatter.set_ylabel('Residuals', fontsize = 14)
        axScatter.plot(self.freqs[self.mask], self.residuals, color = 'purple', alpha = 0.7)
        axScatter.plot(self.freqs[self.mask], [0]*len(self.freqs[self.mask]), color = 'orange', linestyle = 'dashed', marker = '')       
        axScatter.ticklabel_format(axis = 'x', style = 'scientific', scilimits = [-1, 3])     

        bins = 40
        axHisty.hist(self.residuals, bins = bins, color = 'purple', orientation = 'horizontal', alpha = 0.7)
        axHisty.set_ylim(axScatter.get_ylim())
        axHisty.set_xlabel('Counts', fontsize = 14)

        #plt.savefig("Residuals.pdf", bbox_inches = 'tight')

    def fit_wres(self):
        self.init_parameters = np.asarray(self.fit_result.values)
        self.min_obj = self.minuit_obj()
        self.fit()

    def plot_phase(self):
        plt.figure()
        plt.scatter(self.freqs, self.phases, s = 0.5)
        plt.show()

    def plot_amp(self):
        plt.figure()
        plt.scatter(self.freqs, self.amps, s = 0.5)
        plt.show()

    def plot_i(self):
        plt.figure()
        plt.scatter(self.freqs, self.amp_i, s = 0.5)
        plt.show()

    def plot_q(self):
        plt.figure()
        plt.scatter(self.freqs, self.amp_q, s = 0.5)
        plt.show()




class GapFinder():
    """
    Class implementing the fit procedure of quality factor values extracted 
    from resonance data to obtain the energy gap of a superconductor.
    Current main functionalities:
        plotting
        fitting
    """
    def __init__(
        self, 
        filename, 
        omega = 3.03*1e9, 
        inv_q_0 = 4.791014e-5, 
        alpha = 0.86766, # found from Sonnet simulation
        fit_type = "standard"
    ):
        self.fit_result = None

        self.omega = omega
        self.inv_q_0 = inv_q_0
        self.alpha = alpha
        self.set_fit_type(fit_type)
        self._readfile(filename)

    def set_fit_type(self, fit_type):
        self.fit_type = fit_type
        ourk = 1.380649
        if fit_type == 'kondo':        
            def model(val_t, delta0, Tk, b, q0):
                val_t = val_t * 1e-3
                xi = hbar * self.omega / (2 * k * val_t)
                sigma1 = 4*np.exp(-delta0/(ourk*val_t))*np.sinh(xi)*kv(0, xi)
                sigma2 = np.pi*(1-2*np.exp(-delta0/(ourk*val_t))*np.exp(-xi)*iv(0, xi))
                
                return -b*np.log(val_t*1e3/Tk) + 1*self.alpha*sigma1/sigma2 + q0
            
        if fit_type == 'standard':        
            def model(val_t, delta0, q0):
                val_t = val_t * 1e-3
                xi = hbar * self.omega / (2 * k * val_t)
                sigma1 = 4*np.exp(-delta0/(ourk*val_t))*np.sinh(xi)*kv(0, xi)
                sigma2 = np.pi*(1-2*np.exp(-delta0/(ourk*val_t))*np.exp(-xi)*iv(0, xi))
                
                return self.alpha*sigma1/sigma2 + q0
            
        self._fit_function = model
    
    def set_T_limit(self, max):
        self.mask = self._temps<max

    def _readfile(self, filename):
        temps = []
        q_inv = []
        err_q_inv = []

        with open(filename, encoding = 'utf-8') as file:
            for line in file:
                splitted = [float(x) for x in line.split(' ')]
                temps.append(splitted[0])
                q_inv.append(splitted[1])
                err_q_inv.append(splitted[2])

        self._temps = np.array(temps, dtype = 'float64')
        self._q_inv = np.array(q_inv, dtype = 'float64')
        self._err_q_inv = np.array(err_q_inv, dtype = 'float64')
        self.inv_q_0 = self._q_inv[0]

    def fit(self, init_parameters = None):
        if init_parameters is None:
            
            if self.fit_type == 'standard':
                init_parameters = [2, self.inv_q_0]
                
            if self.fit_type == 'kondo':
                init_parameters = [2, 40, 1e-4, self.inv_q_0]
                
        cost_func = cost.LeastSquares(self._temps[self.mask], self._q_inv[self.mask], 
                                      self._err_q_inv[self.mask], self._fit_function)
        m_obj = Minuit(cost_func, *init_parameters)
        m_obj.limits['delta0'] = (0, None)
        m_obj.limits['q0'] = (self.inv_q_0*0.95, self.inv_q_0*1.05)
        #m_obj.fixed['q0'] = True
        
        if self.fit_type == 'kondo':
            m_obj.limits['delta0'] = (0, None)
            m_obj.limits['Tk'] = (0, None)
            m_obj.limits['b'] = (0, None)

        self.fit_result = m_obj
        m_obj.migrad(ncall = 10000, iterate = 20)
        return m_obj

    def chi2(self):
        if self.fit_result is None:
            print("No fit found: doing it now")
            _ = self.fit()
        return self.fit_result.fval / (len(self._temps) - self.fit_result.npar)

    # Basic plot of the data
    def plot(self):
        plt.scatter(self._temps, self._q_inv, s = 0.8)
        plt.show()

    # Fit with chosen model and plot result
    def plot_fit(self):
        plt.figure(dpi = 120)
        plt.errorbar(self._temps, self._q_inv, self._err_q_inv)
        if self.fit_result is None:
            print("No fit found: doing it now")
            _ = self.fit()

        chi = str(round(self.chi2(), 2))
        delta0 = str(round(self.fit_result.values[0] * 6.242e-2, 5)) + " meV"
        textstr = '\n'.join((r'$\tilde{\chi}^2 = $' + chi, r'$\Delta = $'+delta0))
        props = dict(boxstyle = 'round', facecolor = 'white', alpha = 0.9)
        plt.text(50, 6e-4, textstr, fontsize = 14, verticalalignment = 'top',  bbox = props)
        
        plt.plot(self._temps[self.mask], self._fit_function(self._temps[self.mask], 
                *self.fit_result.values), color = 'red', label = 'fit')

        plt.legend(loc = 'upper center', bbox_to_anchor = (0.5, 1.2))
        plt.grid()
        plt.show()
    
    # Nice plot comparing Kondo and standard fit methods
    def plot_fit_compare(self):
        fig = plt.figure(dpi = 150)
        ax = fig.add_subplot(111)
        ax.errorbar(self._temps, self._q_inv, self._err_q_inv, linestyle = ' ', marker = 'o', markersize = 3, label = "Data")

        self.set_fit_type('standard')
        _ = self.fit()
        ax.plot(self._temps[self.mask], self._fit_function(self._temps[self.mask], *self.fit_result.values), 
             color = 'red', linestyle = '--', label = 'Standard fit')
        plt.ylim([self._fit_function(self._temps[self.mask][0], *self.fit_result.values)*0.95, 
                 self._fit_function(self._temps[self.mask], *self.fit_result.values)[-1]])

        self.set_fit_type('kondo')
        _ = self.fit()
        ax.plot(self._temps[self.mask], self._fit_function(self._temps[self.mask], *self.fit_result.values), 
             color = 'red', label = 'Kondo fit')

        plt.xlim([self._temps[self.mask][0], self._temps[self.mask][-1]+10])
        lgd = plt.legend(loc = 'upper center', bbox_to_anchor = (0.5, 1.2), ncol = 3, columnspacing = 0.8)
        plt.grid()
        ax.ticklabel_format(style = 'sci', axis = 'y', scilimits = (0, 0))
        t = ax.yaxis.get_offset_text()
        t.set_x(-0.1)
        plt.xlabel("T (mK)")
        plt.ylabel(r"$1/Q_i$")
       # plt.savefig("Kondo_fit.pdf", bbox_extra_artists = (lgd, ), bbox_inches = 'tight')
        plt.show()