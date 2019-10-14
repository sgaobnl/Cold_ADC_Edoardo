# -*- coding: utf-8 -*-
"""
Created on Thu Sep  5 16:20:54 2019

@author: Edoardo Lopriore
"""
# This is the first file of the full procedure. Initialization Checkout flow:
# (0) Initialize power supply, initialize and disable signal generator, initialize logs, set system frequency, do quick ADC initialization test
# (1) Power check                             ->   Save power consumption data and check if in normal range (yet to be defined)
# (2) Communication check                     ->   Read and write registers with UART and I2C
# (3) Pattern and registers check             ->   Nominal test pattern values for ADC0 and ADC1, default registers values
# (4) Reference check                         ->   Sweep plots of reference voltages and currents, check monotonicity
# (5) Synchronization and calibration check   ->   Correct channel mapping (backend communication), record calibration weights


import adc_config as config
from cmd_library import CMD_ACQ
import time
import os
import sys
import csv
import pickle
import numpy as np
import matplotlib.pyplot as plt
from keysight_e36312a_ps import PS_CTL
from stanford_ds360_gen import GEN_CTL
from rigol_dp832_ps import RIGOL_PS_CTL
gen = GEN_CTL() #signal generator library
ps = PS_CTL()   #power supply library
fm_ps = RIGOL_PS_CTL() 
cq = CMD_ACQ()  #command library

#From ADC configuration file (adc_config.py): temperature and directory name. Create directory if not present
env = config.temperature
rawdir = config.subdir
if (os.path.exists(rawdir)):
    pass
else:
    try:
        os.makedirs(rawdir)
    except OSError:
        print ("Error to create folder ")
        sys.exit()    

ref_set_dir = rawdir + "/Ref_set/"
if (os.path.exists(ref_set_dir )):
    pass
else:
    try:
        os.makedirs(ref_set_dir )
    except OSError:
        print ("Error to create folder ")
        sys.exit()    

