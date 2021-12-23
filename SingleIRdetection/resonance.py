import numpy as np
from matplotlib import pyplot as plt
from iminuit import cost, Minuit

from scipy.constants import k, hbar
from scipy.special import kv, iv

class ResonanceKid():
    """
    Class to automate and simplify the handling of resonance data and fitting.
    Current main functionalities:
        plotting
        fitting
    """

    def __init__(
        self,
        filename,
        norm = True,
        shift = True
    ):
        self._fit_result = None

        self._readfile(filename, norm, shift)

        def model(val_x, val_a, val_b, val_c, val_d, val_q, val_qc, val_phi):
            pol = val_a + val_b*val_x + val_c*val_x**2 + val_d*val_x**3
            quad = 1 - (val_q/val_qc)*np.exp(1j*val_phi)/(1-2j*val_q*val_x)

            return pol*abs(quad)
        self._fit_function = model

    @property
    def freqs(self):
        return self._freqs

    @property
    def amps(self):
        return self._amps

    @property
    def err_amps(self):
        return self._err_amps

    @property
    def min_freq(self):
        return self._min_freq

    @property
    def amp_max(self):
        return self._amp_max

    @property
    def chi2(self):
        if self.fit_result is None:
            print("No fit found: doing it now")
            _ = self.fit()
        return self.fit_result.fval / (len(self.amps) - self.fit_result.npar)

    @property
    def fit_result(self):
        return self._fit_result
    @fit_result.setter
    def fit_result(self, value):
        self._fit_result = value


    @property
    def chi2(self):
        if self.fit_result is None:
            print("No fit found: doing it now")
            _ = self.fit()
        return self.fit_result.fval / (len(self.amps) - self.fit_result.npar)

    def _readfile(self, filename, norm, shift):
        freqs = []
        amps = []

        with open(filename, encoding='utf-8') as file:
            for line in file:
                splitted = [float(x) for x in line.split('\t')]
                freqs.append(splitted[0])
                amps.append(np.sqrt(splitted[1]**2 + splitted[2]**2))

        self._min_freq = freqs[amps.index(min(amps))]
        self._amp_max = amps[0]

        err_amps = [0.01]*len(amps)

        self._freqs = np.array(freqs)
        self._amps = np.array(amps)
        self._err_amps = np.array(err_amps)

        if norm:
            self._amps = self.amps / self.amp_max

        if shift:
            self._freqs = (self.freqs - self.min_freq)/self.min_freq

    def fit(self, init_parameters = None):
        if init_parameters is None:
            init_parameters = [1, 1e-10, 1e-15, 1e-20, 1e3, 1e3, 0.15]
        cost_func = cost.LeastSquares(self.freqs, self.amps, self.err_amps, self._fit_function)
        m_obj = Minuit(cost_func, *init_parameters)
        self.fit_result = m_obj
        return m_obj.migrad()

    def plot_fit(self):
        plt.scatter(self.freqs, self.amps, s=0.5)
        if self.fit_result is None:
            print("No fit found: doing it now")
            _ = self.fit()
        plt.plot(self.freqs, self._fit_function(self.freqs, *self.fit_result.values),
                 color='red', label='fit')
        plt.show()

    def plot_amp(self):
        plt.scatter(self.freqs, self.amps, s=0.5)
        plt.show()

class GapFinder():

    def __init__(
        self,
        filename,
        omega = 3.03*1e9,
        inv_q_0 = 4.791014e-5,
        alpha = 0.66
    ):
        self._fit_result = None

        self.omega = omega
        self.inv_q_0 = inv_q_0
        self.alpha = alpha

        self._readfile(filename)

        def model(val_t, delta0):
            val_t = val_t * 1e-3
            omega = self.omega
            xi = hbar * omega / (2 * k * val_t)
            ourk = 1.380649
            sigma1 = 4*np.exp(-delta0/(ourk*val_t))*np.sinh(xi)*kv(0, xi)
            sigma2 = np.pi*(1-2*np.exp(-delta0/(ourk*val_t))*np.exp(-xi)*iv(0,-xi))
            return self.inv_q_0 + (self.alpha/2)*sigma1/sigma2
        self._fit_function = model

    @property
    def omega(self):
        return self._omega
    @omega.setter
    def omega(self, value):
        self._omega = value

    @property
    def inv_q_0(self):
        return self._inv_q_0
    @inv_q_0.setter
    def inv_q_0(self, value):
        self._inv_q_0 = value

    @property
    def alpha(self):
        return self._alpha
    @alpha.setter
    def alpha(self, value):
        self._alpha = value

    @property
    def fit_result(self):
        return self._fit_result
    @fit_result.setter
    def fit_result(self, value):
        self._fit_result = value

    @property
    def temps(self):
        return self._temps
    @property
    def q_inv(self):
        return self._q_inv
    @property
    def err_q_inv(self):
        return self._err_q_inv

    def _readfile(self, filename):
        temps = []
        q_inv = []
        err_q_inv = []

        with open(filename, encoding='utf-8') as file:
            for line in file:
                splitted = [float(x) for x in line.split(' ')]
                temps.append(splitted[0])
                q_inv.append(splitted[1])
                err_q_inv.append(splitted[2])

        self._temps = np.array(temps, dtype='float64')
        self._q_inv = np.array(q_inv, dtype='float64')
        self._err_q_inv = np.array(err_q_inv, dtype='float64')

    def fit(self, init_parameters = None):
        if init_parameters is None:
            init_parameters = [3.5e-23]
        cost_func = cost.LeastSquares(self.temps, self.q_inv, self.err_q_inv, self._fit_function)
        m_obj = Minuit(cost_func, *init_parameters)
        m_obj.limits['delta0'] = (0, None)
        self.fit_result = m_obj
        return m_obj.migrad()

    def plot_fit(self):
        plt.scatter(self.temps, self.q_inv, s=0.8)
        if self.fit_result is None:
            print("No fit found: doing it now")
            _ = self.fit()
        plt.plot(self.temps, self._fit_function(self.temps, *self.fit_result.values),
                 color='red', label='fit')
        plt.show()





