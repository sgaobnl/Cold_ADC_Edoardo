# -*- coding: utf-8 -*-
"""
Created on Mon Sep  9 11:00:21 2019

@author: Edoardo Lopriore
"""
# This file produces linearity results obtained with a sinewave signal input from Stanford DS360 Low Distortion Generator.
# Input: reference.
# Sinewave cumulative histogram method (first implementation)  ->   J. Doernberg, H.-S. Lee, and D. Hodges, “Full-speed testing of A/D converters”, IEEE Journal of Solid-State Circuits, vol. 19, no. 6, pp. 820–827, 1984.
# Wide documentation about this matter can be found in documents on ADC testing by Analog Devices, Maxim Integrated, Texas Instruments and more.
# Output: DNL & INL plots with maximum and minimum values. Worst DNL and Worst INL are saved in Channel Characterization tables.


import adc_config as config
import numpy as np
import os
import sys
import os.path
import csv
import matplotlib.pyplot as plt
from cmd_library import CMD_ACQ
from stanford_ds360_gen import GEN_CTL
cq = CMD_ACQ()  #command library
gen = GEN_CTL() #signal generator library
plt.rcParams.update({'font.size': 18})

#From ADC configuration file (adc_config.py): temperature and directory name 
env = config.temperature
rawdir = config.subdir

#Input option from batch file: temperature
refs = sys.argv[1]
adc_sample_rate = sys.argv[2]

if(adc_sample_rate == "4"):
    freq = "14404.3"
    fs = 500 #kHz
else:
    #freq = "81054.7"
    #freq = "28320.3"
    freq = "12695.3"
    fs = 2000 #kHz

#50 ohm terminations on socket mezzanine boards
gen_load = "50"  

mode16bit = False
if (mode16bit):
    adc_bits = "ADC16bit"
else:
    adc_bits = "ADC12bit"
    

##### Parameters for DNL/INL calculation #####
Ntot = 2**(22)
amp = "1.3VP"
#if(env=="RT"):
#    amp = "1.4VP"
#else:
#    #IR drop at cold -> use lower swing to avoid overflowing
#    amp = "1.35VP"
#

##### Data Directory #####
lin_dir = rawdir + "Linearity_%sMSPS/"%adc_sample_rate
if (os.path.exists(lin_dir)):
    pass
else:
    try:
        os.makedirs(lin_dir)
    except OSError:
        print ("Error to create folder ")
        sys.exit()


gen.gen_init()
gen.gen_set(wave_type="SINE", freq=freq, amp = amp, dc_oft="0.9", load=gen_load) #sinewave, Hi-Z termination 
#Save Data (>1G of data, comment if not required)
fn = lin_dir + "DNL_INL_sinewave_%s"%refs + ".bin"
print (fn)
chns = cq.get_adcdata(PktNum=Ntot, saveraw=True, fn=fn )

