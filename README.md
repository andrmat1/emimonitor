# RTL-SDR Based EMI Monitor
Scripts for interfacing with the RTL-SDR to monitor EMI in laboratories. 

Developed by Andrew Mattson in 2022

## takespectra.py
This script is designed to collect data and save it to an HDF5 file. When it is run, it will ask the user for two inputs that form the frequency range the scan will take place in. The function automatically creates an EMI_DATA folder if none is present, and saves spectra into monthly files and daily datasets. Each data file is saved with a time stamp along with a location tag. The sampling rate is set to 2.5 MHz, but this can be customized easily as it is an input argument in the function call. The time_interval parameter is a variable inside of the script, and designates how often the script will run. It will continue this process until it is stopped by the user.
The script contains a function for taking the spectra with the RTL-SDR called "spectra", which switches from direct to indirect sampling at 30 MHz. It then performs a Fast Fourier transform on the data and saves it as two arrays, one for frequency called "freq" and one for power called "pwr". It is set by default to collect a spectra every hour, but this can be changed by editing the "time_interval" variable. 
It also contains a function called "takespectra" designed to facilitate well labeled datasets and files, as well as a function called "nextvals" that helps to iterate through columns in an array when saving data. "takespectra" saves the monthly files by the naming convention year_month_location, with each dataset being named as year_month_day.

### Plots generated
![alt text](https://github.com/andrmat1/emimonitor/blob/main/full%20range%20(1).png)
This plot shows a spectrum taken of the full operating range of this device. It contains an average of 60 hours of data from Phillips 002. 

![alt text](https://github.com/andrmat1/emimonitor/blob/main/low%20freq.png)
This plot shows the weird behavior of the monitor in the low frequency range. There are several spots where a discontinuity appears on the graph, and it is believed to be a result of circuit switching within the RTL-SDR when in direct sampling mode.

## analyze.py
This script analyzes the data collected by the takespectra.py script. It calculates an overall average of the entire spectra, as a baseline measurement. It also finds a rolling average and corresponding rolling standard deviation using a calculated interval. The power value at each point was compared to the rolling average and standard deviation to determine if it was a "spike". These spikes were found with a width of 10 KHz, so if multiple frequencies spiked within this region the script selected the most powerful value and saved it as the spike. The analyze function within this script takes inputs of the low and high frequencies in the range, the frequency and power arrays to be analyzed, and a "spike" parameter that determines how many standard deviations away from the average a value must be to register as a spike. When this function runs, it creates a plot with these averages and spikes plotted. It also returns a list of the spiking frequency regions, as well as how many of them occur in the spectrum that was analyzed.

### Plots Generated from Analyze Function

## binhists.py
This script creates histograms for each frequency bin that a spike occurs. It is a function that takes inputs of the frequency array, a list of spike frequencies, and the power array that is many spectra taken over a period of time. It can both generate histograms where there is a Gaussian distribution with outliers on the far right bins, as well as creating lists of the p value for each spiking frequency bin. 

### Example Histogram

## zoompdf.py
This script generates long PDFs of zoomed in spectra plots, to allow better observation of certain frequency areas or spike shapes. It takes inputs of the spike frequency list, frequency array, average power array (which is an average along axis 0 of the long array of every spectra in the dataset), and a variable called "s_or_a". This variable input is "s" when the long PDF is intended to zoom in on spikes, and "a" when the long PDF is intended to break the entire spectrum into 10 MHz ranges.

### Example Long PDF Generated