def pwr_chk():
    #Power check: record voltages and currents from Keysight E36312A and check if in normal range (not defined yet)
    pwr_cycles = 5
    flg = [0,0,0]
    chn = ["VDDA2P5 & VDDD2P5","VDDD1P2","VDDIO"]
    
    #BJT reference
    voltages = [0,0,0]
    v_bjt = [0,0,0]
    currents = [0,0,0]
    i_bjt = [0,0,0]
    powers = [0,0,0]
    p_bjt = [0,0,0]
    #Repeat for number of power cycles
    for i in range(pwr_cycles):
        #Procedure: high master reset -> power off channel 3 -> power off channels 1 and 2 -> power on all channels -> low master reset
        cq.bc.udp.write(cq.bc.fpga_reg.MASTER_RESET,0) 
        time.sleep(1)
        ps.off([1,2, 3])
        if(env == "RT"):
            time.sleep(5)
        else:
            #With LN2, wait longer (current settling)
            time.sleep(30)
        
        #Set VDDA2P5 to 2.8 V for BJT reference only (known issue at LN2 with nominal 2.5 V)
        ps.set_channel(1,2.8)
        ps.set_channel(2,2.1)
        ps.set_channel(3,2.25)
        ps.on([1,2,3])
        time.sleep(5)
        cq.bc.udp.write(cq.bc.fpga_reg.MASTER_RESET,1) 
        time.sleep(1)
        cq.flg_bjt_r = True
        cq.adc_cfg_init(adc_sdc="Bypass", adc_db="Bypass", adc_sha="Single-ended", adc_curr_src="BJT-sd", fn=ref_set_dir)
        time.sleep(5)
        voltages = ps.measure_voltages()
        currents = ps.measure_currents()
        powers = [a*b for a,b in zip(voltages,currents)]
        v_bjt = [x + y for x, y in zip(v_bjt, voltages)]
        i_bjt = [x + y for x, y in zip(i_bjt, currents)]
        p_bjt = [x + y for x, y in zip(p_bjt, powers)]
        #print("Power Channel 1 = %f1 W \nPower Channel 2 = %f2 W \nPower Channel 3 = %f W"%(powers[0],powers[1],powers[2]))
        #If power is higher than expected, flag = 1 -> Status = FAIL, write in Error Log
        if(env=="RT"):
            if(powers[0] > 1.00 or powers[0] < 0.40):
                flg[0] = 1
            else:
                flg[0] = 0
            if(powers[1] > 0.130 or powers[1] < 0.001):
                flg[1] = 1
            else:
                flg[1] = 0
            if(powers[2] > 0.160 or powers[2] < 0.001):
                flg[2] = 1
            else:
                flg[2] = 0
        
        else:
            if(powers[0] > 1.00 or powers[0] < 0.40):
                flg[0] = 1
            else:
                flg[0] = 0
            if(powers[1] > 0.120 or powers[1] < 0.001):
                flg[1] = 1
            else:
                flg[1] = 0
            if(powers[2] > 0.130 or powers[2] < 0.001):
                flg[2] = 1
            else:
                flg[2] = 0
    
    v_bjt[:] = [x / pwr_cycles for x in v_bjt]
    i_bjt[:] = [x / pwr_cycles for x in i_bjt]
    p_bjt[:] = [x / pwr_cycles for x in p_bjt]
    print(v_bjt)
    print(i_bjt)
    print(p_bjt)
    record_power(v_bjt,i_bjt,p_bjt,flg_bjt_r = True)        
    
    for i in range(len(flg)):
        if(flg[i]==1):
            cq.err_log("BJT Reference: Power channel %d (%s) out of range(%f W) \n"%(i+1,chn[i],p_bjt[i]))
            cq.status("FAIL")   
    if(flg == [0,0,0]):
        print("BJT Reference: Power consumption is in normal range")   
        cq.pass_log("Power consumption (BJT reference): PASS \n")

    #CMOS reference (same procedure)
    v_cmos = [0,0,0]
    i_cmos = [0,0,0]
    p_cmos = [0,0,0]
    flg = [0,0,0]
#    cq.ref_set(flg_bjt_r = False , env=env)
    #Powerdown BJT reference (optional)
    #cq.bc.adc_ref_powerdown(1,1)
    for i in range(pwr_cycles):
        cq.bc.udp.write(cq.bc.fpga_reg.MASTER_RESET,0) 
        time.sleep(1)
        ps.off([1,2,3])
        if(env == "RT"):
            time.sleep(5)
        else:
            time.sleep(30)
        ps.set_channel(1,2.5)
        ps.set_channel(2,2.1)
        ps.set_channel(3,2.25)
        ps.on([1,2,3])
        time.sleep(5)
        cq.bc.udp.write(cq.bc.fpga_reg.MASTER_RESET,1) 
        time.sleep(1)
        cq.flg_bjt_r = False
        cq.adc_cfg_init(adc_sdc="Bypass", adc_db="Bypass", adc_sha="Single-ended", adc_curr_src="CMOS-sd", fn=ref_set_dir)
        time.sleep(5)
        voltages = ps.measure_voltages()
        currents = ps.measure_currents()
        powers = [a*b for a,b in zip(voltages,currents)]
        v_cmos = [x + y for x, y in zip(v_cmos, voltages)]
        i_cmos = [x + y for x, y in zip(i_cmos, currents)]
        p_cmos = [x + y for x, y in zip(p_cmos, powers)]
