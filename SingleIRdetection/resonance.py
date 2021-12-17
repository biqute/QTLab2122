from typing import List

import numpy as np
from matplotlib import pyplot as plt
from iminuit import cost, Minuit

class ResonanceKid():
    """
    Class to automate and simplify the handling of resonance data and fitting.
    Current main functionalities:
        plotting
        fitting
    """

    def __init__(
        self,
        filename: str = None,
        norm: bool = True,
        shift: bool = True,
        init_parameters: List[float] = None
    ):
        self._fit_result = None

        self._norm = norm
        self._shift = shift

        if init_parameters is None:
            init_parameters = [1, 1e-10, 1e-15, 1e-20, 1e3, 1e3, 0.15]

        self.init_parameters = init_parameters

        if filename is not None:
            self._readfile(filename)

    @property
    def norm(self):
        return self._norm

    @property
    def shift(self):
        return self._shift

    @property
    def freqs(self):
        return self._freqs
    @freqs.setter
    def freqs(self, value):
        self._freqs = value

    @property
    def amps(self):
        return self._amps
    @amps.setter
    def amps(self, value):
        self._amps = value

    @property
    def err_amps(self):
        return self._err_amps
    @err_amps.setter
    def err_amps(self, value):
        self._err_amps = value

    @property
    def phases(self):
        return self._phases
    @phases.setter
    def phases(self, value):
        self._phases = value

    @property
    def amp_i(self):
        return self._amp_i
    @amp_i.setter
    def amp_i(self, value):
        self._amp_i = value

    @property
    def amp_q(self):
        return self._amp_q
    @amp_q.setter
    def amp_q(self, value):
        self._amp_q = value

    @property
    def min_freq(self):
        return self._min_freq

    @property
    def amp_max(self):
        return self._amp_max

    @property
    def init_parameters(self):
        return self._init_parameters
    @init_parameters.setter
    def init_parameters(self, value):
        self._init_parameters = value

    @property
    def fit_result(self):
        return self._fit_result
    @fit_result.setter
    def fit_result(self, value):
        self._fit_result = value

    @property
    def _fit_function(self):
        def model(val_x, val_a, val_b, val_c, val_d, val_q, val_qc, val_phi):
            pol = val_a + val_b*val_x + val_c*val_x**2 + val_d*val_x**3
            quad = 1 - (val_q/val_qc)*np.exp(1j*val_phi)/(1-2j*val_q*val_x)

            return pol*abs(quad)
        return model

    @property
    def _cost_func(self):
       return cost.LeastSquares(self.freqs, self.amps, self.err_amps, self._fit_function)

    @property
    def chi2(self):
        if self.fit_result is None:
            print("No fit found: doing it now")
            _ = self.fit()
        return self.fit_result.fval / (len(self.amps) - self.fit_result.npar)

    @property
    def minuit_obj(self):
        return Minuit(self._cost_func, *self.init_parameters)

    def _readfile(self, filename):
        freqs = []
        amp_i = []
        amp_q = []
        amps = []
        phases = []

        with open(filename, encoding='utf-8') as file:
            for line in file:
                splitted = [float(x) for x in line.split('\t')]
                freqs.append(splitted[0])
                amp_i.append(splitted[1])
                amp_q.append(splitted[2])
                amps.append(np.sqrt(splitted[1]**2 + splitted[2]**2))
                phases.append(np.arctan(splitted[1] / splitted[2]))

        self.freqs = np.array(freqs)
        self.amps = np.array(amps)
        self.amp_i = np.array(amp_i)
        self.amp_q = np.array(amp_q)
        self.phases = np.array(phases)

        self._min_freq = self.freqs[np.argmin(self.amps)]
        self._amp_max = self.amps[0]

        self.err_amps = np.array([0.01]*len(self.amps))

        if self.norm:
            self.amps = self.amps / self.amp_max

        if self.shift:
            self.freqs = (self.freqs - self.min_freq)/self.min_freq

    def set_file(self, filename):
        self._readfile(filename)

    def fit(self):
        m_obj = self.minuit_obj
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

    def plot_phase(self):
        plt.scatter(self.freqs, self.phases, s=0.5)
        plt.show()

    def plot_amp(self):
        plt.scatter(self.freqs, self.amps, s=0.5)
        plt.show()

    def plot_amp_i(self):
        plt.scatter(self.freqs, self.amp_i, s=0.5)
        plt.show()

    def plot_amp_q(self):
        plt.scatter(self.freqs, self.amp_q, s=0.5)
        plt.show()
