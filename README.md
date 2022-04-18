# RTL-SDR Based EMI Monitor
Scripts for interfacing with the RTL-SDR to monitor EMI in laboratories. 

Developed by Andrew Mattson in 2022

## takespectra.py
This script is designed to collect data and save it to an HDF5 file. When it is run, it will ask the user for two inputs that form the frequency range the scan will take place in. The function automatically creates a data file if none is present, and organizes spectra into monthly and daily categories. The sampling rate is set to 2.5 MHz, but this can be customized easily along with the location tag. 
The script contains a function for taking the spectra with the RTL-SDR called "spectra", which switches from direct to indirect sampling at 30 MHz. It then performs a Fast Fourier transform on the data and saves it as two arrays, one for frequency and one for power. It is set by default to collect a spectra every hour, but this can be changed by editing the "time_interval" variable. 
It also contains a function called "takespectra" designed to facilitate well labeled datasets and files, as well as a function called "nextvals" that helps to iterate through columns in an array when saving data. 

### Plots generated
![My animated logo](assets/my-logo.svg)


##
