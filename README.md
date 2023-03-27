# RTL-SDR Based EMI Monitor

Developed by Andrew Mattson in 2022

# Functionality

## Warning!

The device operates the best if it is plugged in and a few scans are taken before actual data taking begins. This is because once the circuit resets from not being plugged in, it must reconfigure to accurately acquire signals. 

## Antenna and Modifications
The device is plugged into a loop antenna that I made out of wires soldered to an SMA connector. A loop antenna was chosen for its precision in certain frequency ranges, and its ability to be fine tuned to look at different areas of the electromagnetic spectrum. This antenna is used for frequencies above the 30 MHz threshold. Below 30 MHz, a modification was performed to the RTL-SDR to increase its accuracy. This modification involved soldering a wire to the input capacitor and the ground plane of the PCB, and then using this as an antenna directly into the environment for the sub-30 MHz range. The device was providing useless non-physical data before the modification. Now, it has been able to consistently measure signals within 0.5 MHz in this range. 

## Device Accuracy

Through testing the device with a signal generator, an uncertainty for the accuracy has been obtained in 3 different operational frequency ranges. The signal generator used did not exceed 100 MHz, so the highest frequencies tested are around there. There are currently 2 working RTL-SDR EMI monitors with the modification performed, and accuracy is reported for both (one device is called "new" and one is called "old"). 

NEW Accuracy:

Low Frequency Range (5-15 MHz): ±0.33 MHz

Mid Frequency Range (~50 MHz): ±0.65 MHz 

High Frequency Range (~100 MHz): ±1.15 MHz


OLD Accuracy: 

Low Frequency Range (5-15 MHz): ±0.38 MHz

Mid Frequency Range (~50 MHz): ±1.75 MHz 

High Frequency Range (~100 MHz): ±1.00 MHz

![alt text](https://github.com/andrmat1/emimonitor/blob/main/6mhz.png)

This plot shows the spike from a signal generator inputting a sine wave at 6 MHz into the device. 
# Scripts

## takespectra.py
This script is designed to collect data and save it to an HDF5 file. When it is run, it will ask the user for two inputs that form the frequency range the scan will take place in. The function automatically creates an EMI_DATA folder if none is present, and saves spectra into monthly files and daily datasets. Each data file is saved with a time stamp along with a location tag. The sampling rate is set to 2.5 MHz, but this can be customized easily as it is an input argument in the function call. The time_interval parameter is a variable inside of the script, and designates how often the script will run. It will continue this process until it is stopped by the user.
The script contains a function for taking the spectra with the RTL-SDR called "spectra", which switches from direct to indirect sampling at 30 MHz. It then performs a Fast Fourier transform on the data and saves it as two arrays, one for frequency called "freq" and one for power called "pwr". It is set by default to collect a spectra every hour, but this can be changed by editing the "time_interval" variable. 
It also contains a function called "takespectra" designed to facilitate well labeled datasets and files, as well as a function called "nextvals" that helps to iterate through columns in an array when saving data. "takespectra" saves the monthly files by the naming convention year_month_location, with each dataset being named as year_month_day.

This script also facilitates the calculation of a few important statistics. A two-way Kolgomorov-Smirnov Test assesses the day to day differences between spectra. Values close to 0 indicate that the daily change between today's spectrum and yesterday's spectrum can most likely be described by expected transient signals. However, values closer to 1 (or anywhere above 0.3) indicate the presence of a larger change between daily spectra, which could suggest something of interest may have happened. Additionally, this script calculates the average power of the day's spectrum, and updates a website with these 2 statistics along with a plot of the spectrum.

### Plots generated
![alt text](https://github.com/andrmat1/emimonitor/blob/main/full%20range%20(1).png)
This plot shows a spectrum taken of the full operating range of this device. It contains an average of 60 hours of data from Phillips 002. 

![alt text](https://github.com/andrmat1/emimonitor/blob/main/direct%20vs%20indirect.png)
This plot shows the takespectra.py script highlighting the much greater sensitivity of the device in direct I/Q sampling mode at frequencies below 30 MHz. 

![alt text](https://github.com/andrmat1/emimonitor/blob/main/lowfreq.png)

This plot shows the behavior of the monitor in the low frequency range. Thanks to the modification discussed above, the RTL-SDR provides useful data in this range. 

## analyze.py
This script analyzes the data collected by the takespectra.py script. It calculates an overall average of the entire spectra, as a baseline measurement. It also finds a rolling average and corresponding rolling standard deviation using a calculated interval. The power value at each point was compared to the rolling average and standard deviation to determine if it was a "spike". These spikes were found with a width of 10 KHz, so if multiple frequencies spiked within this region the script selected the most powerful value and saved it as the spike. The analyze function within this script takes inputs of the low and high frequencies in the range, the frequency and power arrays to be analyzed, and a "spike" parameter that determines how many standard deviations away from the average a value must be to register as a spike. When this function runs, it creates a plot with these averages and spikes plotted. It also returns a list of the spiking frequency regions, as well as how many of them occur in the spectrum that was analyzed.

### Plots Generated from Analyze Function
![alt text](https://github.com/andrmat1/emimonitor/blob/main/analysis.png)
This is a plot generated by the analysis function, where the rolling average and overall average are plotted as lines on the spectrum graph. Additionally, spikes on this graph are defined as greater than 4 standard deviations away from the local average, and plotted as red dots. 

## binhists.py
This script creates histograms for each frequency bin that a spike occurs. It is a function that takes inputs of the frequency array, a list of spike frequencies, and the power array that is many spectra taken over a period of time. These big power arrays can be constructed from the pwr arrays inside of a dataset for a day, or an entire monthly file. It can both generate histograms where there is an obvious Poisson distribution with a few outliers on the far right bins, as well as creating lists of the p value for each spiking frequency bin. It also can return the values of the number of counts in each bin as an array. 

### Example Histogram
![alt text](https://github.com/andrmat1/emimonitor/blob/main/histograms.png)
This is a few histograms that were generated by this function. They all display a Poisson distribution, as expected, but the distributions have radically different widths. Lower frequency histograms tended to have wider distributions. This could be a result of greater antenna sensitivity in these frequency regions. 

![alt text](https://github.com/andrmat1/emimonitor/blob/main/antennas.png)
This shows the much greater antenna sensitivity of the 1 meter antenna in the sub 100 MHz frequency space. 

## zoompdf.py
This script generates long PDFs of zoomed in spectra plots, to allow better observation of certain frequency areas or spike shapes. It takes inputs of the spike frequency list, frequency array, average power array (which is an average along axis 0 of the long array of every spectra in the dataset), and a variable called "s_or_a". This variable input is "s" when the long PDF is intended to zoom in on spikes, and "a" when the long PDF is intended to break the entire spectrum into 10 MHz ranges.

### Example Long PDF Generated
![alt text](https://github.com/andrmat1/emimonitor/blob/main/zoomed.png)
Example of a few of the zoomed in plots. 

![Full Zoomed PDF that Breaks Spectrum into 10 MHz Pieces](https://github.com/andrmat1/emimonitor/blob/main/fullspec_002_10MHz_pieces.pdf)

## Waterfall Plots
Waterfall plots were also made using frequency as the x axis, time as the y axis, and color as the z axis. Color was placed on a log scale. These allow for easy discrimination between time independent and dependent frequencies. They were constructed by using plt.imshow() with the frequency and power arrays. 

![alt text](https://github.com/andrmat1/emimonitor/blob/main/waterfall.png)