#Use ColdADC as a 12 bit ADC
if(mode16bit == False):    
    chns = list(np.array(chns)//16)

##### DNL and INL Calculation, Sinewave Cumulative Histogram method #####
dnl_all = []
inl_all = []
misscodes = 0
for chnno in range(16):
    chn_data = chns[chnno]
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
    #Misscodes detection(DNL < -1). If DNL > 1, monotonicity is lost, but there are no missing codes.
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
    dnl_all.append(worst_dnl)
    inl_all.append(worst_inl)
    
    #DNL & INL plots
    fig = plt.figure(figsize=(10,8))
    ax1 = plt.subplot2grid((2,2), (0, 0), colspan=2, rowspan=1)
    ax1.x = np.arange(first_bin, last_bin +1)
    ax1_len = len(ax1.x)
    dnl_len = len(dnl)
    tmp_len= min([ax1_len, dnl_len])
    ax1.plot(ax1.x[0: tmp_len],dnl[0: tmp_len])
    ax1.set_xlim([0,4095])
    ax1.set_ylim([-0.8,0.8])
    ax1.set_title('%s Environment. %s Reference. Channel %d'%(env, refs,chnno))
    ax1.set_ylabel('DNL [LSB]')
    ax1.annotate(' max DNL = %0.2f \n min DNL = %0.2f ' %(max_dnl, min_dnl), 
                 xy=(0.65,0.7),xycoords='axes fraction', textcoords='offset points', size=22, bbox=dict(boxstyle="round", fc=(1.0, 1.0, 1.0), ec="none"))
    
    ax2 = plt.subplot2grid((2,2), (1, 0), colspan=2, rowspan=1)
    ax2.x = np.arange(first_bin, last_bin +1)
    ax2_len = len(ax2.x)
    inl_len = len(inl)
    tmp_len= min([ax2_len, inl_len])
    ax2.plot(ax2.x[0:tmp_len], inl[0:tmp_len])
#    ax2.plot(ax2.x,inl)
    ax2.set_xlim([0,4095])
    ax2.set_ylim([-6.5,6.5])
    ax2.set_ylabel('INL [LSB]')
    ax2.annotate(' max INL = %0.2f \n min INL = %0.2f ' %(max_inl, min_inl), 
                 xy=(0.65,0.7),xycoords='axes fraction', textcoords='offset points', size=22, bbox=dict(boxstyle="round", fc=(1.0, 1.0, 1.0), ec="none"))
    
    plt.xlabel('ADC Code')
    
    plt.tight_layout()
    figure_name =  lin_dir + "DNL_INL_%s_%s_ch%d"%(env,refs,chnno) + ".png" 
    print (figure_name)
    plt.savefig(figure_name)
    plt.close()   


#Write misscodes in text log
if(misscodes > 0):
    cq.pass_log('WARNING: Number of misscodes found = %d' %misscodes)    

#Save DNLs and INLs to characterization table
if(refs == "BJT"):
    file_table = rawdir + "Channel_Characterization_BJT_ADC0.csv"
    dnl_adc0 = dnl_all[0:8]
    dnl_adc0.insert(0,"Worst DNL (%s Ms/s)"%adc_sample_rate)      
    inl_adc0 = inl_all[0:8]
    inl_adc0.insert(0,"Worst INL (%s Ms/s)"%adc_sample_rate)     
    with open(file_table, 'a', newline='') as csvfile: 
        csvwriter = csv.writer(csvfile) 
        csvwriter.writerow(dnl_adc0)    
        csvwriter.writerow(inl_adc0) 
    csvfile.close()
    
    file_table = rawdir + "Channel_Characterization_BJT_ADC1.csv"
    dnl_adc1 = dnl_all[8:16]
    dnl_adc1.insert(0,"Worst DNL (%s Ms/s)"%adc_sample_rate)
    inl_adc1 = inl_all[8:16]
    inl_adc1.insert(0,"Worst INL (%s Ms/s)"%adc_sample_rate)             
    with open(file_table, 'a', newline='') as csvfile: 
        csvwriter = csv.writer(csvfile) 
        csvwriter.writerow(dnl_adc1)    
        csvwriter.writerow(inl_adc1)   
    csvfile.close()

if(refs == "CMOS"):
    file_table = rawdir + "Channel_Characterization_CMOS_ADC0.csv"
    dnl_adc0 = dnl_all[0:8]
    dnl_adc0.insert(0,"Worst DNL (%s Ms/s)"%adc_sample_rate)      
    inl_adc0 = inl_all[0:8]
    inl_adc0.insert(0,"Worst INL (%s Ms/s)"%adc_sample_rate)     
    with open(file_table, 'a', newline='') as csvfile: 
        csvwriter = csv.writer(csvfile) 
        csvwriter.writerow(dnl_adc0)    
        csvwriter.writerow(inl_adc0) 
    csvfile.close()
    
    file_table = rawdir + "Channel_Characterization_CMOS_ADC1.csv"
    dnl_adc1 = dnl_all[8:16]
    dnl_adc1.insert(0,"Worst DNL (%s Ms/s)"%adc_sample_rate)
    inl_adc1 = inl_all[8:16]
    inl_adc1.insert(0,"Worst INL (%s Ms/s)"%adc_sample_rate)             
    with open(file_table, 'a', newline='') as csvfile: 
        csvwriter = csv.writer(csvfile) 
        csvwriter.writerow(dnl_adc1)    
        csvwriter.writerow(inl_adc1)   
    csvfile.close()


