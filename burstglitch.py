# %%
import numpy as np
import matplotlib.pyplot as plt
# %matplotlib inline
from lisatools.utils.constants import *
from copy import deepcopy  # can be useful

# %%
import matplotlib as mpl
# Set up plot style for all plots in the notebook
mpl.rcParams.update({'axes.grid' : True,
                     'figure.figsize': [10, 5]})
# mpl.rcParams.items

# %% [markdown]
# ## Define Sine gaussian burst with sky localization parameters

# %%
def SineGaussianBurst(A, f0, phi0, sigma, t0, t, **kwargs):
    """
    A Sine-Gaussian function with 5 parameters.
    
    Inputs:
     - A:     sine amplitude
     - f0:    sine central frequency
     - phi0:  sine intial phase
     - sigma: gaussian width
     - t0:    gaussian central time
     - t:     time

    Return:
     - Sine-Gaussian
    """
    S = A*np.cos(phi0 + 2*np.pi*f0*(t - t0))
    G = np.exp(- (t - t0)**2 / (2*sigma**2))
    
    return S*G


def periodic_SineGaussianBurst(glitch_param_list, t, period):
    """
    Sum multiple Sine-Gaussian functions with 5 parameters.
    Calls the `SineGaussian` function.
    
    Inputs:
     - glitch_param_list: list of glitch parameter lists
     - t:                 time

    Return:
     - Summed Sine-Gaussian
    """
    template = SineGaussianBurst(*glitch_param_list, t)

    reps = t[-1]/period
    print(reps)
    
    for k in range(1,np.int64(reps)):
        # First make sure there are no NaNs in the array!
        template += SineGaussianBurst(*glitch_param_list, t-k*period) + SineGaussianBurst(*glitch_param_list, t+k*period)
    return template

# %%
dt = 0.01

times = np.arange(1000, 12000, dt)

# sgparams = dict(
A = 5e-20
f0 = 1.6
phi0 = np.pi/2
sigma = 0.1
t0 = 10000

lamb = np.pi/2
beta = np.pi/3

period = 20
# )

plt.plot(times, SineGaussianBurst(A, f0, phi0, sigma, t0, times))
# plt.plot(times, periodic_SineGaussianBurst([A, f0, phi0, sigma, t0], times, period), ls='--')
plt.xlim([9990,10010])
plt.show()

# %% [markdown]
# ## Define LISA Response wrapper
# 

# %%
# imports
from fastlisaresponse import ResponseWrapper
from lisatools.detector import EqualArmlengthOrbits

# %%
# if burst_response:
#     del burst_response 

Tobs = 0.0005 # observation time in years
tstart = 5000.0 # start time

# order of the langrangian interpolation
order = 25

# 1st or 2nd or custom (see docs for custom)
tdi_gen = "2nd generation"

tdi_kwargs = dict(
    order=order, tdi=tdi_gen, tdi_chan="XYZ",
)

burst_response = ResponseWrapper(
    waveform_gen = SineGaussianBurst, # it takes a generic waveform generator - can be whatever type of waveform you want
    Tobs = Tobs,
    dt = dt,
    index_lambda = 6,
    index_beta = 7,
    t0 = tstart,
    flip_hx = False,  # set to True if waveform is h+ - ihx
    use_gpu = False,
    remove_sky_coords = True,  # True if the waveform generator does not take sky coordinates
    is_ecliptic_latitude = False,
    remove_garbage= False,  # removes the beginning of the signal that has bad information
    orbits = EqualArmlengthOrbits(),
    **tdi_kwargs
)

# %%
times = np.arange(0, Tobs * YRSID_SI, dt)

times.shape, SineGaussianBurst(A, f0, phi0, sigma, t0, times).shape


# %%

# call response function and generate the TDI response
tdis = burst_response(A, f0, phi0, sigma, tstart+t0, times, lamb, beta)

# %%
tstart/dt

# %%
times, dt

# %%
# plt.plot(times[int(tstart/dt)+1:-int(tstart/dt)], tdis[1])

plt.plot(times[1:], tdis[0])

# plt.ylim([-1,1])
# plt.xlim(7500,7520)
plt.show()
# %%
