#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 17 16:54:11 2019

@author: shanshangao
"""
#import numpy as np
from cmd_library import CMD_ACQ
import time
import numpy as np
from raw_data_decoder import raw_conv
import pickle
import os
import sys
cq = CMD_ACQ() 

tp = sys.argv[1]
sg_str = sys.argv[2]
pls_str =  sys.argv[3]
snc_str = sys.argv[4]
sbf_str = sys.argv[5]
sdc_str = sys.argv[6]
sdacsw_str =  sys.argv[7]
testno = int(sys.argv[8])
env = sys.argv[9]

if tp == "05us":
    tpi = 1
elif tp == "10us":
    tpi = 0
elif tp == "20us":
    tpi = 3
else:
    tpi = 2
st = 16*[tpi]

if (pls_str == "PLS_EN"):
    sts=16*[1]
else:
    sts=16*[0]

if (sg_str == "47mVfC" ):
    sg = 16*[0] #4.7mV/fC   
elif (sg_str == "14mVfC"):
    sg = 16*[2] #14mV/fC 
elif (sg_str == "78mVfC"):
    sg = 16*[1] #14mV/fC 
elif (sg_str == "25mVfC"):
    sg = 16*[3] #14mV/fC 
    
if (snc_str == "900mV"):
    snc = 16*[0] #900mV
else:
    snc = 16*[1]

if (sbf_str == "BUF_ON"):
    sbf = 16*[1]
else:
    sbf = 16*[0]

if (sdc_str == "DC"):
    sdc = 0
else:
    sdc = 1

if (sdacsw_str == "disable"):
    sdacsw = 0 #disable
elif (sdacsw_str == "External"):
    sdacsw = 1 #disable
elif (sdacsw_str == "Internal"):
    sdacsw = 2 #disable
fpga_dac = 0
asic_dac = 8
print ("sdacsw = %d, fpga_dac = %d, asic_dac = %d"%(sdacsw, fpga_dac, asic_dac) )

rawdir = "D:/ColdADC/"
rawdir = rawdir + "D2_gainloss_acq_CMOS_LN/"
if (os.path.exists(rawdir)):
    pass
else:
    try:
        os.makedirs(rawdir)
    except OSError:
        print ("Error to create folder ")
        sys.exit()

cq.fe_cfg(sts=sts, snc=snc, sg=sg, st=st, sbf = sbf, sdc = sdc, sdacsw=sdacsw, fpga_dac=fpga_dac, asic_dac= asic_dac, delay = 0 )   
for delay in range(0,50,1):
    period = 200
    cq.bc.fe_pulse_param(delay=delay, period=period, width=0xa00)
    chns = cq.get_adcdata_raw(PktNum=20000 )

    fn = rawdir + "Gainloss_Test%02d_"%testno + tp + sg_str + snc_str + sbf_str + sdc_str + env + "_delay%02d"%delay +".bin"
    print (fn)
    with open(fn, 'wb') as f:
        pickle.dump(chns, f)
