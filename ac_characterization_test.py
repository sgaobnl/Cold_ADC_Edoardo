# -*- coding: utf-8 -*-
"""
Created on Fri Aug  9 12:33:46 2019

@author: Edoardo Lopriore
"""
# This file executes dynamic behavior studies on binary data previously collected and saved (for example with cmp_app_testing). 
# Power spectrum is truncated to eliminate DC and Nyquist frequency bins.
# Dynamic behavior parameters:
# SFDR is calculated by dividing the signal power bins by the highest-amplitude spurious bins (SFDR in dBc, relative to carrier).
# SINAD is calculated by dividing the signal power bins by every noise and harmonic distortion bins. 
# ENOB is calculated with correction factor (Vfullscale/Vinput). We cannot use full-range sinewaves because of ColdADC overflowing issue. See MT-003 tutorial by Analog Devices for more information on this.
# Outputs PSD plot in dBFS (relative to Full Scale) with parameters printed out.

import numpy as np
import os
from sys import exit
import os.path
import math
import time

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
import matplotlib.mlab as mlab
from scipy.fftpack import fft,rfft,ifft,fftn
from scipy import signal
from itertools import chain

import pickle
plt.rcParams.update({'font.size': 16})

def round_up(n, decimals=0):
    multiplier = 10 ** decimals
    return math.ceil(n * multiplier) / multiplier

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
        
#        window = np.kaiser(Ntot, 11)
#        x = x*window
        
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




##### Sine Wave #####
N = 12
fs = 16000 #kHz
Ntot = 2**(11)
avgs = 10
Nsamps = avgs*Ntot
#fin = 152.8320 #kHz
fin = 85.9375 #kHz

Vfullscale = 1.5
Vinput = 1.0

## temperature can be room (rt) or cold (ln2)
tmp = "RT"

