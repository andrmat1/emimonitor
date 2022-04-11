from rtlsdr import RtlSdr
import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
from statistics import NormalDist
import scipy.stats as sci
import time
import pandas as pd
import h5py
from matplotlib.backends.backend_pdf import PdfPages

def analyze(low, high, freq, pwr, spike):
    ### IDENTIFYING SPIKES

    # calculate a rolling local average and plot it
    interval = len(pwr) / 1000
    pwrdata = pd.Series(pwr)
    localavgs = pwrdata.rolling(int(np.rint(interval))).mean()
    
    # use the local average and std dev to find spikes
    spikes = []
    localsigma = pwrdata.rolling(int(np.rint(interval))).std()
    
    # Deal with NaN values in rolling average list
    avgsfixed = np.array(localavgs[~np.isnan(localavgs)])
    sigmafixed = np.array(localsigma[~np.isnan(localsigma)])
    Nanvals = len(pwr)-len(avgsfixed)
    freq = np.delete(freq, np.arange(0, Nanvals, 1))
    pwr = np.delete(pwr, np.arange(0, Nanvals, 1))
    plt.plot(freq, avgsfixed)
    
    z = 0
    while z < len(avgsfixed):
        if pwr[z] > avgsfixed[z] + spike * sigmafixed[z]:
            spikes.append(pwr[z])
        z += 1
    
    l = 0
    spike_freqs = []
    while l < len(pwr):
        if pwr[l] in spikes:
            spike_freqs.append(freq[l])
        l += 1
    l = 0
    while l < len(spike_freqs)-1:
        if spike_freqs[l] + 100000 > spike_freqs[l+1]:
            smaller = min(spike_freqs[l],spike_freqs[l+1])
            if smaller == spike_freqs[l]:
                spike_freqs.pop(l)
            if smaller == spike_freqs[l+1]:
                spike_freqs.pop(l+1)
        l += 1
    l = 0
    filtered_spikes = []
    while l < len(freq):
        if freq[l] in spike_freqs:
            filtered_spikes.append(pwr[l])
        l += 1
    print(f"Number of spikes: {len(filtered_spikes)}")
    
    # plot spikes
    plt.scatter(spike_freqs, filtered_spikes, s = 5, color = 'red', zorder = 3)
    
    ### FINDING OVERALL AVERAGE

    avg_pwr = 0
    for i in pwr:
        avg_pwr += i
    avg_pwr = avg_pwr / len(pwr)
    plt.plot(freq, avg_pwr*np.ones(len(pwr)))
    
    # NaN values error
    #print(f"# of Nan values in average list: {Nanvals}")
    
    # explain and graph
    plt.plot(freq,pwr, zorder =0)
    plt.yscale('log')
    plt.xscale('log')
    plt.xlim(freq[0], high)
    plt.legend(['spectrum data', 'rolling average', 'overall average', 'spikes'])
    #plt.savefig("xlog scale new avgs.pdf")
    print(f"OVERALL AVG POWER:             {avg_pwr}")
    print(f"AVERAGE OF THE ROLLING AVERAGE: {np.nansum(localavgs)/len(pwr)}")
    return (avg_pwr, spike_freqs, len(spikes))