#        print("Power Channel 1 = %f1 W \nPower Channel 2 = %f2 W \nPower Channel 3 = %f W"%(powers[0],powers[1],powers[2]))
        if(env=="RT"):
            if(powers[0] > 0.90 or powers[0] < 0.20):
                flg[0] = 1
            else:
                flg[0] = 0
            if(powers[1] > 0.030 or powers[1] < 0.005):
                flg[1] = 1
            else:
                flg[1] = 0
            if(powers[2] > 0.060 or powers[2] < 0.010):
                flg[2] = 1
            else:
                flg[2] = 0
        
        else:
            if(powers[0] > 0.90 or powers[0] < 0.20):
                flg[0] = 1
            else:
                flg[0] = 0
            if(powers[1] > 0.020 or powers[1] < 0.002):
                flg[1] = 1
            else:
                flg[1] = 0
            if(powers[2] > 0.030 or powers[2] < 0.004):
                flg[2] = 1
            else:
                flg[2] = 0
    
    v_cmos[:] = [x / pwr_cycles for x in v_cmos]
    i_cmos[:] = [x / pwr_cycles for x in i_cmos]
    p_cmos[:] = [x / pwr_cycles for x in p_cmos]
    record_power(v_cmos,i_cmos,p_cmos,flg_bjt_r = False)
    print(v_cmos)
    print(i_cmos)
    print(p_cmos)
    
    for i in range(len(flg)):
        if(flg[i]==1):
            cq.err_log("CMOS Reference: Power channel %d (%s) out of range(%f W) \n"%(i+1,chn[i],p_cmos[i]))
            cq.status("FAIL") 
    if(flg == [0,0,0]):
        print("CMOS Reference: Power consumption is in normal range") 
        cq.pass_log("Power consumption (CMOS reference): PASS \n")
        
def record_power(v,i,p,flg_bjt_r):
    fields = ['Quantity','CH1 (VDDA2P5)', 'CH2 (VDDD1P2)', 'CH3 (VDDD2P5)'] 
    rows = []
    if(flg_bjt_r):
        refs = "BJT"
    else:
        refs = "CMOS"
    
    rows.append(['Voltage [V]','%.3f'%(v[0]),'%.3f'%(v[1]),'%.3f'%(v[2])])
    rows.append(['Current [mA]','%.3f'%(i[0]*10**3),'%.3f'%(i[1]*10**3),'%.3f'%(i[2]*10**3)])
    rows.append(['Power [mW]','%.3f'%(p[0]*10**3),'%.3f'%(p[1]*10**3),'%.3f'%(p[2]*10**3)])
    
    pwr_dir = rawdir + "Power_Check/"
    if (os.path.exists(pwr_dir)):
        pass
    else:
        try:
            os.makedirs(pwr_dir)
        except OSError:
            print ("Error to create folder ")
            sys.exit()
            
    filename = pwr_dir + "Power_Check_%s.csv"%refs      
    print(filename)    
    # writing to csv file 
    with open(filename, 'w', newline='') as csvfile: 
        csvwriter = csv.writer(csvfile) 
        csvwriter.writerow(fields) 
        csvwriter.writerows(rows)   
    csvfile.close()        


def strictly_increasing(L):
    return all(x<y for x, y in zip(L, L[1:]))

def strictly_decreasing(L):
    return all(x>y for x, y in zip(L, L[1:]))

def non_increasing(L):
    return all(x>=y for x, y in zip(L, L[1:]))

def non_decreasing(L):
    return all(x<=y for x, y in zip(L, L[1:]))

def monotonic(L):
    return non_increasing(L) or non_decreasing(L)

