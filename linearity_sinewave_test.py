# -*- coding: utf-8 -*-
"""
Created on Fri Aug  9 12:29:51 2019

@author: Edoardo Lopriore
"""
# This file executes DNL and INL calculation and plotting from binary data previously collected and saved (for example with cmp_app_testing.py).
# Sinewave cumulative histogram method (first implementation)  ->   J. Doernberg, H.-S. Lee, and D. Hodges, “Full-speed testing of A/D converters”, IEEE Journal of Solid-State Circuits, vol. 19, no. 6, pp. 820–827, 1984.
# Wide documentation about this matter can be found in documents on ADC testing by Analog Devices, Maxim Integrated, Texas Instruments and more.
# Frozen SHA: remember that in this case we have only one active channel for every internal ADC, therefore chns[0] represents sample number 0 and chns[i] is sample i (for i between 0 and 7).

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
import scipy.optimize
from itertools import chain

import pickle

plt.rcParams.update({'font.size': 16})

#freq = 21 #kHz
N = 12
Ntot = 4194304 

##### ADC_TST_IN Sine Wave #####
#vpp = 1.496 #V
#offset = 0.88 #V, real input offset (double the sine wave generator offset)


fn = "D:/ColdADC/ADC_TST_IN/ADC_TST_IN" + "_test" + ".bin"
#fn = "D:/ColdADC/SHA/RT_lin_ch7_free_clk500k" + ".bin"
with open (fn, 'rb') as fp:
    chns = pickle.load(fp)
    chns = list(np.array(chns)//16)


chn_data = chns[0][:Ntot]


# For frozen SHA: all time slices option
#chn_data = []
#for i in range(524288):
#    for j in range(8):
#        chn_data.append(chns[j][i])
    



# DNL and INL, Cumulative Histogram method ##
val, bins = np.histogram(chn_data, bins = 4095, range = (0,4095))
nonzero_bins = np.nonzero(val)
first_bin = nonzero_bins[0][0]
last_bin = nonzero_bins[0][-1]
val_nonzero = val[np.nonzero(val)]
sum_Hk = np.cumsum(val_nonzero)
#normalized transition voltages
Vj = - np.cos(np.pi*sum_Hk/Ntot)
end = len(Vj)
#linearized histogram
hlin =  Vj[1:] - Vj[:-1]
#first and last bit truncation (can be extended)
trunc=200;
hlin_trunc = hlin[trunc:-trunc]
#LSB calculation as average code width
lsb = np.sum(hlin_trunc) / len(hlin_trunc)
#DNL, concatenate a 0 at the beginning
dnl = np.insert(hlin_trunc/lsb-1, 0, 0.)

inl = np.cumsum(dnl)

fig = plt.figure(figsize=(10,8))
ax1 = plt.subplot2grid((2,2), (0, 0), colspan=2, rowspan=1)
ax1.x = np.arange(first_bin + trunc, last_bin - trunc +1)
ax1.plot(ax1.x,dnl)
ax1.set_xlim([0,4095])
ax1.set_ylim([-0.8,0.8])
ax1.set_title('RT. Frozen SHA + ADC0 (Channel 7). Sample 2')
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

# Sine wave example (channel 0) and complete histogram ##
fig = plt.figure(figsize=(10,8))
sps = (len(chn_data))
x = np.arange(sps)*0.5
ax1 = plt.subplot2grid((2,1), (0, 0), colspan=1, rowspan=1)
ax1.scatter(x[0:200], np.array(chn_data[0:200])&0x0000FFFF, marker ='.')
ax1.plot(x[0:200], np.array(chn_data[0:200])&0x0000FFFF)

ax2 = plt.subplot2grid((2,1), (1, 0), colspan=1, rowspan=1)
ax2.hist(chn_data, bins = last_bin - first_bin)

plt.tight_layout()
plt.show()
