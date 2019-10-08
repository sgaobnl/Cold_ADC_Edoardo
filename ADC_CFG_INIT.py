#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 17 16:54:11 2019

@author: shanshangao
"""
#import numpy as np
import adc_config as config
from cmd_library import CMD_ACQ
import os
import sys
import csv
import pickle
cq = CMD_ACQ()  #command library

env = config.temperature
rawdir = config.subdir

flg_bjt_r = (sys.argv[1] == "BJT")
adc_sdc_en = (sys.argv[2] == "SDC")
new_weights = (sys.argv[3] == "NEW_CALI")

#### Debug #####
#env = "RT"
#flg_bjt_r = True
#adc_sdc_en = False
#new_weights = False
################


def old_wghts():
    print("Reloading old calibration weights...")
    cq.bc.udp.clr_server_buf()
    if(flg_bjt_r):
        refs = "BJT"
    else:
        refs = "CMOS"
        
    val = []
    reg = []

    wght_dir = rawdir + "Weights_Records/"
    with open(wght_dir + "Raw_Weights_%s.bin"%refs, "rb") as fp:   #unpickle raw weights
      reg,val = pickle.load(fp)
          
    print(val)
    print(reg)
    cq.bc.adc_load_weights(reg, val)
    cq.Converter_Config(edge_sel = "Normal", out_format = "offset binary", 
                             adc_sync_mode ="Normal", adc_test_input = "Normal", 
                             adc_output_sel = "cali_ADCdata", adc_bias_uA = 50)
    print("Old weights reloaded!")
    
if(new_weights):
    cali = "new weights"
else:
    cali = "reload weights"
    
if(flg_bjt_r):
    adc_curr_src = "BJT-sd"
else:
    adc_curr_src = "CMOS-sd"
print(adc_curr_src)

if (adc_sdc_en):
    cq.adc_cfg(adc_sdc="On", adc_db="Bypass", adc_sha="Diff", adc_curr_src=adc_curr_src, env=env, flg_bjt_r=flg_bjt_r, cali = cali)
    print("SDC Enabled")
    if(cali == "reload weights"):
        old_wghts()
else:
    cq.adc_cfg(adc_sdc="Bypass", adc_db="Bypass", adc_sha="Single-ended", adc_curr_src="BJT-sd", env=env, flg_bjt_r=flg_bjt_r, cali = cali)
    if(cali == "reload weights"):
        old_wghts()