def record_weights(reg, val, flg_bjt_r):  
    #Saves calibration weights for BJT and CMOS references in two CSV files
    
    #CSV field names 
    fields = ['Internal ADC', 'Weight', 'Stage', 'Value'] 
    rows = []
    if(flg_bjt_r):
        refs = "BJT"
    else:
        refs = "CMOS"
    
    #Create Weights_Records directory
    wght_dir = rawdir + "Weights_Records/"
    if (os.path.exists(wght_dir)):
        pass
    else:
        try:
            os.makedirs(wght_dir)
        except OSError:
            print ("Error to create folder ")
            sys.exit() 
    
    #Pickle raw weights
    with open(wght_dir + "Raw_Weights_%s.bin"%refs, "wb") as fp:  
      pickle.dump((reg,val), fp)
     
    print(val)
    
    #Save weights: indicate internal ADC (0 or 1), weight number (Wx) and stage number
    for i in range(0,14,2):
        internal_adc = "ADC0"
        wght_nr = "W0"
        stage = (reg[i]-0) / 2
        wght_val = (val[i+1]<<8)|(val[i])           
        rows.append([internal_adc, wght_nr, stage, wght_val])      
    for i in range(14,28,2):
        internal_adc = "ADC0"
        wght_nr = "W2"
        stage = (reg[i]-0x20) / 2
        wght_val = (val[i+1]<<8)|(val[i]) 
        rows.append([internal_adc, wght_nr, stage, wght_val])      
    for i in range(28,42,2):
        internal_adc = "ADC1"
        wght_nr = "W0"
        stage = (reg[i]-0x40) / 2
        wght_val = (val[i+1]<<8)|(val[i])
        rows.append([internal_adc, wght_nr, stage, wght_val])      
    for i in range(42,56,2):
        internal_adc = "ADC1"
        wght_nr = "W2"
        stage = (reg[i]-0x60) / 2
        wght_val = (val[i+1]<<8)|(val[i])
        rows.append([internal_adc, wght_nr, stage, wght_val])     

    record_dir = rawdir + "Weights_Records/"
    if (os.path.exists(record_dir)):
        pass
    else:
        try:
            os.makedirs(record_dir)
        except OSError:
            print ("Error to create folder ")
            sys.exit()
    filename = record_dir + "Weights_Record_%s.csv"%refs          

    with open(filename, 'w', newline='') as csvfile: 
        csvwriter = csv.writer(csvfile) 
        csvwriter.writerow(fields) 
        csvwriter.writerows(rows)   
    csvfile.close()        

def refs_plot():
    #Create sweep plots of reference settings for both BJT and CMOS. If not monotonic, Status = FAIL and report in Error Log
    ref_dir = rawdir + "Reference_Check/"
    if (os.path.exists(ref_dir)):
        pass
    else:
        try:
            os.makedirs(ref_dir)
        except OSError:
            print ("Error to create folder ")
            sys.exit()          
    vrefp_bjt = []
    vrefn_bjt = []
    vcmi_bjt = []
    vcmo_bjt = []
    ibuff0_bjt = []
    ibuff1_bjt = []
    ivdac0 = []
    ivdac1 = []       
    vrefp_cmos = []
    vrefn_cmos = []
    vcmi_cmos = []
    vcmo_cmos = []
    ibuff_cmos = []
    cq.init_chk()
    #Collect BJT references (2.8 V for VDDA2P5)
    ps.set_channel(1,2.8)
    time.sleep(5)
    cq.flg_bjt_r = True
    vrefp_bjt, vrefn_bjt, vcmi_bjt, vcmo_bjt, ibuff0_bjt, ibuff1_bjt, ivdac0_bjt, ivdac1_bjt = cq.refs_chk()
    with open(ref_dir + "BJT_ref_cali.bin", "wb") as fp:  
        pickle.dump((vrefp_bjt, vrefn_bjt, vcmi_bjt, vcmo_bjt, ibuff0_bjt, ibuff1_bjt, ivdac0_bjt, ivdac1_bjt), fp)

    #Collect CMOS references (2.5 V for VDDA2P5)
    ps.set_channel(1,2.5)
    time.sleep(5)
    cq.flg_bjt_r = False
    vrefp_cmos, vrefn_cmos, vcmi_cmos, vcmo_cmos, ibuff_cmos = cq.refs_chk()
    with open(ref_dir + "CMOS_ref_cali.bin", "wb") as fp:  
        pickle.dump((vrefp_cmos, vrefn_cmos, vcmi_cmos, vcmo_cmos, ibuff_cmos), fp)

    #Check sweep plots monotonicity
    if(not monotonic(vrefp_bjt)):
        cq.status("FAIL") 
        cq.err_log("Reference setting error: VREFP (BJT) is not monotonic \n")
    if(not monotonic(vrefn_bjt)):
        cq.status("FAIL") 
        cq.err_log("Reference setting error: VREFN (BJT) is not monotonic \n")
    if(not monotonic(vcmi_bjt)):
        cq.status("FAIL") 
        cq.err_log("Reference setting error: VCMI (BJT) is not monotonic \n")
    if(not monotonic(vcmo_bjt)):
        cq.status("FAIL") 
        cq.err_log("Reference setting error: VCMO (BJT) is not monotonic \n")
    if(not monotonic(ibuff0_bjt)):
        cq.status("FAIL") 
        cq.err_log("Reference setting error: IBUFF0 (BJT) is not monotonic \n")
