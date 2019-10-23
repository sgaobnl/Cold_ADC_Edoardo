# -*- coding: utf-8 -*-
"""
Created on Mon Sep  9 11:17:56 2019

@author: Edoardo Lopriore
"""
# This file generates FFT and PSD (Power Spectral Density) calculations from sinewave inputs from DS360 Stanford Generator. 
# Input: reference.
# SFDR is calculated by dividing the signal power bins by the highest-amplitude spurious bins.
# SINAD is calculated by dividing the signal power bins by every noise and harmonic distortion bins. 
# ENOB is calculated with correction factor (Vfullscale/Vinput). We cannot use full-range sinewaves because of ColdADC overflowing issue. See MT-003 tutorial by Analog Devices for more information on this.
# Output: PSD plots (relative to full scale) with calculated ENOB, SFDR, SINAD. Values for ENOB are saved in Channel Characterization tables.

import adc_config as config
import numpy as np
import os
import sys
import os.path
import csv
import matplotlib.pyplot as plt
from scipy.fftpack import fft,rfft,ifft,fftn
from cmd_library import CMD_ACQ
from stanford_ds360_gen import GEN_CTL
import pickle
cq = CMD_ACQ()  #command library
gen = GEN_CTL() #signal generator library
plt.rcParams.update({'font.size': 18})

#From ADC configuration file (adc_config.py): temperature and directory name 
env = config.temperature
rawdir = config.subdir

#Input option from batch file: BJT or CMOS reference
refs = sys.argv[1]

#50 ohm terminations on socket mezzanine boards
gen_load = "50"

