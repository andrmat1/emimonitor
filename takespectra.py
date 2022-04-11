from rtlsdr import RtlSdr
import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
from statistics import NormalDist
import scipy.stats as sci
import time
import pandas as pd
import h5py
import os

# provides coverage from 150 Hz to 1.6 GHz
os.environ['TZ'] = 'EST'
time.tzset()

time_interval = 60*60 #saving interval (in seconds)
location = '_Room002' #describes situational use

if 'EMI_DATA' not in os.listdir():
        os.mkdir('EMI_DATA')

def takespectra(time_interval):
    a = 0
    while a < 1:
        ti = time.time()
        year_month = time.strftime('%Y_%m',time.localtime(ti))
        year_month_day = time.strftime('%Y_%m_%d',time.localtime(ti))
        
        spec = spectra(150, 1600e6, 2.5e6)
        
        if year_month+location+'_EMI.h5' not in os.listdir('DATA'):
            print('New month file created at \'/Data/'+year_month+location+'_EMI.h5\'')
            file = h5py.File('DATA/'+year_month+location+'_EMI.h5','w')
            file.attrs['time_created'] = ti
            file.attrs['location'] = location
            ffreq = file.create_dataset('Frequency',data=spec[0])
            
        else:
            file = h5py.File('DATA/'+year_month+location+'_EMI.h5','r+')

        if year_month_day not in list(file):
            print('New daily dataset created for ' + year_month_day)
            fspec = file.create_dataset(year_month_day,shape=[int(24*60*60/time_interval),len(spec[1])])
            ftime = file.create_dataset(year_month_day+'_time',shape=[int(24*60*60/time_interval)])
            fspec[0] = spec[1]
            ftime[0] = ti
        else:
            save_index = nextvals(np.array(file[year_month_day]))
        if save_index == 'ERROR: Day Full':
            print(save_index)
        else:
            fspec = file[year_month_day]
            ftime = file[year_month_day+'_time']
            fspec[save_index] = spectra
            ftime[save_index] = t_0
        file.close()
            
        tf = time.time()
        timediff = time_interval - (tf - ti)
        if timediff > 0:
            time.sleep(timediff)
            
def nextvals(array):
    # determine the next index for an empty array in an MxN array. Returns ERROR if data not saved
    # currently no way to extend already created h5py dataset
    for n in range(len(array)):
        if np.all(array[n]==0):
            return(n)
    return('ERROR: Day Full')

def spectra(lowfrq, highfrq, samplerate):
    sdr = RtlSdr()

    # set up master frequency and power lists
    freqlist = []
    pwrlist = []

    # set up list of cfqs
    cfqs = [lowfrq]

    # configure sample rate
    sdr.sample_rate = samplerate # Hz

    # loop through center freqs, collecting 5 MHz of data at each one
    for i in cfqs:
        # test to make sure still in range
        if i > highfrq:
            return (freqlist, pwrlist)
        # assign center frequency
        sdr.center_freq = i
        directsampling = 1
        if i < 30e6:
            if directsampling == 1:
                sdr.set_direct_sampling('i')
        if i >= 30e6:
            if directsampling == 2:
                sdr.set_direct_sampling(0)
        # 256 samples because of welch setting
        sample = sdr.read_samples(256)
        # use welch method to calculate power, outputs numpy arrays
        [freq, pwr] = signal.welch(sample, 5e6)

        # correct frequency by removing first value of 0 and shifting
        shiftedfreq = np.fft.fftshift(freq[0:]) + i
        shiftedpwr = np.fft.fftshift(pwr[0:])

        # remove the drop off on either side
        submask1 = np.arange(0,38,1)
        submask2 = np.arange(218,256,1)

        # remove oddly low points in middle that are because of cfq
        submask3 = np.arange(127,131,1)
        mask1 = np.append(submask1, submask2)
        mask = np.append(mask1, submask3)
        finalfreq = np.delete(shiftedfreq, mask)
        finalpwr = np.delete(shiftedpwr, mask)
        #print(f"beginning freq of cfq {i} = {finalfreq[0]}")

        # create next cfq
        new_cfq = ((finalfreq[len(finalfreq)-1] - i) * 2.012) + i
        #print(f"final freq of cfq {i} = {finalfreq[len(finalfreq)-1]}")
        #print(f"new cfq = {new_cfq}")
        cfqs.append(new_cfq)

        # add frequencies and powers from this iteration to global lists
        freqlist.extend(finalfreq)
        pwrlist.extend(finalpwr)

    sdr.close()
    return (freqlist, pwrlist)

takespectra(time_interval)
