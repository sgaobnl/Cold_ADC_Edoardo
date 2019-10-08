# -*- coding: utf-8 -*-
"""
Created on Mon Sep  9 11:00:21 2019

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
import scipy.optimize

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
    gen.gen_set(wave_type="SINE", freq="21000", amp = amp, dc_oft="0.9", load="Hi-Z") 
    #sinewave, Hi-Z termination
    
def take_data():    
    chns = cq.get_adcdata(PktNum=Ntot )
    fn = rawdir + "DNL_INL_sinewave" + ".bin"
    print (fn)
    with open(fn, 'wb') as f:
        pickle.dump(chns, f)
    
    if(mode16bit == False):    
        chns = list(np.array(chns)//16)
    chn_data = chns[0][:Ntot]
    return chn_data

##### Parameters for ENOB calculation #####
Ntot = 2**(22)
trunc = 200
if(env=="RT"):
    amp = "1.45VP"
else:
    amp = "1.40VP"

##### Data Directory #####
rawdir = "D:/ColdADC/"
rawdir = rawdir + "Static_Behavior/"
rawdir = rawdir + "Linearity/"
if (os.path.exists(rawdir)):
    pass
else:
    try:
        os.makedirs(rawdir)
    except OSError:
        print ("Error to create folder ")
        sys.exit()

##### DNL and INL Calculation, Sinewave Cumulative Histogram method #####
set_generator()
chn_data = take_data()    
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
#Arbitrary bit truncation
trunc=trunc;
hlin_trunc = hlin[trunc:-trunc]
#LSB calculation as average code width
lsb = np.sum(hlin_trunc) / len(hlin_trunc)
#DNL: concatenate a 0 at the beginning
dnl = np.insert(hlin_trunc/lsb-1, 0, 0.)
#Misscodes detection
misscodes = np.where((dnl > 1) | (dnl < -1))
if(np.array(misscodes).size > 0):
    cq.err_log('Number of misscodes found = %d' %np.array(misscodes).size)
    cq.status = "FAIL"
#INL: cumulative sum of DNL
inl = np.cumsum(dnl)

fig = plt.figure(figsize=(10,8))
ax1 = plt.subplot2grid((2,2), (0, 0), colspan=2, rowspan=1)
ax1.x = np.arange(first_bin + trunc, last_bin - trunc +1)
ax1.plot(ax1.x,dnl)
ax1.set_xlim([0,4095])
ax1.set_ylim([-0.8,0.8])
ax1.set_title('%s1 Environment. %s2 References'%(env, refs))
ax1.set_ylabel('DNL [LSB]')
ax1.annotate(' max DNL = %0.2f \n min DNL = %0.2f ' %(np.around(max(dnl), decimals=2), np.around(min(dnl), decimals=2)), 
             xy=(0.76,0.8),xycoords='axes fraction', textcoords='offset points', size=14, bbox=dict(boxstyle="round", fc=(1.0, 1.0, 1.0), ec="none"))

ax2 = plt.subplot2grid((2,2), (1, 0), colspan=2, rowspan=1)
ax2.x = np.arange(first_bin + trunc, last_bin - trunc +1)
ax2.plot(ax2.x,inl)
ax2.set_xlim([0,4095])
ax2.set_ylim([-6.5,6.5])
ax2.set_ylabel('INL [LSB]')
ax2.annotate(' max INL = %0.2f \n min INL = %0.2f ' %(np.around(max(inl), decimals=2), np.around(min(inl), decimals=2)), 
             xy=(0.76,0.8),xycoords='axes fraction', textcoords='offset points', size=14, bbox=dict(boxstyle="round", fc=(1.0, 1.0, 1.0), ec="none"))

plt.xlabel('ADC Code')

plt.tight_layout()
plt.savefig( rawdir + "DNL_INL_%s1_%s2"%(refs,env) + ".png" )
plt.close()   