#    if(not monotonic(ibuff1_bjt)):
#        cq.status("FAIL") 
#        cq.err_log("Reference setting error: IBUFF1 (BJT) is not monotonic \n")
    if(not monotonic(ivdac0_bjt)):
        cq.status("FAIL") 
        cq.err_log("Reference setting error: IDAC0 (BJT) is not monotonic \n")    
    if(not monotonic(ivdac1_bjt)):
        cq.status("FAIL") 
        cq.err_log("Reference setting error: IDAC1 (BJT) is not monotonic \n")
    if(not monotonic(vrefp_cmos)):
        cq.status("FAIL") 
        cq.err_log("Reference setting error: VREFP (CMOS) is not monotonic \n")
    if(not monotonic(vrefn_cmos)):
        cq.status("FAIL") 
        cq.err_log("Reference setting error: VREFN (CMOS) is not monotonic \n")
    if(not monotonic(vcmi_cmos)):
        cq.status("FAIL") 
        cq.err_log("Reference setting error: VCMI (CMOS) is not monotonic \n")
    if(not monotonic(vcmo_cmos)):
        cq.status("FAIL") 
        cq.err_log("Reference setting error: VCMO (CMOS) is not monotonic \n")        
    if(not monotonic(ibuff_cmos)):
        cq.status("FAIL") 
        cq.err_log("Reference setting error: IBUFF (CMOS) is not monotonic \n")              
        
    sweep = len(vrefp_bjt) #18
    
   
    #Reference sweep plots: BJT
    fig = plt.figure(figsize=(18,8))
    ax1 = plt.subplot2grid((2,4), (0, 0), colspan=1, rowspan=1)
    ax1.x = 15*np.arange(sweep)
    ax1.plot(ax1.x,vrefp_bjt)
    ax1.set_title('VREFP (BJT)')
    ax1.set_ylabel('VREFP [V]')
    
    ax2 = plt.subplot2grid((2,4), (0, 1), colspan=1, rowspan=1)
    ax2.plot(ax1.x,vrefn_bjt)
    ax2.set_title('VREFN (BJT)')
    ax2.set_ylabel('VREFN [V]')

    ax3 = plt.subplot2grid((2,4), (0, 2), colspan=1, rowspan=1)
    ax3.plot(ax1.x,vcmi_bjt)
    ax3.set_title('VCMI (BJT)')
    ax3.set_ylabel('VCMI [V]')
    
    ax4 = plt.subplot2grid((2,4), (0, 3), colspan=1, rowspan=1)
    ax4.plot(ax1.x,vcmo_bjt)
    ax4.set_title('VCMO (BJT)')
    ax4.set_ylabel('VCMO [V]')
    
    ax5 = plt.subplot2grid((2,4), (1, 0), colspan=1, rowspan=1)
    ax5.plot(ax1.x,ibuff0_bjt)
    ax5.set_title('IBUFF0 (BJT)')
    ax5.set_ylabel('IBUFF0_5k [V]')
    ax5.set_xlabel('Setting Code')
    
    ax6 = plt.subplot2grid((2,4), (1, 1), colspan=1, rowspan=1)
    ax6.plot(ax1.x,ibuff1_bjt)
    ax6.set_title('IBUFF1 (BJT)')
    ax6.set_ylabel('IBUFF1_5k [V]')
    ax6.set_xlabel('Setting Code')
    
    ax7 = plt.subplot2grid((2,4), (1, 2), colspan=1, rowspan=1)
    ax7.plot(ax1.x,ivdac0_bjt)
    ax7.set_title('IDAC0 (BJT)')
    ax7.set_ylabel('IDAC0_5k [V]')
    ax7.set_xlabel('Setting Code')
    
    ax8 = plt.subplot2grid((2,4), (1, 3), colspan=1, rowspan=1)
    ax8.plot(ax1.x,ivdac1_bjt)
    ax8.set_title('IDAC1 (BJT)')
    ax8.set_ylabel('IDAC1_5k [V]')
    ax8.set_xlabel('Setting Code')
    
    plt.tight_layout()
    plt.savefig( ref_dir + "Reference_BJT"+ ".png" )
    plt.close()
    print("BJT Reference sweep plots successfully created")
    
    #Reference sweep plots: BJT
    fig = plt.figure(figsize=(18,4))
    ax1 = plt.subplot2grid((1,5), (0, 0), colspan=1, rowspan=1)
    ax1.x = (sweep-1)*np.arange(sweep)
    ax1.plot(ax1.x,vrefp_cmos)
    ax1.set_title('VREFP (CMOS)')
    ax1.set_ylabel('VREFP [V]')
    ax1.set_xlabel('Setting Code')
    
    ax2 = plt.subplot2grid((1,5), (0, 1), colspan=1, rowspan=1)
    ax2.plot(ax1.x,vrefn_cmos)
    ax2.set_title('VREFN (CMOS)')
    ax2.set_ylabel('VREFN [V]')
    ax2.set_xlabel('Setting Code')

    ax3 = plt.subplot2grid((1,5), (0, 2), colspan=1, rowspan=1)
    ax3.plot(ax1.x,vcmi_cmos)
    ax3.set_title('VCMI (CMOS)')
    ax3.set_ylabel('VCMI [V]')
    ax3.set_xlabel('Setting Code')
    
    ax4 = plt.subplot2grid((1,5), (0, 3), colspan=1, rowspan=1)
    ax4.plot(ax1.x,vcmo_cmos)
    ax4.set_title('VCMO (CMOS)')
    ax4.set_ylabel('VCMO [V]')
    ax4.set_xlabel('Setting Code')
    
    ax5 = plt.subplot2grid((1,5), (0, 4), colspan=1, rowspan=1)
    ax5.x = 3*np.arange(22)
    ax5.plot(ax5.x,ibuff_cmos)
    ax5.set_title('IBUFF (CMOS)')
    ax5.set_ylabel('IBUFF_5k [V]')
    ax5.set_xlabel('Setting Code')
    
    plt.tight_layout()
    plt.savefig( ref_dir + "Reference_CMOS"+ ".png" )
    plt.close()   
    print("CMOS Reference sweep plots successfully created")

