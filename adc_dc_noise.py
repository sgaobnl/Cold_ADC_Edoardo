# -*- coding: utf-8 -*-
"""
Created on Wed Sep 11 15:43:23 2019

@author: Edoardo Lopriore
"""
# This file elaborates Noise Studies with histograms of 10000 samples each. 
# Input: reference, baseline (200 or 900).
# RMS Noise is calculated for every channel, with both 200 mV and 900 mV DC (baseline) inputs from the DS360 Stanford Generator (white noise option with amplitude = 0 is the configuration with best noise performance).
# Output: single channel RMS Noise histograms, all-channels comparison plot. RMS values are saved in Channel Characterization tables.


import adc_config as config
import numpy as np
import os
import sys
import os.path
import csv
import matplotlib.pyplot as plt
from scipy.stats import norm
import pickle
from cmd_library import CMD_ACQ
from stanford_ds360_gen import GEN_CTL
cq = CMD_ACQ()  #command library
gen = GEN_CTL() #signal generator library

env = config.temperature
rawdir = config.subdir

refs = sys.argv[1]
baseline = sys.argv[2]
adc_sample_rate = sys.argv[3]

gen_load = "50"

#env = "RT"
#refs = "CMOS"
#baseline = "200"
    
mode16bit = False
if (mode16bit):
    adc_bits = "ADC16bit"
else:
    adc_bits = "ADC12bit"

Ntot = 60000

gen.gen_init()
print(baseline)
if(baseline == "200"):
    gen.gen_set(wave_type="WHITE", freq="0", amp="0VP", dc_oft="0.2", load=gen_load) 
else:
    gen.gen_set(wave_type="WHITE", freq ="0", amp="0VP", dc_oft="0.9", load=gen_load)
    #sinewave, Hi-Z termination

noise_dir = rawdir + "DC_Noise_%sMSPS/"%adc_sample_rate
if (os.path.exists(noise_dir)):
    pass
else:
    try:
        os.makedirs(noise_dir)
    except OSError:
        print ("Error to create folder ")
        sys.exit()

fn = noise_dir + "WHITE_%s_%s"%(env,refs) + ".bin"
print (fn)
chns = cq.get_adcdata(PktNum=Ntot, saveraw=True, fn=fn )
                

single_ch_dir = noise_dir + "Single_Channel/"
if (os.path.exists(single_ch_dir)):
    pass
else:
    try:
        os.makedirs(single_ch_dir)
    except OSError:
        print ("Error to create folder ")
        sys.exit()


rms = []
for chnno in range(16):
    if (mode16bit):
        data_slice = np.array(chns[chnno][0:10000])&0xffff
    else:
        data_slice = (np.array(chns[chnno][0:10000])&0xffff)//16
        
    N = len(data_slice)
    print(data_slice)
    print(N)
    rms.append(np.std(data_slice))
    ped = np.mean(data_slice)
    sigma3 = int(rms[chnno]+1)*3
    
    fig = plt.figure(figsize=(12,5.2))
    plt.hist(data_slice, density=1, bins=sigma3*2, range=(ped-sigma3, ped+sigma3),  histtype='bar', label="CH%d RMS: %.3f"%(chnno, rms[chnno]), rwidth=0.9 )
    gaussian_x = np.linspace(ped - 3*rms[chnno], ped + 3*rms[chnno], 100)
    gaussian_y = norm.pdf(gaussian_x, ped, rms[chnno])
    plt.plot(gaussian_x, gaussian_y, color='r')
    
    plt.title('%s Environment. %s Reference. %s mV Baseline. Channel %d'%(env, refs, baseline,chnno), size = 18)
    plt.ylabel('Normalized Counts', size = 18)
    plt.xlabel('ADC Output / LSB', size = 18)
    plt.legend(loc="upper right", fontsize = 22)
    plt.savefig(single_ch_dir + "Hist_NoiseTest_%s_%s_%s_ch%d"%(env,refs,baseline,chnno) + ".png" )
    plt.close()