#Choose between 16 bit or 12 bit ADC
mode16bit = False

    
def chn_rfft_psd(chndata, fs = 2000000.0, fft_s = 2000, avg_cycle = 50):  
    #Averaged RFFT and Power Spectral Density calculations
    ts = 1.0/fs 
    len_chndata = len(chndata)
    avg_cycle_tmp = avg_cycle
    if ( len_chndata >= fft_s * avg_cycle_tmp):
        pass
    else:
        avg_cycle_tmp = (len_chndata//fft_s)

    p = np.array([])
    for i in range(0,avg_cycle_tmp,1):
        x = chndata[i*fft_s:(i+1)*fft_s]
        if ( i == 0 ):
            #FFT computing and normalization
            p = abs(rfft(x)/fft_s)**2     
        else:
            p = p + (abs(rfft(x)/fft_s))**2   
    #PSD calculation
    psd = p / avg_cycle_tmp
    psd = p / ( fs/fft_s)
    psd = p*2
    f = np.linspace(0,fs/2,len(psd))
    psd = 10*np.log10(psd)
    return f,p,psd


##### Parameters for ENOB Calculation #####
Ntot = 2**(11)
avgs = 50
Nsamps = (avgs+2)*Ntot
fs = 500 #kHz

if(refs == "BJT"):
    with open (rawdir + "/ref_set/bjt.bjt", 'rb') as f:
        tmp = pickle.load(f)
else:
    with open (rawdir + "/ref_set/cmos.cmos", 'rb') as f:
        tmp = pickle.load(f)
Vfullscale = tmp[1][3] - tmp[1][4]
#Vfullscale = 1.5 #V
avgs = 10

amp = "1.3VP"
Vinput = 1.3

#if(env=="RT"):
#    amp = "1.4VP"
#    Vinput = 1.4
#else:
#    amp = "1.35VP"
#    Vinput = 1.35


##### Data Directory #####
enob_dir = rawdir + "Dynamic_Behavior/"
if (os.path.exists(enob_dir)):
    pass
else:
    try:
        os.makedirs(enob_dir)
    except OSError:
        print ("Error to create folder ")
        sys.exit()


##### Take Data #####
print ("Enabling ADC External Input...")
cq.Converter_Config(edge_sel = "Normal", out_format = "offset binary", 
                         adc_sync_mode ="Normal", adc_test_input = "Normal", 
                         adc_output_sel = "cali_ADCdata", adc_bias_uA = 50)
gen.gen_init()
gen.gen_set(wave_type="SINE", freq="14404.3", amp=amp, dc_oft="0.9", load=gen_load)  #sinewave, Hi-Z termination

#Save Data (comment if not necesssary)
fn = enob_dir + "ENOB_%s_%s"%(env,refs) + ".bin"
print (fn)
#chns = cq.get_adcdata(PktNum=Ntot, saveraw=True, fn=fn )
chns = cq.get_adcdata(PktNum=Nsamps, saveraw=True, fn=fn )

if(mode16bit == False):
    chns = list(np.array(chns)//16)

##### FFT and PSD #####
enob_all = []
for chnno in range(16):
    fft_data = chns[chnno]
    f, p, psd = chn_rfft_psd(fft_data, fs = fs, fft_s = Ntot, avg_cycle = avgs)
    #Truncate DC and Nyquist bins
    trunc = 20
    p = p[trunc:Ntot-trunc]

    #Span three bins at side of fundamental to calculate signal power
    p_aux = np.copy(p)
    noise = min(p)
    mx_arr = np.where(p_aux == max(p_aux))
    mx = mx_arr[0][0]
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
    ENOB = (SINAD - 1.76 + 20*np.log10(Vfullscale/Vinput)) / 6.02
    
    fundamental = max(p)
    SFDR = 10*np.log10( fundamental / max(p_aux))
    
    if(ENOB < 8):
        cq.pass_log("WARNING: Channel %d ENOB = %0.2f bits \n"%(chnno,ENOB)) 
    
    enob_all.append(ENOB)
    
    ##### Plot normalized power spectral density in dBFS #####
    fig = plt.figure(figsize=(10,8))
    psd = psd[trunc:Ntot-trunc]
    psd_dbfs = psd - max(psd) - 20*np.log10(Vfullscale/Vinput)
    points_dbfs = np.linspace(0,fs/2, len(psd_dbfs))
    plt.plot(points_dbfs, psd_dbfs)
    plt.title('%s Environment. %s Reference. Channel %d'%(env, refs,chnno))
    plt.xlabel('Frequency [kHz]')
    plt.ylabel('Amplitude [dBFS]')
    plt.annotate('SFDR = %0.2f dB \nSINAD = %0.2f dB \nENOB = %0.2f bits' %(np.around(SFDR, decimals=2), np.around(SINAD, decimals=2), np.around(ENOB, decimals = 2)), 
                 xy=(0.6,0.8),xycoords='axes fraction', textcoords='offset points', size=22, bbox=dict(boxstyle="round", fc=(1.0, 1.0, 1.0), ec="none"))
    
    plt.tight_layout()
    figure_name =  enob_dir + "ENOB_%s_%s_ch%d"%(env,refs,chnno) + ".png" 
    print (figure_name)
    plt.savefig(figure_name)
    plt.close()  


#Save ENOBs to characterization table
if(refs == "BJT"):
    file_table = rawdir + "Channel_Characterization_BJT_ADC0.csv"
    enob_adc0 = enob_all[0:8]
    enob_adc0 = [round(x,3) for x in enob_adc0]
    enob_adc0.insert(0,"ENOB")         
    with open(file_table, 'a', newline='') as csvfile: 
        csvwriter = csv.writer(csvfile) 
        csvwriter.writerow(enob_adc0)    
    csvfile.close()
    
    file_table = rawdir + "Channel_Characterization_BJT_ADC1.csv"
    enob_adc1 = enob_all[8:16]
    enob_adc1 = [round(x,3) for x in enob_adc1]
    enob_adc1.insert(0,"ENOB")         
    with open(file_table, 'a', newline='') as csvfile: 
        csvwriter = csv.writer(csvfile) 
        csvwriter.writerow(enob_adc1)    
    csvfile.close()

if(refs == "CMOS"):
    file_table = rawdir + "Channel_Characterization_CMOS_ADC0.csv"
    enob_adc0 = enob_all[0:8]
    enob_adc0 = [round(x,3) for x in enob_adc0]
    enob_adc0.insert(0,"ENOB")         
    with open(file_table, 'a', newline='') as csvfile: 
        csvwriter = csv.writer(csvfile) 
        csvwriter.writerow(enob_adc0)    
    csvfile.close()
    
    file_table = rawdir + "Channel_Characterization_CMOS_ADC1.csv"
    enob_adc1 = enob_all[8:16]
    enob_adc1 = [round(x,3) for x in enob_adc1]
    enob_adc1.insert(0,"ENOB")         
    with open(file_table, 'a', newline='') as csvfile: 
        csvwriter = csv.writer(csvfile) 
        csvwriter.writerow(enob_adc1)    
    csvfile.close()