#fn = "D:/ColdADC/ADC_TST_IN/%s"%tmp + "_ac" + "_%d"%Ntot + "_%0.4f"%fin + ".bin"
#fn = "D:/ColdADC/ADC_TST_IN/ADC_TST_IN" + "_test" + ".bin"
fn = "D:/ColdADC/Performance Measurements/ADC_TST_IN/LN2_ac_2048_85.9375_stan" + ".bin"
with open (fn, 'rb') as fp:
    chns = pickle.load(fp)
    chns = list(np.array(chns)//16)


## AC Characterization ##

#for 2 Mhz (NOT adc test input)
#fft_data = chns[0]
    
#only for adc test input (using 16 Mhz):
N_single_chn = int(Nsamps/8)
fft_data = list(chain.from_iterable(zip(chns[0][:N_single_chn], chns[1][:N_single_chn],chns[2][:N_single_chn],chns[3][:N_single_chn],chns[4][:N_single_chn],chns[5][:N_single_chn],chns[6][:N_single_chn],chns[7][:N_single_chn])))
#psd = np.abs(rfft(fft_data))**2

#average calculation
#data_lst = [[] for x in range(avgs)]
#N_single_chn = int(Ntot/8)
#for i in range(0,avgs):
#    data_lst[i] = list(chain.from_iterable(zip(chns[0][i*N_single_chn:(i+1)*N_single_chn], chns[1][i*N_single_chn:(i+1)*N_single_chn],chns[2][i*N_single_chn:(i+1)*N_single_chn],chns[3][i*N_single_chn:(i+1)*N_single_chn],chns[4][i*N_single_chn:(i+1)*N_single_chn],chns[5][i*N_single_chn:(i+1)*N_single_chn],chns[6][i*N_single_chn:(i+1)*N_single_chn],chns[7][i*N_single_chn:(i+1)*N_single_chn])))
#
#chn_data = np.asarray(data_lst)
#fft_data = chn_data.ravel()    


#eliminate DC and Nyquist frequency
f, p, psd = chn_rfft_psd(fft_data, fs = fs, fft_s = Ntot, avg_cycle = avgs)
trunc = 2
p = p[trunc:Ntot-trunc]

#eliminate spurious bins (not correct)
#p_aux = np.copy(p)
#noise = min(p)
#spurious = 3
#while max(p_aux)>10**(0):
#    mx_arr = np.where(p_aux == max(p_aux))
#    print(max(p_aux))
#    mx = mx_arr[0]
#    p_aux[mx] = noise
#    for k in range(1, spurious+1):
#        p[mx-k] = noise
#        p_aux[mx-k] = noise
#        if(mx+k < len(p)):
#            p[mx+k] = noise
#            p_aux[mx+k] = noise


#consider all high bins for signal power (fundamental)
#p_aux = np.copy(p)
#noise = min(p)
#fundamental = 0
#while max(p_aux)>10**(1):
#    mx_arr = np.where(p_aux == max(p_aux))
#    print(max(p_aux))
#    mx = mx_arr[0]
#    fundamental = fundamental + max(p_aux)
#    p_aux[mx] = noise
#    print(fundamental)


#Span three bins at side of fundamental
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


NAD = np.sum(p) - signal_pwr
SINAD = 10*np.log10( signal_pwr / NAD )
ENOB = (SINAD - 1.76 + 20*np.log10(Vfullscale/Vinput)) / 6.02

fundamental = max(p)
SFDR = 10*np.log10( fundamental / max(p_aux))
              
#normalized power spectral density in dB
fig = plt.figure(figsize=(10,8))
trunc = 2
psd = psd[trunc:Ntot-trunc]
psd_dbfs = psd - max(psd) - 20*np.log10(Vfullscale/Vinput)
points_dbfs = np.linspace(0,fs/2, len(psd_dbfs))
plt.plot(points_dbfs, psd_dbfs)
plt.title('Stanford Research Generator \n %s.'%tmp + ' ADC Test Input. ' + 'Frequency = %0.4f'%fin + ' kHz . Bins = %d'%Ntot)
plt.xlabel('Frequency [MHz]')
plt.ylabel('Power Density Amplitude [dBFS]')
plt.annotate('SFDR = %0.2f dB \nSINAD = %0.2f dB \nENOB = %0.2f bits' %(np.around(SFDR, decimals=2), np.around(SINAD, decimals=2), np.around(ENOB, decimals = 2)), 
             xy=(0.65,0.8),xycoords='axes fraction', textcoords='offset points', size=14, bbox=dict(boxstyle="round", fc=(1.0, 1.0, 1.0), ec="none"))






#T = 1.0 / fs
#y = fft_data[:Ntot]
#
##w = signal.blackman(Ntot)
#w = np.kaiser(Ntot,8)
#
#ywf = fft(y*w)
#xf = np.linspace(0.0, 1.0/(2.0*T), Ntot//2)
#
#p = 2.0/Ntot * np.abs(ywf[1:Ntot//2])
#
#plt.semilogy(xf[4:Ntot//2], 2.0/Ntot * np.abs(ywf[4:Ntot//2]), '-b')
#plt.legend(['FFT', 'FFT w. window'])
#plt.grid()
#plt.show()
#
#p = p[4:Ntot//2]
#
#p_aux = np.copy(p)
#noise = min(p)
#spurious = 4
#while max(p_aux)>5*10**(6):
#    mx_arr = np.where(p_aux == max(p_aux))
#    print(max(p_aux))
#    mx = mx_arr[0]
#    p_aux[mx] = noise
#    for k in range(1, spurious+1):
#        p[mx-k] = noise
#        p_aux[mx-k] = noise
#        if(mx+k < len(p)):
#            p[mx+k] = noise
#            p_aux[mx+k] = noise
#
#fundamental = max(p)
#print(fundamental)
#NAD = np.sum(p) - fundamental
#SINAD = 10*np.log10( fundamental / NAD )
#
#ENOB = (SINAD - 1.76 + 20*np.log10(Vfullscale/Vinput)) / 6.02
#print(ENOB)

plt.tight_layout()
plt.show()