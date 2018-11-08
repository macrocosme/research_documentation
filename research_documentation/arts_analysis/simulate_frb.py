import random

import numpy as np
import glob
from scipy import signal

import reader
import tools

class Event(object):
    """ Class to generate a realistic fast radio burst and 
    add the event to data, including scintillation, temporal 
    scattering, spectral index variation, and DM smearing. 

    This class was expanded from real-time FRB injection 
    in Kiyoshi Masui's 
    https://github.com/kiyo-masui/burst\_search
    """
    def __init__(self, t_ref, f_ref, dm, fluence, width, 
                 spec_ind, disp_ind=2, scat_factor=0):
        self._t_ref = t_ref
        self._f_ref = f_ref
        self._dm = dm
        self._fluence = fluence 
        self._width = width
        self._spec_ind = spec_ind
        self._disp_ind = disp_ind
        self._scat_factor = min(1, scat_factor + 1e-18) # quick bug fix hack

    def disp_delay(self, f, _dm, _disp_ind=-2.):
        """ Calculate dispersion delay in seconds for 
        frequency,f, in MHz, _dm in pc cm**-3, and 
        a dispersion index, _disp_ind. 
        """
        return 4.148808e3 * _dm * (f**(-_disp_ind))

    def arrival_time(self, f):
        t = self.disp_delay(f, self._dm, self._disp_ind)
        t = t - self.disp_delay(self._f_ref, self._dm, self._disp_ind)
        return self._t_ref + t

    def calc_width(self, dm, freq_c, bw=400.0, NFREQ=1024,
                   ti=0.001, tsamp=0.001, tau=0):
        """ Calculated effective width of pulse 
        including DM smearing, sample time, etc.
        Input/output times are in seconds.
        """

        ti *= 1e3
        tsamp *= 1e3
        delta_freq = bw/NFREQ

        # taudm in milliseconds
        tdm = 8.3e-3 * dm * delta_freq / freq_c**3
        tI = np.sqrt(ti**2 + tsamp**2 + tdm**2 + tau**2)

        return 1e-3*tI

    def dm_smear(self, DM, freq_c, bw=400.0, NFREQ=1024,
                 ti=1, tsamp=0.0016, tau=0):  
        """ Calculate DM smearing SNR reduction
        """
        tau *= 1e3 # make ms
        ti *= 1e3 
        tsamp *= 1e3

        delta_freq = bw / NFREQ

        tI = np.sqrt(ti**2 + tsamp**2 + (8.3 * DM * delta_freq / freq_c**3)**2)

        return (np.sqrt(ti**2 + tau**2) / tI)**0.5

    def scintillation(self, freq):
        """ Include spectral scintillation across 
        the band. Approximate effect as a sinusoid, 
        with a random phase and a random decorrelation 
        bandwidth. 
        """
        # Make location of peaks / troughs random
        scint_phi = np.random.rand()
        f = np.linspace(0, 1, len(freq))

        # Make number of scintils between 0 and 10 (ish)
        nscint = np.exp(np.random.uniform(np.log(1e-3), np.log(7))) 
        #nscint=5
