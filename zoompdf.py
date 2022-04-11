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

# zooming in on each smaller region and generating a more detailed plot for each section
def zoom(spikefreqs, freq, avgpwr, filename, s_or_a):
    if s_or_a == 's':
        fig, ax = plt.subplots(len(spikefreqs)+1, 1, figsize=(15,700))
        ax[0].set_yscale('log')
        ax[0].plot(freq, avgpwr)
        i = 1
        ax[i].set_yscale('linear')
        for f in spikefreqs:
            index, = np.where(freq == f)
            index = int(index)
            indexes = np.arange(index-100, index+100, 1)
            zoompwr = []
            zoomfreq = []
            for num in indexes:
                zoompwr.append(avgpwr[num])
                zoomfreq.append(freq[num])
            ax[i].plot(zoomfreq, zoompwr)
            plt.yscale('log')
            ax[i].set_title(f'zoomed-in region of spike at {f/1e6} MHz')
            i += 1
        plt.savefig(filename)
    if s_or_a == 'a':
        freqrange = freq[len(freq)-1] - freq[0]
        numofplots = freqrange / 1e7
        indexes = len(freq) / int(np.ceil(numofplots))
        splitfreq = np.array_split(freq, numofplots)
        splitpwr = np.array_split(avgpwr, numofplots)
        if len(splitfreq) != len(splitpwr):
            print("Error")
            return
        fig, ax = plt.subplots(int(np.ceil(numofplots)+1), 1, figsize=(15,600))
        ax[0].set_yscale('log')
        ax[0].plot(freq, avgpwr)
        i = 1
        ax[i].set_yscale('linear')
        l = 0
        for sf in splitfreq:
            pltfreq = []
            pltpwr = []
            counter = 0
            while counter < int(indexes):
                pltfreq.append(sf[counter])
                pltpwr.append(splitpwr[l][counter])
                counter += 1
            ax[i].plot(pltfreq, pltpwr)
            if sf[0] >= 0:
                ax[i].set_xlim(sf[0], sf[len(sf)-1])
                ax[i].set_title(f'zoomed-in region from {sf[0]/1e6} MHz to {sf[len(sf)-1]/1e6} MHz')
            else:
                ax[i].set_xlim(0, sf[len(sf)-1])
                ax[i].set_title(f'zoomed-in region from 0 MHz to {sf[len(sf)-1]/1e6} MHz')
            i += 1
            l += 1
        plt.savefig(filename)
    return