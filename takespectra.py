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
from bs4 import BeautifulSoup as bs
import copy

# provides coverage from 150 Hz to 1.6 GHz
os.environ['TZ'] = 'EST'
time.tzset()

time_interval = 5 #saving interval (in seconds)
location = '_Room002' #describes situational use
filepath = '/Users/andrew/Desktop/emi website'
if os.path.exists(filepath+'/EMI_DATA') is False:
        os.mkdir(filepath+'/EMI_DATA')

def takespectra(low, high, time_interval):
    a = 0
    counter = 0
    while a < 1:
        ti = time.time()
        year_month = time.strftime('%Y_%m',time.localtime(ti))
        year_month_day = time.strftime('%Y_%m_%d',time.localtime(ti))
        
        spec = spectra(low, high, 2.5e6)
        print(len(spec[1]))
        
        save_index = 0
        if os.path.exists(filepath+'/EMI_DATA/'+year_month+location+'_EMI.h5') is False:
            print('New month file created at \'/EMI_DATA/'+year_month+location+'_EMI.h5\'')
            file = h5py.File(filepath+'/EMI_DATA/'+year_month+location+'_EMI.h5','w')
            file.attrs['time_created'] = ti
            file.attrs['location'] = location
            ffreq = file.create_dataset('Frequency',data=spec[0])

        else:
            file = h5py.File(filepath+'/EMI_DATA/'+year_month+location+'_EMI.h5','r+')

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
            fspec[save_index] = spec[1]
            ftime[save_index] = ti
        file.close()

        tf = time.time()
        timediff = time_interval - (tf - ti)
        counter += 1
        print(counter)
        if counter % 24 == 0:
            ## create and save daily plot
            file2 = h5py.File(filepath+f"/EMI_DATA/{year_month}_Room002_EMI.h5", "r")
            freq = np.array(file2['Frequency'])
            pwr = np.average(np.array(file2[year_month_day]), 0)

            plt.figure()
            plt.plot(freq, pwr)
            plt.xlim(0, freq[-1])
            plt.yscale('log')
            plt.title(f"PSD for {year_month_day}")
            plt.xlabel('Frequency (Hz)')
            plt.ylabel('Relative Power (log scale)')
            plt.savefig(filepath+'/images/spectrumex.png')
            file2.close()

            ## update html file values
            # assign variables
            if counter >= 48:
                print('hi')
                oldavgpwr = avgpwr
                avgpwr = np.average(pwr)
                specdata = np.zeros([2, len(pwr)])
                specdata[0, :] = oldpwr
                specdata[1, :] = pwr
                ksval = kstest(specdata)
                ksval = np.round(ksval, 5)
                print(ksval)
                # update the file
                with open(filepath+'/temp.html') as html:
                    soup = bs(html, 'html.parser')
                    soup_new = copy.copy(soup)
                    text1 = soup_new.ap
                    text2 = soup_new.kv
                    text1.string = str(avgpwr)
                    text2.string = str(ksval)
                with open(filepath+"/index.html", "wb") as file:
                    file.write(soup_new.prettify('utf-8'))
            avgpwr = np.average(pwr)
            oldpwr = pwr
            



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
    directsampling = 'f'
    
    # loop through center freqs, collecting 5 MHz of data at each one
    for i in cfqs:
        # test to make sure still in range
        if i > highfrq:
            return (freqlist, pwrlist)
        # assign center frequency
        sdr.center_freq = i
        if i < 30e6:
            if directsampling == 'f':
                sdr.set_direct_sampling('i')
                directsampling = 't'
        if i >= 30e6:
            if directsampling == 't':
                sdr.set_direct_sampling(0)
                directsampling = 'f'
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

def kstest(specdata):
    speccdfs = np.empty_like(specdata)
    for i in range(len(specdata)):
        spectot = 0 
        for pwrval in specdata[i]:
            spectot += pwrval

        specdatanorm = specdata / spectot

        speccdfs[i] = np.cumsum(specdatanorm[i])
    pval = []
    ksval = []
    for i in range(1, len(speccdfs)):
        temp_ksval, temp_p = sci.ks_2samp(speccdfs[i], speccdfs[i-1], alternative='two-sided')
        pval.append(temp_p)
        ksval.append(temp_ksval)

    return ksval[0]

low = float(input("Low frequency: "))
high = float(input("High frequency: "))
takespectra(low, high, time_interval)