#        envelope = np.cos(nscint*(freq - self._f_ref)/self._f_ref + scint_phi)
        envelope = np.cos(2*np.pi*nscint*f + scint_phi)
        envelope[envelope<0] = 0

        return envelope

    def gaussian_profile(self, nt, width, t0=0.):
        """ Use a normalized Gaussian window for the pulse, 
        rather than a boxcar.
        """
        t = np.linspace(-nt//2, nt//2, nt)
        g = np.exp(-(t-t0)**2 / width**2)

        if not np.all(g > 0):
            g += 1e-18

        g /= g.max()

        return g

    def scat_profile(self, nt, f, tau=1.):
        """ Include exponential scattering profile. 
        """
        tau_nu = tau * (f / self._f_ref)**-4.
        t = np.linspace(0., nt//2, nt)

        prof = 1 / tau_nu * np.exp(-t / tau_nu)
        return prof / prof.max()

    def pulse_profile(self, nt, width, f, tau=100., t0=0.):
        """ Convolve the gaussian and scattering profiles 
        for final pulse shape at each frequency channel.
        """
        gaus_prof = self.gaussian_profile(nt, width, t0=t0)
        scat_prof = self.scat_profile(nt, f, tau) 
#        pulse_prof = np.convolve(gaus_prof, scat_prof, mode='full')[:nt]
        pulse_prof = signal.fftconvolve(gaus_prof, scat_prof)[:nt]
    
        return pulse_prof

    def add_to_data(self, delta_t, freq, data, scintillate=True, bandwidth=300.):
        """ Method to add already-dedispersed pulse 
        to background noise data. Includes frequency-dependent 
        width (smearing, scattering, etc.) and amplitude 
        (scintillation, spectral index). 
        """

        NFREQ = data.shape[0]
        NTIME = data.shape[1]
        tmid = NTIME//2
        freq_mid = freq[len(freq)//2]

        scint_amp = self.scintillation(freq)
        self._fluence /= np.sqrt(NFREQ)
#        stds_perchan = np.std(data)#*np.sqrt(NFREQ)
        SNRTools = tools.SNR_Tools()
        stds_perchan, med = SNRTools.sigma_from_mad(data.flatten())

        for ii, f in enumerate(freq):
            # Do not add FRB to missing channels
            if data[ii].sum()==0:
                continue

            width_ = self.calc_width(self._dm, self._f_ref*1e-3, 
                                     bw=bandwidth, NFREQ=NFREQ,
                                     ti=self._width, tsamp=delta_t, tau=0)

            index_width = max(1, (np.round((width_/ delta_t))).astype(int))
            tpix = int(self.arrival_time(f) / delta_t)

            if abs(tpix) >= tmid:
                # ensure that edges of data are not crossed
                continue

            pp = self.pulse_profile(NTIME, index_width, f, 
                                    tau=self._scat_factor, t0=tpix)

            val = pp.copy()
            val /= val.max()
            val *= self._fluence

#            val *= (100.0 / stds_perchan) # hack
            val /= (width_ / delta_t) 
            val = val * (f / self._f_ref) ** self._spec_ind 

            if scintillate is True:
                val = (0.1 + scint_amp[ii]) * val 
                
            data[ii] += val

#            data[ii, tpix] += 5*np.std(data[ii])
            
            if f == freq_mid:
                width_eff = width_

        np.save('testie', data)

        return width_eff

    def add_to_data_sigmas(self, delta_t, freq, data, snr, 
                    scintillate=True, bandwidth=300.):
        """ Method to add simulated pulse 
        to background noise data for a specific
        S/N.
        """

        NFREQ = data.shape[0]
        NTIME = data.shape[1]
        tmid = NTIME//2

        self._fluence /= np.sqrt(NFREQ)
        stds = np.std(data)

        for ii, f in enumerate(freq):
            # Do not add FRB to missing channels
            if data[ii].sum()==0:
                continue
                
            width_ = self.calc_width(self._dm, self._f_ref*1e-3, 
                                            bw=bandwidth, NFREQ=NFREQ,
                                            ti=self._width, tsamp=delta_t, tau=0)

            index_width = max(1, (np.round((width_/ delta_t))).astype(int))
            tpix = int(self.arrival_time(f) / delta_t)

            snr_per_pix = snr / (np.sqrt(NFREQ*index_width))

            if abs(tpix) >= tmid:
                # ensure that edges of data are not crossed
                continue

            val = snr_per_pix*np.std(data[ii])
            data[ii, tpix] += val

    def dm_transform(self, delta_t, data, freq, maxdm=5.0, NDM=50):
        """ Transform freq/time data to dm/time data.
        """
    
        if len(freq)<3:
            NFREQ = data.shape[0]
            freq = np.linspace(freq[0], freq[1], NFREQ) 

        dm = np.linspace(-maxdm, maxdm, NDM)
        ndm = len(dm)
        ntime = data.shape[-1]

        data_full = np.zeros([ndm, ntime])

        for ii, dm in enumerate(dm):
            for jj, f in enumerate(freq):
                self._dm = dm
                tpix = int(self.arrival_time(f) / delta_t)
                data_rot = np.roll(data[jj], tpix, axis=-1)
                data_full[ii] += data_rot

        return data_full


class EventSimulator():
    """Generates simulated fast radio bursts.
    Events occurrences are drawn from a Poissonian distribution.


    This class was expanded from real-time FRB injection 
    in Kiyoshi Masui's 
    https://github.com/kiyo-masui/burst\_search
    """

    def __init__(self, dm=(0.,2000.), fluence=(0.03,0.3),
                 width=(2*0.0016, 1.), spec_ind=(-4.,4), 
                 disp_ind=2., scat_factor=(0, 0.5), freq=(800., 400.)):
        """
        Parameters
        ----------
        datasource : datasource.DataSource object
            Source of the data, specifying the data rate and band parameters.
        dm : float or pair of floats
            Burst dispersion measure or dispersion measure range (pc cm^-2).
        fluence : float or pair of floats
            Burst fluence (at band centre) or fluence range (s).
        width : float or pair of floats.
            Burst width or width range (s).
        spec_ind : float or pair of floats.
            Burst spectral index or spectral index range.
        disp_ind : float or pair of floats.
            Burst dispersion index or dispersion index range.
        freq : tuple 
            Min and max of frequency range in MHz. Assumes low freq 
            is first freq in array, not necessarily the lowest value. 

        """

        self.width = width
        self.freq_low = freq[0]
        self.freq_up = freq[1]

        if hasattr(dm, '__iter__') and len(dm) == 2:
            self._dm = tuple(dm)
        else:
            self._dm = (float(dm), float(dm))
        if hasattr(fluence, '__iter__') and len(fluence) == 2:
            fluence = (fluence[1]**-1, fluence[0]**-1)
            self._fluence = tuple(fluence)
        else:
            self._fluence = (float(fluence)**-1, float(fluence)**-1)
        if hasattr(width, '__iter__') and len(width) == 2:
            self._width = tuple(width)
        else:
             self._width = (float(width), float(width))
        if hasattr(spec_ind, '__iter__') and len(spec_ind) == 2:
            self._spec_ind = tuple(spec_ind)
        else:
            self._spec_ind = (float(spec_ind), float(spec_ind))
        if hasattr(disp_ind, '__iter__') and len(disp_ind) == 2:
            self._disp_ind = tuple(disp_ind)
        else:
            self._disp_ind = (float(disp_ind), float(disp_ind))
        if hasattr(scat_factor, '__iter__') and len(scat_factor) == 2:
            self._scat_factor = tuple(scat_factor)
        else:
            self._scat_factor = (float(scat_factor), float(scat_factor))

        # self._freq = datasource.freq
        # self._delta_t = datasource.delta_t

        self._freq = np.linspace(self.freq_low, self.freq_up, 256) # tel parameter 

    def draw_event_parameters(self):
        dm = uniform_range(*self._dm)
        fluence = uniform_range(*self._fluence)**(-2/3.)
        # Convert to Jy ms from Jy s
        fluence *= 1e3*self._fluence[0]**(-2/3.)
        spec_ind = uniform_range(*self._spec_ind)
        disp_ind = uniform_range(*self._disp_ind)
        # turn this into a log uniform dist. Note not *that* many 
        # FRBs have been significantly scattered. Should maybe turn this 
        # knob down.
        scat_factor = np.exp(np.random.uniform(*self._scat_factor))
        # change width from uniform to lognormal
        width = np.random.lognormal(np.log(self._width[0]), self._width[1])
        width = np.random.uniform(self._width[0], self._width[1])
        width = max(min(width, 1000*self._width[0]), 0.5*self._width[0])
        return dm, fluence, width, spec_ind, disp_ind, scat_factor

def uniform_range(min_, max_):
    return random.uniform(min_, max_)


def gen_simulated_frb(NFREQ=16, NTIME=250, sim=True, fluence=(0.03,0.3),
                spec_ind=(-4, 4), width=(2*0.0016, 1), dm=(-0.01, 0.01),
                scat_factor=(-3, -0.5), background_noise=None, delta_t=0.0016,
                plot_burst=False, freq=(800, 400), FREQ_REF=600., scintillate=True,
                ):
    """ Simulate fast radio bursts using the EventSimulator class.

    Parameters
    ----------
    NFREQ       : np.int 
        number of frequencies for simulated array
    NTIME       : np.int 
        number of times for simulated array
    sim         : bool 
        whether or not to simulate FRB or just create noise array
    spec_ind    : tuple 
        range of spectral index 
    width       : tuple 
        range of widths in seconds (atm assumed dt=0.0016)
    scat_factor : tuple 
        range of scattering measure (atm arbitrary units)
    background_noise : 
        if None, simulates white noise. Otherwise should be an array (NFREQ, NTIME)
    plot_burst : bool 
        generates a plot of the simulated burst

    Returns
    -------
    data : np.array 
        data array (NFREQ, NTIME)
    parameters : tuple 
        [dm, fluence, width, spec_ind, disp_ind, scat_factor]

    """
    plot_burst = False

    # Hard code incoherent Pathfinder data time resolution
    # Maybe instead this should take a telescope class, which 
    # has all of these things already.
    t_ref = 0. # hack

    if len(freq) < 3:
        freq=np.linspace(freq[0], freq[1], NFREQ)      

    if background_noise is None:
        # Generate background noise with unit variance
        data = np.random.normal(0, 1, NTIME*NFREQ).reshape(NFREQ, NTIME)
    else: 
        data = background_noise

    # What about reading in noisy background?
    if sim is False:
        return data, []

    # Call class using parameter ranges
    ES = EventSimulator(dm=dm, scat_factor=scat_factor, fluence=fluence, 
                        width=width, spec_ind=spec_ind)
    # Realize event parameters for a single FRB
    dm, fluence, width, spec_ind, disp_ind, scat_factor = ES.draw_event_parameters()
    # Create event class with those parameters 
    E = Event(t_ref, FREQ_REF, dm, 10e-4*fluence, 
              width, spec_ind, disp_ind, scat_factor)

    # Add FRB to data array 
    width_eff = E.add_to_data(delta_t, freq, data, scintillate=scintillate)

    if plot_burst:
        subplot(211)
        imshow(data.reshape(-1, NTIME), aspect='auto', 
               interpolation='nearest', vmin=0, vmax=10)
        subplot(313)
        plot(data.reshape(-1, ntime).mean(0))


    return data, [dm, fluence, width_eff, spec_ind, disp_ind, scat_factor]