def cali_chk():
    #BJT calibration weights
    ps.set_channel(1,2.8)
    time.sleep(5)
    flg_bjt_r = True
    cq.adc_cfg(adc_sdc="Bypass", adc_db="Bypass", adc_sha="Single-ended", adc_curr_src="BJT-sd", cali = "new weights", fn=ref_set_dir)
    reg, weight_bjt = cq.bc.adc_read_weights()
    record_weights(reg, weight_bjt,flg_bjt_r= True)
    
    #CMOS calibration weights
    ps.set_channel(1,2.5)
    time.sleep(5)
    flg_bjt_r = False
    cq.adc_cfg(adc_sdc="Bypass", adc_db="Bypass", adc_sha="Single-ended", adc_curr_src="CMOS-sd", cali = "new weights", fn=ref_set_dir)
    reg, weight_cmos = cq.bc.adc_read_weights()
    record_weights(reg, weight_cmos,flg_bjt_r=False)
    

def init_chns_table():
    #Create Channel Characterization CSV files: all relevant performance values for every channel
    #Record Worst DNL, Worst INL (best-fit method), ENOB, Noise (200 mV baseline), Noise (900 mv baseline)
    
    fields = ['Quantity', 'Channel 0', 'Channel 1', 'Channel 2', 'Channel 3','Channel 4', 'Channel 5', 'Channel 6', 'Channel 7']  
         
    #BJT reference
    filename = rawdir + "Channel_Characterization_BJT_ADC0.csv"         
    with open(filename, 'w', newline='') as csvfile: 
        csvwriter = csv.writer(csvfile) 
        csvwriter.writerow(fields)    
    csvfile.close()
    
    fields = ['Quantity', 'Channel 8', 'Channel 9', 'Channel 10', 'Channel 11','Channel 12', 'Channel 13', 'Channel 14', 'Channel 15'] 
    filename = rawdir + "Channel_Characterization_BJT_ADC1.csv"         
    with open(filename, 'w', newline='') as csvfile: 
        csvwriter = csv.writer(csvfile) 
        csvwriter.writerow(fields)    
    csvfile.close()     

    #CMOS reference
    filename = rawdir + "Channel_Characterization_CMOS_ADC0.csv"         
    with open(filename, 'w', newline='') as csvfile: 
        csvwriter = csv.writer(csvfile) 
        csvwriter.writerow(fields)    
    csvfile.close()
    
    fields = ['Quantity', 'Channel 8', 'Channel 9', 'Channel 10', 'Channel 11','Channel 12', 'Channel 13', 'Channel 14', 'Channel 15'] 
    filename = rawdir + "Channel_Characterization_CMOS_ADC1.csv"         
    with open(filename, 'w', newline='') as csvfile: 
        csvwriter = csv.writer(csvfile) 
        csvwriter.writerow(fields)    
    csvfile.close()                   

