# -*- coding: utf-8 -*-
"""
Created on Mon Sep  9 11:17:56 2019

@author: Edoardo Lopriore
"""
import numpy as np
import os
from sys import exit
import os.path
import math
import time
from raw_data_decoder import raw_conv

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
import matplotlib.mlab as mlab
from scipy.fftpack import fft,rfft,ifft,fftn
from scipy import signal
from itertools import chain

import pickle
from cmd_library import CMD_ACQ
from stanford_ds360_gen import GEN_CTL
cq = CMD_ACQ()  #command library
gen = GEN_CTL() #signal generator library

#env = sys.argv[1]
#refs = sys.argv[2]
env = "RT"
refs = "BJT"

plt.rcParams.update({'font.size': 16})
mode16bit = False
if (mode16bit):
    adc_bits = "ADC16bit"
else:
    adc_bits = "ADC12bit"


def set_generator():
    gen.gen_init()
    gen.gen_set(wave_type="SINE", freq="88378.9", amp="1.0VP", dc_oft="0.9", load="Hi-Z") 
    #sinewave, Hi-Z termination

def take_data():
    chns = cq.get_adcdata(PktNum=Nsamps )
    fn = rawdir + "ENOB" + ".bin"
    print (fn)
    with open(fn, 'wb') as f:
        pickle.dump(chns, f)

    if(mode16bit == False):
        chns = list(np.array(chns)//16)
    data = chns[0]
    return data
    
def chn_rfft_psd(chndata, fs = 2000000.0, fft_s = 2000, avg_cycle = 50):  
    ts = 1.0/fs;# sampling interval
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
            p = abs(rfft(x)/fft_s)**2# fft computing and normalization
        else:
            p = p + (abs(rfft(x)/fft_s))**2# fft computing and normalization
    psd = p / avg_cycle_tmp
    psd = p / ( fs/fft_s)
    psd = p*2
    f = np.linspace(0,fs/2,len(psd))
    psd = 10*np.log10(psd)
    return f,p,psd

##### Parameters for DNL/INL Calculation #####
Nsamps = 2**(16)
Ntot = 2**(12)
fs = 2000 #kHz
fin = 88.3789 #kHz
Vinput = 1.0 #V
Vfullscale = 1.5 #V
avgs = 10

##### Data Directory #####
rawdir = "D:/ColdADC/"
rawdir = rawdir + "Dynamic_Behavior/"
if (os.path.exists(rawdir)):
    pass
else:
    try:
        os.makedirs(rawdir)
    except OSError:
        print ("Error to create folder ")
        sys.exit()

##### FFT and PSD Calculation #####
set_generator()
fft_data = take_data()
f, p, psd = chn_rfft_psd(fft_data, fs = fs, fft_s = Ntot, avg_cycle = avgs)
#Truncate DC and Nyquist bins
trunc = 2
p = p[trunc:Ntot-trunc]
#Eliminate spurious bins
p_aux = np.copy(p)
noise = min(p)
spurious = 3
while max(p_aux)>10**(0):
    mx_arr = np.where(p_aux == max(p_aux))
    print(max(p_aux))
    mx = mx_arr[0]
    p_aux[mx] = noise
    for k in range(1, spurious+1):
        p[mx-k] = noise
        p_aux[mx-k] = noise
        if(mx+k < len(p)):
            p[mx+k] = noise
            p_aux[mx+k] = noise

##### Extract parameters of interest #####
fundamental = max(p)
print(fundamental)
NAD = np.sum(p) - fundamental
SINAD = 10*np.log10( fundamental / NAD )
ENOB = (SINAD - 1.76 + 20*np.log10(Vfullscale/Vinput)) / 6.02
p_NAD = np.copy(p)
p_NAD[np.where(p == max(p))] = 0
SFDR = 10*np.log10( fundamental / max(p_NAD))
              
##### Plot normalized power spectral density in dBFS #####
fig = plt.figure(figsize=(10,8))
trunc = 2
psd = psd[trunc:Ntot-trunc]
psd_dbfs = psd - max(psd)
points_dbfs = np.linspace(0,fs/2, len(psd_dbfs))
plt.plot(points_dbfs, psd_dbfs)
plt.title('Stanford Research Generator W/ Synchronized CLK   \n %s.'%env + ' ADC Test Input. ' + 'Frequency = %0.4f'%fin + ' kHz . Bins = %d'%Ntot)
plt.xlabel('Frequency [MHz]')
plt.ylabel('Power Density Amplitude [dBFS]')
plt.annotate('SFDR = %0.2f dB \nSINAD = %0.2f dB \nENOB = %0.2f bits' %(np.around(SFDR, decimals=2), np.around(SINAD, decimals=2), np.around(ENOB, decimals = 2)), 
             xy=(0.65,0.8),xycoords='axes fraction', textcoords='offset points', size=14, bbox=dict(boxstyle="round", fc=(1.0, 1.0, 1.0), ec="none"))

plt.tight_layout()
plt.savefig( rawdir + "ENOB"+ ".png" )
plt.close()  