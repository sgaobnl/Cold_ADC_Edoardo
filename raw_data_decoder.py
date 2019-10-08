# -*- coding: utf-8 -*-
"""
Created on Wed Jul 24 00:00:54 2019

@author: protoDUNE
"""

from sys import exit
#import os.path
#import math
#import time

#import matplotlib.pyplot as plt
#import matplotlib.gridspec as gridspec
#import matplotlib.patches as mpatches
#import matplotlib.mlab as mlab
#
#import pickle
#
import numpy as np
import struct

def raw_conv(raw_data, pktnum = -1):
    chn_data_pls=[[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],]
    chn_data=[[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],]
    pkg_len = (0x1610//2)
    for upkg in raw_data:
        dataNtuple =struct.unpack_from(">%dH"%(pkg_len),upkg)
        i = 8
        while (i <= pkg_len-22):
            if (dataNtuple[i] == 0xbc3c ) :
                for chn in range(16):
                    if (dataNtuple[i+4] == 0x0001):
                        chn_data_pls[chn].append(dataNtuple[i+6+chn] + 0x10000 )
                    else:
                        chn_data_pls[chn].append(dataNtuple[i+6+chn] )
            else:
                print ("Error: incomplete user package is found, please retake data")
                exit()
            i = i + 22 
    for i in range(len(chn_data_pls)):
        chn_data[i] = list( np.array( chn_data_pls[i][0:pktnum] ) & 0xffff )
        chn_data_pls[i] = chn_data_pls[i][0:pktnum] 
    return chn_data, chn_data_pls

#fn = "D:/ColdADC/C3_debug_asicdac5/Data_chn0_20us_dly0.bin"
#print (fn)
#print ("wait...")
#with open (fn, 'rb') as fp:
#    rawdata = pickle.load(fp)
#
#
#chn_data = raw_conv(rawdata)
#print ("Total samples = %d"%(len(chn_data[0])))
#for i in range(16):
#    print (hex(chn_data[i][0]))

