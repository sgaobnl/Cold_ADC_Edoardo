#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 17 16:54:11 2019

@author: shanshangao
"""
# This file takes care of the full configuration of ColdADC. 
# Input: reference, SDC enable, calibration weights (new or old), sampling rate.
# Set sampling rate, power supply configuration (different between BJT and CMOS references), configure ADC itself.


import adc_config as config
from cmd_library import CMD_ACQ
import time
import sys
import pickle
from keysight_e36312a_ps import PS_CTL
from all_ps_on import power_on_init
ps = PS_CTL()   #power supply library
cq = CMD_ACQ()  #command library

#From ADC configuration file (adc_config.py): temperature and directory name 
env = config.temperature
rawdir = config.subdir

#Turn on power supplies and set generator output off (default)
power_on_init()

#Input options from batch file: reference, SDC enable, weights selection, system sample rate 
#ADC Sample Rate = 16   ->  16 Ms/s sample rate of internal ADC, 2 MHz sample rate of full system ADC (not fully reliable operation)
#ADC Sample Rate = 4    ->  4 Ms/s sample rate of internal ADC, 500 kHz sample rate of full system ADC (reliable operation)
flg_bjt_r = (sys.argv[1] == "BJT")              #BJR reference flag
adc_sdc_en = (sys.argv[2] == "SDC")             #SDC enable flag
new_weights = (sys.argv[3] == "NEW_CALI")       #New calibration weights flag 
adc_sample_rate = sys.argv[4]                   #4 Ms/s internal ADC sample rate flag
clk10m_syn_en = (sys.argv[5] == "SYNC10M" ) #10MHz sync out 


def old_wghts():
    #Load calibration weights from Raw_Weights_(refs) binary file, produced during Initalization Checkout (cali_chk)
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
    
    #Configure normal input operation
    cq.Converter_Config(edge_sel = "Normal", out_format = "offset binary", 
                             adc_sync_mode ="Normal", adc_test_input = "Normal", 
                             adc_output_sel = "cali_ADCdata", adc_bias_uA = 50)
    print("Old weights reloaded!")



if(new_weights):
    cali = "new weights"
else:
    cali = "reload weights"


cq.bc.udp.write_reg_checked(0x05,0)
#reg5[0]: 0->-16Ms/s, 1--> 4Ms/s
#reg5[1]: 0->-10MHz sync out enable,  1--> disable
#reg5[4]: 0--> 2MHz & 64MHz enable, 1 --> disable
if(adc_sample_rate == "4"):
    print("Sampling frequency set: 500 kHz (ADC sampling at 4 Ms/s)")
    tmp = cq.bc.udp.read_reg(0x05)
    tmp = cq.bc.udp.read_reg(0x05)
    cq.bc.udp.write_reg_checked(0x05,tmp|0x01)

      
else:
    tmp = cq.bc.udp.read_reg(0x05)
    tmp = cq.bc.udp.read_reg(0x05)
    cq.bc.udp.write_reg_checked(0x05,tmp&0xFFFFFFFE)
    print("Sampling frequency set: 2 MHz (ADC sampling at 16 Ms/s)")

#if (clk10m_syn_en):
#    tmp = cq.bc.udp.read_reg(0x05)
#    tmp = cq.bc.udp.read_reg(0x05)
#    print("10MHz Sync out on MISC[0] is enabled")
#    cq.bc.udp.write_reg_checked(0x05,tmp&0xFFFFFFFD)
#else:
#    tmp = cq.bc.udp.read_reg(0x05)
#    tmp = cq.bc.udp.read_reg(0x05)
#    print("10MHz Sync out on MISC[0] is disabled")
#    cq.bc.udp.write_reg_checked(0x05,tmp|0x02)
#

#Set 2.8 V for channel 1 (VDDA2P5) if BJT reference is used    
ps.ps_init()
if(flg_bjt_r):
    adc_curr_src = "BJT-sd"
    cq.bc.udp.write(cq.bc.fpga_reg.MASTER_RESET,0)
    ps.off([1,2,3])
    time.sleep(5)
    ps.set_channel(1,2.8)
    ps.set_channel(2,2.1)
    ps.set_channel(3,2.25)
    ps.on([1,2,3])
    time.sleep(5)
    cq.bc.udp.write(cq.bc.fpga_reg.MASTER_RESET,1)
    time.sleep(10)

else:
    adc_curr_src = "CMOS-sd"
    cq.bc.udp.write(cq.bc.fpga_reg.MASTER_RESET,0)
    ps.off([1,2,3])
    time.sleep(5)
    ps.set_channel(1,2.5)
    ps.set_channel(2,2.1)
    ps.set_channel(3,2.25)
    ps.on([1,2,3])
    time.sleep(5)
    cq.bc.udp.write(cq.bc.fpga_reg.MASTER_RESET,1)
    time.sleep(10)

#Complete ADC configuration: input buffer, SDC, SHA, current source, references, weights)
if (adc_sdc_en):
    cq.adc_cfg(adc_sdc="On", adc_db="Bypass", adc_sha="Diff", adc_curr_src=adc_curr_src, env=env, flg_bjt_r=flg_bjt_r, cali = cali)
    print("SDC Enabled")
    if(cali == "reload weights"):
        old_wghts()
else:
    cq.adc_cfg(adc_sdc="Bypass", adc_db="Bypass", adc_sha="Single-ended", adc_curr_src=adc_curr_src, env=env, flg_bjt_r=flg_bjt_r, cali = cali)
    print("SDC Disabled")
    if(cali == "reload weights"):
        old_wghts()