def init_system_500k():
    #Sampling frequency initialized: 500 kHz
    #0x05      ->  FPGA register for system frequency control
    #write 1   ->  SHA sampling frequency 500 kHz (4 Ms/s ADC)
    #write 0   ->  SHA sampling frequency 2 MHz (nominal, 16 Ms/s ADC)
    cq.bc.udp.write_reg_checked(0x05,1)
    print("Sampling frequency set: 500 kHz")

def init_system_2M():
    #Sampling frequency initialized: 500 kHz
    #0x05      ->  FPGA register for system frequency control
    #write 1   ->  SHA sampling frequency 500 kHz (4 Ms/s ADC)
    #write 0   ->  SHA sampling frequency 2 MHz (nominal, 16 Ms/s ADC)
    cq.bc.udp.write_reg_checked(0x05,0)
    print("Sampling frequency set: 2 MHz")

def init_logs():
    #Initialize logs
    #Status      ->  PASS as default, FAIL if initialization checkout fails. Every step of initialization checkout has a failure mode
    #Pass log    ->  Collects every successful test in the initialization checkout. Will printed out in final Summary (adc_only_pdf)
    #Error log   ->  If status = FAIL, collects and describes every unsuccessful test. If status FAIL, this will be printed out in final Summary (adc_only_pdf)
    cq.status("PASS")
    err_file = open("Error_Log.txt","w") 
    err_file.write("") 
    err_file.close()
    pass_file = open("Pass_Log.txt","w")
    pass_file.write("") 
    pass_file.close()
    print("clear")

def gen_output_dis():
    #Disable DS360 generator output
    gen.gen_init()
    gen.gen_set(out = "dis")


init_system_2M()
init_logs()
ps.ps_init()
pwr_chk()
cq.init_chk()
cq.uart_chk()
cq.i2c_chk()
cq.pattern_chk()
cq.regs_chk()
refs_plot()
cali_chk()
init_chns_table()

