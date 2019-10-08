# -*- coding: utf-8 -*-
"""
Created on Wed Jul 24 00:00:54 2019

@author: protoDUNE
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

def file_list(runpath):
    if (os.path.exists(runpath)):
        for root, dirs, files in os.walk(runpath):
            break
    return files

test_ps = [
            [2, 2, "10us", "14mVfC", "900mV", "NoSDC"], 
           ]
mode16bit = False
if (mode16bit):
    adc_bits = "ADC16bit"
else:
    adc_bits = "ADC12bit"

nf_dir = "D:/ColdADC/ChipN_noise/"
nfr_dir = nf_dir + "results/"
    
for ty in range(len(test_ps)):
    noise_testno = test_ps[ty][0] 
    g_testno = test_ps[ty][1] 
    tp =  test_ps[ty][2]
    sg =  test_ps[ty][3]
    BL = test_ps[ty][4]
    

    f_dir = nf_dir
    fr_dir = nfr_dir
    
    if (os.path.exists(fr_dir)):
        pass
    else:
        try:
            os.makedirs(fr_dir)
        except OSError:
            print ("Error to create folder ")
            exit()
    
    noise_testno_str = "Test%02d"%noise_testno
    fs = file_list(runpath=f_dir)
    for f in fs:
        if (f.find(noise_testno_str)>0) and (f.find(tp)>0) and (f.find(sg)>0) and (f.find(".bin")>0) and (f.find(BL)>0):
            fn = f_dir + f
            break
    with open (fn, 'rb') as fp:
        chns = pickle.load(fp)
    
    if (True):
        fig = plt.figure(figsize=(16,9))

        for chnno in range(16):
            if (mode16bit):
                data_slice = np.array(chns[chnno][0:10000])&0xffff
            else:
                data_slice = (np.array(chns[chnno][0:10000])&0xffff)//16
                
            ax = plt.subplot2grid((16, 16), ( (chnno//4)*4, (chnno%4)*4) , colspan=4, rowspan=4)
    
            N = len(data_slice)
            rms = np.std(data_slice)
            ped = int(np.mean(data_slice))
            sigma3 = int(rms+1)*3
            ax.hist(data_slice, normed=1, bins=sigma3*2, range=(ped-sigma3, ped+sigma3),  histtype='bar', label="CH%d RMS: %.3f"%(chnno, rms), color='b', rwidth=0.9 )
            gaussian_x = np.linspace(ped - 3*rms, ped + 3*rms, 100)
            gaussian_y = mlab.normpdf(gaussian_x, ped, rms)
            ax.plot(gaussian_x, gaussian_y, color='r')

            ax.grid(True)
            ax.set_title("Histogram with " + "(%d samples)"%N )
            ax.set_xlabel("ADC output / LSB")
            ax.set_ylabel("Normalized counts")
            ax.legend(loc=3)

        plt.tight_layout(rect=[0, 0.05, 1, 0.95])
        plt.savefig( nfr_dir + "HIST_NoiseTest%d"%test_ps[ty][0] + test_ps[ty][2] +test_ps[ty][3] + test_ps[ty][4] +test_ps[ty][5] + adc_bits +  ".png" )
        plt.close()
