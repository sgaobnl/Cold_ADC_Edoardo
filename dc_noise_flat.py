# -*- coding: utf-8 -*-
"""
Created on Thu Sep 12 09:57:53 2019

@author: Edoardo Lopriore
"""
import numpy as np
import os
from sys import exit
import os.path
import math
import time
import statsmodels.api as sm

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
import matplotlib.mlab as mlab
import pickle
from stanford_ds360_gen import GEN_CTL
from cmd_library import CMD_ACQ
cq = CMD_ACQ()  #command library
gen = GEN_CTL() #signal generator library

env = "RT"
baseline = 200

mode16bit = False
if (mode16bit):
    adc_bits = "ADC16bit"
else:
    adc_bits = "ADC12bit"


fn = "D:/ColdADC/ADC_TST_IN/ADC_TST_IN" + "_test" + ".bin"
with open (fn, 'rb') as fp:
    chns = pickle.load(fp)
                
rawdir = "D:/ColdADC/"
rawdir = rawdir + "DC_Noise/"
if (os.path.exists(rawdir)):
    pass
else:
    try:
        os.makedirs(rawdir)
    except OSError:
        print ("Error to create folder ")
        sys.exit()
        

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
    ax.hist(data_slice, normed=1, bins=sigma3*2, range=(ped-sigma3, ped+sigma3),  histtype='bar', label="CH%d RMS: %.3f"%(chnno, rms[chnno]), rwidth=0.9 )
    gaussian_x = np.linspace(ped - 3*rms[chnno], ped + 3*rms[chnno], 100)
    gaussian_y = mlab.normpdf(gaussian_x, ped, rms[chnno])
    ax.plot(gaussian_x, gaussian_y, color='r')
    
    ax.grid(True)
    if(chnno == 0 or chnno == 4 or chnno == 8 or chnno == 12):
        ax.set_ylabel("Normalized counts", size = 14)
    if(chnno == 12 or chnno == 13 or chnno == 14 or chnno == 15):
        ax.set_xlabel("ADC output / LSB", size = 14)
    ax.legend(loc=3, fontsize = 'x-small')

fig.suptitle("RMS Noise: Histogram with " + "%d samples"%N, size=18)      
fig.tight_layout()
fig.subplots_adjust(top=0.92)
plt.savefig( rawdir + "Hist_NoiseTest_%d_%s"%(baseline,env) + ".png" )
#plt.close()

bad_rms = [x for x in rms if (x>0.8 or x<0.3)]
if not (bad_rms == []):
    for i in range(len(bad_rms)):
        cq.err_log("Channel %d RMS Noise (%f) is out of expected range \n"%(i,bad_rms[i]))
        cq.status = "FAIL"


fig = plt.figure(figsize=(16,9))
fig.suptitle("RMS Noise: All Channels", size=18) 
plt.plot(rms,marker='o')
plt.ylim(0.2, 1.2)
plt.xticks(np.arange(0, 16, 1))
plt.xlabel('Channel', size = 16)
plt.ylabel('RMS Noise', size = 16)
plt.savefig( rawdir + "RMS_NoiseTest_%d_%s"%(baseline,env) + ".png" )
plt.show()
plt.close()