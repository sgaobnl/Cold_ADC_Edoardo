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

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
import matplotlib.mlab as mlab

import pickle

fn = "D:/ColdADC/D1_debug_asicdac5/Data_chn0_20us_dly0.bin"
with open (fn, 'rb') as fp:
    chns = pickle.load(fp)

fig = plt.figure(figsize=(8,8))    
for i in range(16):
    ax = plt.subplot2grid((8,2), (i%8, i//8), colspan=1, rowspan=1)
    sps = (len(chns[i]))
    x = np.arange(sps)*0.5
    ax.scatter(x[0:200], np.array(chns[i][0:200])&0x0000FFFF, marker ='.')
    ax.plot(x[0:200], np.array(chns[i][0:200])&0x0000FFFF)


plt.tight_layout()
plt.show()
#plt.savefig("d:/ColdADC/pics/" "a.png")
#plt.close()