#Save RMS Noise to characterization table
if(refs == "BJT"):
    file_table = rawdir + "Channel_Characterization_BJT_ADC0.csv"
    rms_adc0 = rms[0:8]
    rms_adc0 = [round(x,3) for x in rms_adc0] 
    rms_adc0.insert(0,"Noise (%s)"%baseline)         
    # writing to csv file 
    with open(file_table, 'a', newline='') as csvfile: 
        csvwriter = csv.writer(csvfile) 
        csvwriter.writerow(rms_adc0)    
    csvfile.close()
    
    file_table = rawdir + "Channel_Characterization_BJT_ADC1.csv"
    rms_adc1 = rms[8:16]
    rms_adc1 = [round(x,3) for x in rms_adc1]
    rms_adc1.insert(0,"Noise (%s)"%baseline)         
    # writing to csv file 
    with open(file_table, 'a', newline='') as csvfile: 
        csvwriter = csv.writer(csvfile) 
        csvwriter.writerow(rms_adc1)    
    csvfile.close()

if(refs == "CMOS"):
    file_table = rawdir + "Channel_Characterization_CMOS_ADC0.csv"
    rms_adc0 = rms[0:8]
    rms_adc0 = [round(x,3) for x in rms_adc0] 
    rms_adc0.insert(0,"Noise (%s)"%baseline)         
    with open(file_table, 'a', newline='') as csvfile: 
        csvwriter = csv.writer(csvfile) 
        csvwriter.writerow(rms_adc0)    
    csvfile.close()
    
    file_table = rawdir + "Channel_Characterization_CMOS_ADC1.csv"
    rms_adc1 = rms[8:16]
    rms_adc1 = [round(x,3) for x in rms_adc1]
    rms_adc1.insert(0,"Noise (%s)"%baseline)         
    with open(file_table, 'a', newline='') as csvfile: 
        csvwriter = csv.writer(csvfile) 
        csvwriter.writerow(rms_adc1)    
    csvfile.close()


fig = plt.figure(figsize=(12,10))
rms = []
for chnno in range(16):
    if (mode16bit):
        data_slice = np.array(chns[chnno][0:10000])&0xffff
    else:
        data_slice = (np.array(chns[chnno][0:10000])&0xffff)//16
        
    N = len(data_slice)
    print(data_slice)
    print(N)
    rms.append(np.std(data_slice))
    ped = np.mean(data_slice)
    sigma3 = int(rms[chnno]+1)*3
    
    ax = plt.subplot2grid((16, 16), ( (chnno//4)*4, (chnno%4)*4) , colspan=4, rowspan=4)
    ax.hist(data_slice, density=1, bins=sigma3*2, range=(ped-sigma3, ped+sigma3),  histtype='bar', label="CH%d RMS: %.3f"%(chnno, rms[chnno]), rwidth=0.9 )
    gaussian_x = np.linspace(ped - 3*rms[chnno], ped + 3*rms[chnno], 100)
    gaussian_y = norm.pdf(gaussian_x, ped, rms[chnno])
    ax.plot(gaussian_x, gaussian_y, color='r')
    
    ax.grid(True)
    if(chnno == 0 or chnno == 4 or chnno == 8 or chnno == 12):
        ax.set_ylabel("Normalized Counts", size = 14)
    if(chnno == 12 or chnno == 13 or chnno == 14 or chnno == 15):
        ax.set_xlabel("ADC Output / LSB", size = 14)
    ax.legend(loc="lower center", fontsize = 'large')

fig.suptitle("RMS Noise: Histogram with " + "%d samples"%N, size=18)      
fig.tight_layout()
fig.subplots_adjust(top=0.94)
plt.savefig( noise_dir + "Hist_NoiseTest_%s_%s_%s"%(env,refs,baseline) + ".png" )
plt.close()

bad_rms = [x for x in rms if (x>0.9 or x<0.4)]
if not (bad_rms == []):
    for i in range(len(bad_rms)):
        cq.pass_log("WARNING: Channel %d RMS Noise (%f) is out of expected range \n"%(i,bad_rms[i]))


fig = plt.figure(figsize=(16,9))
plt.title("RMS Noise: All Channels", size=22) 
plt.plot(rms,marker='o')

plt.ylim(0.2, 1.2)
plt.yticks(size = 18)
plt.xticks(np.arange(0, 16, 1), size = 18)
plt.xlabel('Channel', size = 18)
plt.ylabel('RMS Noise', size = 18)
plt.savefig( noise_dir + "RMS_NoiseTest_%s_%s_%s"%(env,refs,baseline) + ".png" )
plt.close()
    

