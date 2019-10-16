# -*- coding: utf-8 -*-
"""
Created on Fri Sep 27 15:36:42 2019

@author: Edoardo Lopriore
"""
# This file outputs full noise, linearity and dynamic behavior results for ADC Test Input measurements.
# Input: references, internal ADC sample rate.
# Output: plots and saved data for RMS noise, DNL and INL, PSD and ENOB.


import adc_config as config
import numpy as np
import os
import sys
import os.path
import csv
from raw_data_decoder import raw_conv
import matplotlib.pyplot as plt
from scipy.fftpack import fft,rfft,ifft,fftn
from scipy.stats import norm
from itertools import chain
from cmd_library import CMD_ACQ
from stanford_ds360_gen import GEN_CTL
import pickle
cq = CMD_ACQ()  #command library
gen = GEN_CTL() #signal generator library

env = config.temperature
rawdir = config.subdir

refs = sys.argv[1]
adc_sample_rate = sys.argv[2]

gen_load = "50"


def chn_rfft_psd(chndata, fs = 2000000.0, fft_s = 2000, avg_cycle = 50):  
    len_chndata = len(chndata)
    avg_cycle_tmp = avg_cycle
    if ( len_chndata >= fft_s * avg_cycle_tmp):
        pass
    else:
        avg_cycle_tmp = (len_chndata//fft_s)

    p = np.array([])
    for i in range(0,avg_cycle_tmp,1):
        x = chndata[i*fft_s:(i+1)*fft_s]
        
#        windowing function
#        x = x*np.kaiser(len(x),14)
#        x = x*np.hamming(len(x))
        
        if ( i == 0 ):
            p = abs(rfft(x)/fft_s)**2# fft computing and normalization
        else:
            p = p + (abs(rfft(x)/fft_s))**2# fft computing and normalization
    psd = p / avg_cycle_tmp
    psd = p / ( fs/fft_s)
    psd = p*2
    f = np.linspace(0,fs/2,len(psd))
    psd = 10*np.log10(psd)
    return f,p,psd


plt.rcParams.update({'font.size': 18})
mode16bit = False
if (mode16bit):
    adc_bits = "ADC16bit"
else:
    adc_bits = "ADC12bit"


##### Sampling frequency initialized: 1 MHz #####
#0x05      ->  FPGA register for system frequency control
#write 1   ->  SHA sampling frequency 500 kHz (4 Ms/s ADC)
#write 0   ->  SHA sampling frequency 2 MHz (nominal, 16 Ms/s ADC)
if(adc_sample_rate == "4"):
    freq = "13671.9"
    dnl_freq = "13672.1"
    fs = 4000 #kHz
else:
    freq = "85937.5"
    dnl_freq = "85937.7"
    #dnl_freq = freq
    #freq = "54688.6"
    #dnl_freq = "54687.5"
    fs = 16000 #kHz



##### Data Directory #####
adc_tst_dir = rawdir + "ADC_TST_IN/"
if (os.path.exists(adc_tst_dir)):
    pass
else:
    try:
        os.makedirs(adc_tst_dir)
    except OSError:
        print ("Error to create folder ")
        sys.exit()
        
adc_tst_dir = adc_tst_dir + "%sMss/"%adc_sample_rate
if (os.path.exists(adc_tst_dir)):
    pass
else:
    try:
        os.makedirs(adc_tst_dir)
    except OSError:
        print ("Error to create folder ")
        sys.exit()


##### Enable ADC Test Input #####
print ("Enabling ADC Test Input...")
cq.Converter_Config(edge_sel = "Normal", out_format = "offset binary", 
                         adc_sync_mode ="Normal", adc_test_input = "ADC_TST_IN", 
                         adc_output_sel = "cali_ADCdata", adc_bias_uA = 50)

Ntot = 2**(22)
amp = "1.3VP"
Vinput = 1.3

#if(env=="RT"):
#    amp = "1.4VP"
#    Vinput = 1.4
#else:
#    amp = "1.35VP"
#    Vinput = 1.35
gen.gen_init()

###############################################################################
######################### DNL/INL Calculation #################################


###### Take Data #####
##### Parameters for DNL/INL calculation #####


#gen.gen_set(wave_type="SINE", freq=dnl_freq, amp = amp, dc_oft="0.45", load=gen_load) #sinewave, 50Ohm termination 
gen.gen_set(wave_type="SINE", freq=dnl_freq, amp = amp, dc_oft="0.90", load=gen_load) #sinewave, 50Ohm termination 

#Save Data (>1G of data, comment if necessary)
fn = adc_tst_dir + "ADC_TST_INPUT_DNLINL_%s_%s"%(env,refs) + ".bin"
print (fn)
chns = cq.get_adcdata(PktNum=Ntot, saveraw=True, fn=fn )

if(mode16bit == False):    
    chns = list(np.array(chns)//16)

#chn_data = []
#for i in range(524288):
#    for j in range(8):
#        chn_data.append(chns[j][i])

##### DNL and INL Calculation, Sinewave Cumulative Histogram method #####
misscodes = 0

chn_data = chns[0][:Ntot]
val, bins = np.histogram(chn_data, bins = 4095, range = (0,4095))
nonzero_bins = np.nonzero(val)
first_bin = nonzero_bins[0][0]
last_bin = nonzero_bins[0][-1]
val_nonzero = val[np.nonzero(val)]
sum_Hk = np.cumsum(val_nonzero)
#Normalized transition voltages
Vj = - np.cos(np.pi*sum_Hk/Ntot)
end = len(Vj)
#Linearized histogram
hlin =  Vj[1:] - Vj[:-1]

#Arbitrary bit truncation (otion 1)
trunc = 30
hlin_trunc = hlin[trunc:-trunc]
first_bin = first_bin + trunc
last_bin = last_bin - trunc

#Fixed bit truncation (option 2)
#trunc_first = 200 - first_bin
#trunc_last = last_bin - 3895
#first_bin = 200
#last_bin = 3895
#hlin_trunc = hlin[trunc_first:-trunc_last]

#LSB calculation as average code width
lsb = np.sum(hlin_trunc) / len(hlin_trunc)
#DNL: concatenate a 0 at the beginning
dnl = np.insert(hlin_trunc/lsb-1, 0, 0.)
#Misscodes detection
miss = np.where(dnl <= -1)
if(np.array(miss).size > 0):
    misscodes += np.array(miss).size  
#INL: cumulative sum of DNL
inl = np.cumsum(dnl)

max_dnl = np.around(max(dnl), decimals=2)
min_dnl = np.around(min(dnl), decimals=2)
max_inl = np.around(max(inl), decimals=2)
min_inl = np.around(min(inl), decimals=2)

#Worst DNL is the maximum of the absolute values
#Worst INL is half the difference between maximum and minimum values (best fit method)
worst_dnl = max(max_dnl, -min_dnl)
worst_inl = np.around(max_inl - min_inl, decimals=2) / 2

#DNL & INL plot
fig = plt.figure(figsize=(10,8))
ax1 = plt.subplot2grid((2,2), (0, 0), colspan=2, rowspan=1)
ax1.x = np.arange(first_bin, last_bin +1)
ax1_len = len(ax1.x)
dnl_len = len(dnl)
tmp_len= min([ax1_len, dnl_len])
ax1.plot(ax1.x[0:tmp_len], dnl[0:tmp_len])
ax1.set_xlim([0,4095])
ax1.set_ylim([-0.8,0.8])
ax1.set_title('%s Environment. %s Reference. ADC Test Input'%(env, refs))
ax1.set_ylabel('DNL [LSB]')
ax1.annotate(' max DNL = %0.2f \n min DNL = %0.2f ' %(max_dnl, min_dnl), 
             xy=(0.65,0.7),xycoords='axes fraction', textcoords='offset points', size=22, bbox=dict(boxstyle="round", fc=(1.0, 1.0, 1.0), ec="none"))

ax2 = plt.subplot2grid((2,2), (1, 0), colspan=2, rowspan=1)
ax2.x = np.arange(first_bin, last_bin +1)

ax2_len = len(ax2.x)
inl_len = len(inl)
tmp_len= min([ax2_len, inl_len])
ax2.plot(ax2.x[0:tmp_len], inl[0:tmp_len])
#ax2.plot(ax2.x,inl)
ax2.set_xlim([0,4095])
ax2.set_ylim([-6.5,6.5])
ax2.set_ylabel('INL [LSB]')
ax2.annotate(' max INL = %0.2f \n min INL = %0.2f ' %(max_inl, min_inl), 
             xy=(0.65,0.7),xycoords='axes fraction', textcoords='offset points', size=22, bbox=dict(boxstyle="round", fc=(1.0, 1.0, 1.0), ec="none"))

plt.xlabel('ADC Code')

plt.tight_layout()
figure_name =  adc_tst_dir + "DNL_INL_%s_%s"%(env,refs) + ".png" 
print (figure_name)
plt.savefig(figure_name)
plt.close()   


###############################################################################
######################### ENOB Calculation ####################################

##### Parameters for ENOB Calculation #####
Ntot = 2**(11)
avgs = 50
Nsamps = 2**(17)

if(refs == "BJT"):
    with open (rawdir + "/ref_set/bjt.bjt", 'rb') as f:
        tmp = pickle.load(f)
else:
    with open (rawdir + "/ref_set/cmos.cmos", 'rb') as f:
        tmp = pickle.load(f)
Vfullscale = tmp[1][3] - tmp[1][4]

#Vfullscale = 1.5 #V

##### Take Data #####
def p_delete(f, p, psd, fmin=3900, fmax=4100):
    if max(f) < fmin:
        pnew = p
        psdnew = psd
    else:
        if max(f) < fmax :
            fmax = max(f)
        f4min = np.where( (f >= fmin) )[0][0]
        f4max = np.where( (f >= fmax) )[0][0]
        p4m = f4min + np.where( p[f4min:f4max] == max(p[f4min:f4max]) )[0][0]
        pnew = np.append(p[0:p4m], p[p4m-1])
        pnew = np.append(pnew, p[p4m+1:])
        psd4m = f4min + np.where( psd[f4min:f4max] == max(psd[f4min:f4max]) )[0][0]
        psdnew = np.append(psd[0:psd4m], psd[psd4m-1])
        psdnew = np.append(psdnew, psd[psd4m+1:])
    return f, pnew, psdnew

#gen.gen_set(wave_type="SINE", freq=freq, amp=amp, dc_oft="0.45", load=gen_load)  #sinewave, 50 ohm termination, offset half than real (100 ohm term between P and N)
gen.gen_set(wave_type="SINE", freq=freq, amp=amp, dc_oft="0.90", load=gen_load)  #sinewave, 50 ohm termination, offset half than real (100 ohm term between P and N)
new_enob = 0
ENOB = 0
flag = 0
#Select best between ten tries. This is not necessary, results are very similar between each other
while(flag < 10 and ENOB < 10):
    fn = adc_tst_dir + "ADC_TEST_INPUT_ENOB_%s_%s"%(env,refs) + ".bin"
    chns = cq.get_adcdata(PktNum=Nsamps , saveraw=True, fn=fn )
#    chns = cq.get_adcdata(PktNum=Ntot, saveraw=True, fn=fn )
    
    if(mode16bit == False):
        chns = list(np.array(chns)//16)
    
    ##### FFT and PSD Calculation #####
    N_single_chn = int(Nsamps/8)
    fft_data = list(chain.from_iterable(zip(chns[0][:N_single_chn], chns[1][:N_single_chn],chns[2][:N_single_chn],chns[3][:N_single_chn],chns[4][:N_single_chn],chns[5][:N_single_chn],chns[6][:N_single_chn],chns[7][:N_single_chn])))
    
    f, p, psd = chn_rfft_psd(fft_data, fs = fs, fft_s = Ntot, avg_cycle = avgs)
#    f, p, psd = p_delete(f, p, psd, fmin=1950, fmax=2050)
#    f, p, psd = p_delete(f, p, psd, fmin=3950, fmax=4050)
#    f, p, psd = p_delete(f, p, psd, fmin=5950, fmax=6050)

    #Truncate DC and Nyquist bins
    trunc = 5
    p = p[trunc:Ntot-trunc]
       
	#Span three bins at side of fundamental to calculate signal power
    p_aux = np.copy(p)
    noise = min(p)
    mx_arr = np.where(p_aux == max(p_aux))
    mx = mx_arr[0]
    signal_pwr = max(p_aux)
    span = 3
    p_aux[mx] = noise
    for k in range(1, span+1):
        signal_pwr = signal_pwr + p[mx+k] + p[mx-k]
        p_aux[mx+k] = noise
        p_aux[mx-k] = noise

    
    ##### Extract parameters of interest #####
    NAD = np.sum(p) - signal_pwr
    SINAD = 10*np.log10( signal_pwr / NAD )
    new_enob = (SINAD - 1.76 + 20*np.log10(Vfullscale/Vinput)) / 6.02
    
    fundamental = max(p)
    SFDR = 10*np.log10( fundamental / max(p_aux))
    
    if(new_enob > ENOB):
        ENOB = new_enob
        good_chns = chns
        
    flag += 1
    print(flag)

##### Plot normalized power spectral density in dBFS #####
fig = plt.figure(figsize=(10,8))
psd = psd[trunc:Ntot-trunc]
psd_dbfs = psd - max(psd) - 20*np.log10(Vfullscale/Vinput)
points_dbfs = np.linspace(0,fs/2, len(psd_dbfs))
plt.plot(points_dbfs, psd_dbfs)
plt.title('%s Environment. %s Reference. ADC Test Input'%(env, refs))
plt.xlabel('Frequency [kHz]')
plt.ylabel('Power Density Amplitude [dBFS]')
plt.annotate('SFDR = %0.2f dB \nSINAD = %0.2f dB \nENOB = %0.2f bits' %(np.around(SFDR, decimals=2), np.around(SINAD, decimals=2), np.around(ENOB, decimals = 2)), 
             xy=(0.6,0.8),xycoords='axes fraction', textcoords='offset points', size=22, bbox=dict(boxstyle="round", fc=(1.0, 1.0, 1.0), ec="none"))

plt.tight_layout()
figure_name =  adc_tst_dir + "ENOB_%s_%s"%(env,refs) + ".png" 
print (figure_name)
plt.savefig(figure_name)
plt.close()


###############################################################################
############################# Noise Study #####################################
Ntot = 60000

#Reminder: due to our termination, real offset is double the set one
#Baseline 900 mV
baseline = "900"
#gen.gen_set(wave_type="WHITE", freq ="0", amp="0VP", dc_oft="0.45", load=gen_load)
gen.gen_set(wave_type="WHITE", freq ="0", amp="0VP", dc_oft="0.90", load=gen_load)

#chns = cq.get_adcdata(PktNum=Ntot )
fn = adc_tst_dir + "ADC_TST_INPUT_WHITE_%s_%s"%(env,refs) + ".bin"
chns = cq.get_adcdata(PktNum=Ntot, saveraw=True, fn=fn )

if (mode16bit):
    data_slice = np.array(chns[0][0:10000])&0xffff
else:
    data_slice = (np.array(chns[0][0:10000])&0xffff)//16
    
N = len(data_slice)
rms900 = np.std(data_slice)
ped = np.mean(data_slice)
sigma3 = int(rms900+1)*3

fig = plt.figure(figsize=(12,8))
plt.hist(data_slice, density=1, bins=sigma3*2, range=(ped-sigma3, ped+sigma3),  histtype='bar', label="RMS: %.3f"%(rms900), rwidth=0.9 )
gaussian_x = np.linspace(ped - 3*rms900, ped + 3*rms900, 100)
gaussian_y = norm.pdf(gaussian_x, ped, rms900)
plt.plot(gaussian_x, gaussian_y, color='r')

plt.title('%s Environment. %s Reference. %s mV Baseline. ADC Test Input'%(env, refs, baseline))
plt.xlabel('Normalized Counts')
plt.ylabel('ADC Output / LSB')
plt.legend(loc="upper right", fontsize = 22)
plt.savefig(adc_tst_dir + "Hist_NoiseTest_%s_%s_%s"%(env,refs,baseline) + ".png" )
plt.close()



###############################################################################
######################### ADC Test Input Table ################################

fields = ['Quantity', 'Value']
dnl_table = []
inl_table = []
enob_table = []
noise_table = []

if(refs == "BJT"):
    file_table = adc_tst_dir + "Channel_Characterization_BJT.csv"
    dnl_table.append(dnl)
    inl_table.append(inl)
    enob_table.append(ENOB)
    noise_table.append(rms900)
    dnl_table.insert(0,"Worst DNL")      
    inl_table.insert(0,"Worst INL")     
    enob_table.insert(0,"ENOB")  
    noise_table.insert(0,"Noise (900)") 
    with open(file_table, 'w', newline='') as csvfile: 
        csvwriter = csv.writer(csvfile) 
        csvwriter.writerow(fields)    
        csvwriter.writerow(dnl_table)
        csvwriter.writerow(inl_table)
        csvwriter.writerow(enob_table)
        csvwriter.writerow(noise_table)
    csvfile.close()
    

if(refs == "CMOS"):
    file_table = adc_tst_dir + "Channel_Characterization_CMOS.csv"
    dnl_table.append(dnl)
    inl_table.append(inl)
    enob_table.append(ENOB)
    noise_table.append(rms900)
    dnl_table.insert(0,"Worst DNL")      
    inl_table.insert(0,"Worst INL")     
    enob_table.insert(0,"ENOB")  
    noise_table.insert(0,"Noise (900)") 
    with open(file_table, 'w', newline='') as csvfile: 
        csvwriter = csv.writer(csvfile) 
        csvwriter.writerow(fields)    
        csvwriter.writerow(dnl_table)
        csvwriter.writerow(inl_table)
        csvwriter.writerow(enob_table)
        csvwriter.writerow(noise_table)
    csvfile.close()
