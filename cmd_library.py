#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 17 16:54:11 2019

@author: shanshangao
"""
#import numpy as np
from brd_config import Brd_Config
import time
import numpy as np
from raw_data_decoder import raw_conv
import pickle
import os

#from udp import UDP 
#from adc_i2c_uart import COLDADC_tool
#
#from fpga_reg import FPGA_REG
#from fe_reg import FE_REG
#from user_defined import User_defined
#from adc_i2c_uart import COLDADC_tool
#from adc_reg import ADC_REG
#from frame import Frames
#import sys
#import time
#import math

class CMD_ACQ:
    def err_log(self, s):
        err_file = open("Error_Log.txt","a") #append mode 
        err_file.write(s) 
        err_file.close()
        
    def pass_log(self, s):
        pass_file = open("Pass_Log.txt","a") #append mode 
        pass_file.write(s) 
        pass_file.close()
        
    def status(self, s):
        stat_file = open("Status.txt","w") #write mode
        stat_file.write(s) 
        stat_file.close()

    def __init__(self):
        self.flg_bjt_r = True
        self.bc = Brd_Config()
        self.vp_vcmi = False
        self.vn_vcmi = False
        self.vm_vcmi = False
        self.vp_vcmo = False
        self.vn_vcmo = False
        self.vm_vcmo = False
        self.vp_vrefp = False
        self.vn_vrefp = False
        self.vm_vrefp = False
        self.vp_vrefn = False
        self.vn_vrefn = False
        self.vm_vrefn = False
        self.vrefp_voft = 0xe5
        self.vrefn_voft = 0x27
        self.vcmi_voft = 0x5c
        self.vcmo_voft = 0x87

#        if (env == "RT"):
##for chip soldered on board C2
##                vrefp_voft = 0xe1#0xe5#0xe0#0xde#0xe4#0xe1#0xf0#0xf8#0xe4
##                vrefn_voft = 0x27#0x25#0x21#0x26#0x24#0x27#0x08#0x10#0x24
##                vcmi_voft = 0x60#0x5c#0x60#0x50#0x60
##                vcmo_voft = 0x82
#            self.vrefp_voft = 0xe5#0xe5#0xe0#0xde#0xe4#0xe1#0xf0#0xf8#0xe4
#            self.vrefn_voft = 0x27#0x25#0x21#0x26#0x24#0x27#0x08#0x10#0x24
#            self.vcmi_voft = 0x5c#0x60#0x5c#0x60#0x50#0x60
#            self.vcmo_voft = 0x87#0x82
#        else:
#            self.vrefp_voft = 0xd7#0xdc#0xdc#0xeb#0xf1
#            self.vrefn_voft = 0x23#0x23#0x26#0x47#0x2b#0x29
#            self.vcmi_voft = 0x60#0x50#0x64#0x7e#0x64#0x65
#            self.vcmo_voft = 0x80#0x78#0x7d#0x9d#0x7c#0x8d



    def init_chk(self):
        #Hard reset ADC -> Read register 0 -> Soft reset (necessary for default page 2 registers, recently discovered problem)
        self.bc.Acq_start_stop(0)
        print ("ADC hard reset after power on")
        self.bc.adc.hard_reset()
        init_str = self.bc.adc_read_reg(0)
        if (init_str != '0x52'):
            self.status("FAIL")
            self.err_log("Initialization check failed. Read/Write not working correctly. \n")  
        self.bc.adc_soft_reset()
            
    def i2c_chk(self):
        #Read and Write register with I2C
        self.bc.Acq_start_stop(0)
        self.bc.adc_i2c_uart("I2C")
        self.bc.adc_write_reg(1, 0x22)
        i2c_write = self.bc.adc_read_reg(1)
        if (i2c_write != '0x22'):
            self.status("FAIL")
            self.err_log("I2C check failed. Read/Write not working correctly. \n") 
        else:
            print("I2C Connection works")
            self.pass_log("I2C Read/Write: PASS \n")

    def uart_chk(self):
        #Read and Write register with UART
        self.bc.Acq_start_stop(0)
        self.bc.adc_i2c_uart("UART")
        self.bc.adc_write_reg(1, 0x22)
        uart_write = self.bc.adc_read_reg(1)
        if (uart_write != '0x22'):
            self.status("FAIL")
            self.err_log("UART check failed. Read/Write not working correctly. \n")   
        else:
            print("UART Connection works")
            self.pass_log("UART Read/Write: PASS \n")   
    
    def pattern_chk(self):
        #Check ADC0 and ADC1 default test patterns
        self.bc.adc.hard_reset()
        adc0_h = self.bc.adc_read_reg(52)
        adc0_l = self.bc.adc_read_reg(51)
        if (adc0_h != '0xab' or adc0_l != '0xcd'):
            self.status("FAIL")
            self.err_log("ADC0 Configuration Pattern: unexpected value \n")
        adc1_h = self.bc.adc_read_reg(54)
        adc1_l = self.bc.adc_read_reg(53)
        if (adc1_h != '0x12' or adc1_l != '0x34'):
            self.status("FAIL")
            self.err_log("ADC1 Configuration Pattern: unexpected value \n")
        
        else:
            print("ADC configuration pattern is good")
            self.pass_log("Configuration pattern: PASS \n") 
    
    def regs_chk(self):
        self.bc.adc.hard_reset()
        reg = []
        flg = 0
        #Check page 1 registers
        default = [0x52, 0x00, 0x00, 0x00, 0x33, 0x33, 0x33, 0x33, 0x0a, 0x00,
                   0xfa, 0x3a, 0x9a, 0x73, 0xff, 0x99, 0x99, 0x99, 0x99, 0x00,
                   0x00, 0x00, 0x00, 0x30, 0x00, 0x00, 0x00, 0x00, 0x0c, 0x27,
                   0x27, 0x00, 0x7f, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                   0x00, 0x00, 0xa5, 0xca, 0x00, 0x00, 0x00, 0x00, 0x07, 0x00,
                   0x00, 0xcd, 0xab, 0x34, 0x12]
        for i in range(0,50):
            reg.append(int((self.bc.adc_read_reg(i)),16))
            if(reg[i] != default[i]):
                #If non-default register value is found, Status = FAIL and report issue in Error Log
                self.status("FAIL")
                self.err_log("Register %d (page 1) value %x1 instead of default value %d \n"%(i, reg[i], default[i]))
                flg = 1
        #Check page 2 registers
        reg2 = []
        default2 = [0x04,0xff,0x00] #default registers are NOT the ones reported in datasheet
        for i in range(1,4):
            reg2.append(self.bc.adc.I2C_read(self.bc.chip_id,2,i))
            if(reg2[i-1] != default2[i-1]):
                self.status("FAIL")
                self.err_log("Register %d (page 2) value %s instead of default value %d \n"%(i, reg2[i-1], default2[i-1]))
                flg = 1
        #If everything is default, send PASS message
        if (flg == 0):
            print("Default registers are good")
            self.pass_log("Default registers: PASS \n")
    
    def refs_chk(self):
        #Sweeps reference voltages and currents
        avgs = 1
        if (self.flg_bjt_r):
            self.bc.adc_ref_vol_src("BJT")
            self.bc.adc_bias_curr_src("BJT")
            vrefp_bjt = []
            vrefn_bjt = []
            vcmi_bjt = []
            vcmo_bjt = []
            ibuff0_bjt = []
            ibuff1_bjt = []
            ivdac0_bjt = []
            ivdac1_bjt = []
            vrefp_ioft = 1
            vrefn_ioft = 1
            vcmi_ioft = 1
            vcmo_ioft = 1
            vbgr  = self.ref_vmon(vmon = "VBGR")
            #Checks VBGR normal value
            if(vbgr > 1.3 or vbgr < 1.1):
                self.status("FAIL")
                self.err_log("Bandgap Reference out of expected range: VBGR = %0.3f \n"%(vbgr))
            else:
                self.pass_log("Bandgap reference: PASS \n") 
            self.bc.adc_set_ioffset(vrefp_ioft, vrefn_ioft, vcmo_ioft, vcmi_ioft)
            for j in range (avgs):
                if(j==0):
                    #Codes between 0 and 256. Take data every 15 
                    for i in range (0,256,15):
                        #Set and collect IBUFF and IDAC values
                        self.bc.adc_set_curr_ibuff(i, i)
                        ibuff0_bjt.append(self.bjt_ref_aux("ibuff0_5k","AUX_ISOURCE"))
                        ibuff1_bjt.append(self.bjt_ref_aux("ibuff1_5k","AUX_ISOURCE"))
                        self.bc.adc_set_curr_vdac(i, i)
                        ivdac0_bjt.append(self.bjt_ref_aux("Vdac0_5k","AUX_ISOURCE"))
                        ivdac1_bjt.append(self.bjt_ref_aux("Vdac1_5k","AUX_ISOURCE"))    
                        #Set and collect VREFs values
                        self.bc.adc_set_vrefs(i, i, i, i)
                        vcmi_i, vcmo_i, vrefp_i, vrefn_i = self.ref_vmons()
                        print(i, vcmi_i, vcmo_i, vrefp_i, vrefn_i)
                        vcmi_bjt.append(vcmi_i)
                        vcmo_bjt.append(vcmo_i)
                        vrefp_bjt.append(vrefp_i)
                        vrefn_bjt.append(vrefn_i)

                else:
                    #Only for avgs > 1
                    for i in range (0,256,15):
                        self.bc.adc_set_vrefs(i, i, i, i)
                        time.sleep(0.1)
                        vcmi_i, vcmo_i, vrefp_i, vrefn_i = self.ref_vmons()
                        vcmi_bjt[i] += vcmi_i
                        vcmo_bjt[i] += vcmo_i
                        vrefp_bjt[i] += vrefp_i
                        vrefn_bjt[i] += vrefn_i
                        self.bc.adc_set_curr_ibuff(i, i)
                        ibuff0_bjt[i] += self.bjt_ref_aux("ibuff0_5k","AUX_ISOURCE")
                        ibuff1_bjt[i] += self.bjt_ref_aux("ibuff1_5k","AUX_ISOURCE")
                        self.bc.adc_set_curr_vdac(i, i)
                        ivdac0_bjt[i] += self.bjt_ref_aux("Vdac0_5k","AUX_ISOURCE")
                        ivdac1_bjt[i] += self.bjt_ref_aux("Vdac1_5k","AUX_ISOURCE")     
            vrefp_bjt[:] = [x / avgs for x in vrefp_bjt]
            vrefn_bjt[:] = [x / avgs for x in vrefn_bjt]
            vcmi_bjt[:] = [x / avgs for x in vcmi_bjt]
            vcmo_bjt[:] = [x / avgs for x in vcmo_bjt]
            ibuff0_bjt[:] = [x / avgs for x in ibuff0_bjt]
            ibuff1_bjt[:] = [x / avgs for x in ibuff1_bjt]
            ivdac0_bjt[:] = [x / avgs for x in ivdac0_bjt]
            ivdac1_bjt[:] = [x / avgs for x in ivdac1_bjt]
            return (vrefp_bjt, vrefn_bjt, vcmi_bjt, vcmo_bjt, ibuff0_bjt, ibuff1_bjt, ivdac0_bjt, ivdac1_bjt)
            
        else:
            #Repeat same procedure for CMOS references
            self.bc.adc_ref_vol_src("CMOS")
            self.bc.adc_bias_curr_src("CMOS_INTR")
            vrefp_cmos = []
            vrefn_cmos = []
            vcmi_cmos = []
            vcmo_cmos = []
            ibuff_cmos = []
            iref_trim = 45
            self.bc.adc_set_cmos_iref_trim(iref_trim)
            for j in range (avgs):
                if (j==0):
                    for i in range (0,256,15):
                        self.bc.adc_set_cmos_vrefs(i, i, i, i)
                        vcmi_i, vcmo_i, vrefp_i, vrefn_i = self.ref_vmons()
                        vcmi_cmos.append(vcmi_i)
                        vcmo_cmos.append(vcmo_i)
                        vrefp_cmos.append(vrefp_i)
                        vrefn_cmos.append(vrefn_i)
                    for k in range (0, 64, 3):
                        print(k)
                        self.bc.adc_set_cmos_ibuff(k, k)
                        ibuff_cmos.append(self.ref_imon(imon = "IBUFF_CMOS"))     
                else:
                    for i in range (0,256,15):
                        self.bc.adc_set_cmos_vrefs(i, i, i, i)
                        vcmi_i, vcmo_i, vrefp_i, vrefn_i = self.ref_vmons()
                        vcmi_cmos[i] += vcmi_i
                        vcmo_cmos[i] += vcmo_i
                        vrefp_cmos[i] += vrefp_i
                        vrefn_cmos[i] += vrefn_i
                    for k in range (0, 64, 3):
                        self.bc.adc_set_cmos_ibuff(k, k)
                        ibuff_cmos[k]  += self.ref_imon(imon = "IBUFF_CMOS")       
            vrefp_cmos[:] = [x / avgs for x in vrefp_cmos]
            vrefn_cmos[:] = [x / avgs for x in vrefn_cmos]
            vcmi_cmos[:] = [x / avgs for x in vcmi_cmos]
            vcmo_cmos[:] = [x / avgs for x in vcmo_cmos]
            ibuff_cmos[:] = [x / avgs for x in ibuff_cmos]
            return (vrefp_cmos, vrefn_cmos, vcmi_cmos, vcmo_cmos, ibuff_cmos)

    def find_ref(self, vreg, vp, vn, vm, vread, vset  ):
        if (vp and vn):
            pass
        else:
            if (vread > vset + 0.01):
                vreg -=1
                vp = True
            elif (vread <  vset - 0.01):
                vreg += 1
                vp = vp
                vn = True
            else:
                vreg = vreg
                vm = True
        return vreg, vp, vn, vm
   
    def ref_set_find(self,  fn = "" ):
        if (self.flg_bjt_r):

            self.bc.adc_ref_vol_src("BJT")
            print ("Internal BJT voltage references are used")
            self.bc.adc_bias_curr_src("BJT")
            print ("Bias currents come from BJT-based references")
            vrefp_ioft = 1
            vrefn_ioft = 1
            vcmi_ioft = 1
            vcmo_ioft = 1
            self.bc.adc_set_ioffset(vrefp_ioft, vrefn_ioft, vcmo_ioft, vcmi_ioft)
            ibuff0_15 = 0x99
            ibuff1_16 = 0x99
            ivdac0_17 = 0x99
            ivdac1_18 = 0x99
            self.bc.adc_set_curr_ibuff(ibuff0_15, ibuff1_16)
            self.bc.adc_set_curr_vdac(ivdac0_17, ivdac1_18)
            print ("BJT current source for input buffer and VDAC is set to default values!")

            print ("BJT reference is being calibrated")
            self.vp_vcmi = False
            self.vn_vcmi = False
            self.vm_vcmi = False
            self.vp_vcmo = False
            self.vn_vcmo = False
            self.vm_vcmo = False
            self.vp_vrefp = False
            self.vn_vrefp = False
            self.vm_vrefp = False
            self.vp_vrefn = False
            self.vn_vrefn = False
            self.vm_vrefn = False
            self.vrefp_voft = 0xe8
            self.vrefn_voft = 0x20
            self.vcmi_voft = 0x60
            self.vcmo_voft = 0x88
            while (True):
                vrefp_f = False
                vrefn_f = False
                vcmi_f = False
                vcmo_f = False

                self.bc.adc_set_vrefs(self.vrefp_voft, self.vrefn_voft, self.vcmo_voft, self.vcmi_voft )
                vbgr, vcmi, vcmo, vrefp, vrefn, vssa = self.all_ref_vmons( )
                if not ( (self.vp_vrefp and self.vn_vrefp ) or self.vm_vrefp ):
                    self.vrefp_voft, self.vp_vrefp, self.vn_vrefp, self.vm_vrefp = \
                            self.find_ref(self.vrefp_voft, self.vp_vrefp, self.vn_vrefp, self.vm_vrefp, vread=vrefp, vset=1.95 )
                else:
                    vrefp_f = True
                if not ( (self.vp_vrefn and self.vn_vrefn ) or self.vm_vrefn ):
                    self.vrefn_voft, self.vp_vrefn, self.vn_vrefn, self.vm_vrefn = \
                            self.find_ref(self.vrefn_voft, self.vp_vrefn, self.vn_vrefn, self.vm_vrefn, vread=vrefn, vset=0.45 )
                else:
                    vrefn_f = True
                if not ( (self.vp_vcmi and self.vn_vcmi ) or self.vm_vcmi ):
                    self.vcmi_voft, self.vp_vcmi, self.vn_vcmi, self.vm_vcmi = \
                            self.find_ref(self.vcmi_voft, self.vp_vcmi, self.vn_vcmi, self.vm_vcmi, vread=vcmi, vset=0.90 )
                else:
                    vcmi_f = True
                if not ( (self.vp_vcmi and self.vn_vcmi ) or self.vm_vcmo ):
                    self.vcmo_voft, self.vp_vcmo, self.vn_vcmo, self.vm_vcmo = \
                            self.find_ref(self.vcmo_voft, self.vp_vcmo, self.vn_vcmo, self.vm_vcmo, vread=vcmo, vset=1.20 )
                else:
                    vcmo_f = True

                print ("VREFP = %.3f, VREFN = %.3f, VCMI = %.3f, VCMO = %.3f"%(vrefp, vrefn, vcmi, vcmo))
                if vrefp_f and vrefn_f and vcmi_f and vcmo_f:
                    break

            with open(fn + "bjt.bjt", 'wb+') as f:
                vref_regs = [self.vrefp_voft, self.vrefn_voft, self.vcmo_voft, self.vcmi_voft]
                vref_values = [vbgr, vcmi, vcmo, vrefp, vrefn, vssa ]
                pickle.dump([vref_regs, vref_values] , f)

        else:
            self.bc.adc_ref_vol_src("CMOS")
            print ("CMOS voltage references are used")
            self.bc.adc_bias_curr_src("CMOS_INTR")
            print ("Bias currents come from CMOS-basedreference with internal R")  
            iref_trim = 45
            self.bc.adc_set_cmos_iref_trim(iref_trim)
            print ("Set vt-reference current to 45uA (correction to default value)!") 
            ibuff0_cmos = 0x27
            ibuff1_cmos = 0x27
            self.bc.adc_set_cmos_ibuff(ibuff0_cmos, ibuff1_cmos)
            print ("CMOS bias source for the input buffer is set!") 

            print ("CMOS reference is being calibrated !") 
            self.vp_vcmi = False
            self.vn_vcmi = False
            self.vm_vcmi = False
            self.vp_vcmo = False
            self.vn_vcmo = False
            self.vm_vcmo = False
            self.vp_vrefp = False
            self.vn_vrefp = False
            self.vm_vrefp = False
            self.vp_vrefn = False
            self.vn_vrefn = False
            self.vm_vrefn = False
            self.vrefp_voft = 0xd8
            self.vrefn_voft = 0x28
            self.vcmi_voft = 0x60
            self.vcmo_voft = 0x80
            while (True):
                self.bc.adc_set_cmos_vrefs(self.vrefp_voft, self.vrefn_voft, self.vcmi_voft, self.vcmo_voft)
                vbgr, vcmi, vcmo, vrefp, vrefn, vssa = self.all_ref_vmons( )
                vrefp_f = False
                vrefn_f = False
                vcmi_f = False
                vcmo_f = False
                if not ( (self.vp_vrefp and self.vn_vrefp ) or self.vm_vrefp ):
                    self.vrefp_voft, self.vp_vrefp, self.vn_vrefp, self.vm_vrefp = \
                            self.find_ref(self.vrefp_voft, self.vp_vrefp, self.vn_vrefp, self.vm_vrefp, vread=vrefp, vset=1.95 )
                else:
                    vrefp_f = True
                if not ( (self.vp_vrefn and self.vn_vrefn ) or self.vm_vrefn ):
                    self.vrefn_voft, self.vp_vrefn, self.vn_vrefn, self.vm_vrefn = \
                            self.find_ref(self.vrefn_voft, self.vp_vrefn, self.vn_vrefn, self.vm_vrefn, vread=vrefn, vset=0.45 )
                else:
                    vrefn_f = True
                if not ( (self.vp_vcmi and self.vn_vcmi ) or self.vm_vcmi ):
                    self.vcmi_voft, self.vp_vcmi, self.vn_vcmi, self.vm_vcmi = \
                            self.find_ref(self.vcmi_voft, self.vp_vcmi, self.vn_vcmi, self.vm_vcmi, vread=vcmi, vset=0.90 )
                else:
                    vcmi_f = True
                if not ( (self.vp_vcmi and self.vn_vcmi ) or self.vm_vcmo ):
                    self.vcmo_voft, self.vp_vcmo, self.vn_vcmo, self.vm_vcmo = \
                            self.find_ref(self.vcmo_voft, self.vp_vcmo, self.vn_vcmo, self.vm_vcmo, vread=vcmo, vset=1.20 )
                else:
                    vcmo_f = True

                print ("VREFP = %.3f, VREFN = %.3f, VCMI = %.3f, VCMO = %.3f"%(vrefp, vrefn, vcmi, vcmo))
                if vrefp_f and vrefn_f and vcmi_f and vcmo_f:
                    break
            with open(fn + "cmos.cmos", 'wb+') as f:
                vref_regs = [self.vrefp_voft, self.vrefn_voft, self.vcmo_voft, self.vcmi_voft]
                vref_values = [vbgr, vcmi, vcmo, vrefp, vrefn, vssa ]
                pickle.dump([vref_regs, vref_values] , f)
  
    def ref_set(self, fn ):
        if (self.flg_bjt_r):
            self.bc.adc_ref_vol_src("BJT")
            print ("Internal BJT voltage references are used")
            self.bc.adc_bias_curr_src("BJT")
            print ("Bias currents come from BJT-based references")
            vrefp_ioft = 1
            vrefn_ioft = 1
            vcmi_ioft = 1
            vcmo_ioft = 1
            self.bc.adc_set_ioffset(vrefp_ioft, vrefn_ioft, vcmo_ioft, vcmi_ioft)

            print ("BJT reference is set to pre-calibrated values!")
            with open(fn+"bjt.bjt", 'rb') as f:
                vref_regs, vref_values = pickle.load( f)
            self.vrefp_voft, self.vrefn_voft, self.vcmo_voft, self.vcmi_voft = vref_regs
            self.bc.adc_set_vrefs(self.vrefp_voft, self.vrefn_voft, self.vcmo_voft, self.vcmi_voft )

            print ("BJT current source for input buffer and VDAC is set to default values!")
            ibuff0_15 = 0x99
            ibuff1_16 = 0x99
            ivdac0_17 = 0x99
            ivdac1_18 = 0x99
            self.bc.adc_set_curr_ibuff(ibuff0_15, ibuff1_16)
            self.bc.adc_set_curr_vdac(ivdac0_17, ivdac1_18)
        else:
            self.bc.adc_ref_vol_src("CMOS")
            print ("CMOS voltage references are used")
            print ("Bias currents come from CMOS-basedreference with internal R")  
            self.bc.adc_bias_curr_src("CMOS_INTR")

            print ("CMOS reference is set to pre-calibrated values!") 
            with open(fn+"cmos.cmos", 'rb') as f:
                vref_regs, vref_values = pickle.load( f)
            self.vrefp_voft, self.vrefn_voft, self.vcmo_voft, self.vcmi_voft = vref_regs
            self.bc.adc_set_cmos_vrefs(self.vrefp_voft, self.vrefn_voft, self.vcmi_voft, self.vcmo_voft)

            print ("Set vt-reference current to 45uA (correction to default value)!") 
            iref_trim = 45
            self.bc.adc_set_cmos_iref_trim(iref_trim)

            print ("CMOS bias source for the input buffer is set!") 
            ibuff0_cmos = 0x27
            ibuff1_cmos = 0x27
            self.bc.adc_set_cmos_ibuff(ibuff0_cmos, ibuff1_cmos)

    def bjt_ref_aux(self, mon_src = "VREFP", mux_src = "AUX_VOLTAGE", avg_points =5  ):
        self.bc.cots_adc_bjt_mon_src(src = mon_src)
        self.bc.cots_adc_mux_mon_src(src = mux_src )
        self.bc.cots_adc_data(avr = 2)
        val = self.bc.cots_adc_data(avr = avg_points)
#        print ("MUX = %s, %s = %f"%(mux_src, mon_src, val))
        return val

    def all_bjt_ref_auxs(self ):
        vref  = self.bjt_ref_aux(mon_src = "VREF_ext",  mux_src = "AUX_VOLTAGE")
        vrefn = self.bjt_ref_aux(mon_src = "VREFN",     mux_src = "AUX_VOLTAGE")
        vrefp = self.bjt_ref_aux(mon_src = "VREFP",     mux_src = "AUX_VOLTAGE")
        vcmi  = self.bjt_ref_aux(mon_src = "VCMI",      mux_src = "AUX_VOLTAGE")
        vcmo  = self.bjt_ref_aux(mon_src = "VCMO",      mux_src = "AUX_VOLTAGE")
        vbgr  = self.bjt_ref_aux(mon_src = "VBGR_1.2V", mux_src = "AUX_VOLTAGE")
        vdac0_5k   = self.bjt_ref_aux(mon_src = "Vdac0_5k",  mux_src = "AUX_ISOURCE")
        vdac1_5k   = self.bjt_ref_aux(mon_src = "Vdac1_5k",  mux_src = "AUX_ISOURCE")
        ibuff0_5k  = self.bjt_ref_aux(mon_src = "ibuff0_5k", mux_src = "AUX_ISOURCE")
        ibuff1_5k  = self.bjt_ref_aux(mon_src = "ibuff1_5k", mux_src = "AUX_ISOURCE")
        isink_adc1_5k  = self.bjt_ref_aux(mon_src = "Isink_adc1_5k", mux_src = "AUX_ISINK")
        isink_adc0_5k  = self.bjt_ref_aux(mon_src = "Isink_adc0_5k", mux_src = "AUX_ISINK")
        isink_sha1_5k  = self.bjt_ref_aux(mon_src = "Isink_sha1_5k", mux_src = "AUX_ISINK")
        isink_sha0_5k  = self.bjt_ref_aux(mon_src = "Isink_sha0_5k", mux_src = "AUX_ISINK")
        isink_refbuf0_5k  = self.bjt_ref_aux(mon_src = "Isink_refbuf0_5k", mux_src = "AUX_ISINK")
        isink_refbuf1_5k  = self.bjt_ref_aux(mon_src = "Isink_refbuf1_5k", mux_src = "AUX_ISINK")
        return (vref, vrefn, vrefp, vcmi, vcmo, vbgr, vdac0_5k, vdac1_5k, ibuff0_5k, ibuff1_5k, 
                isink_adc1_5k, isink_adc0_5k, isink_sha1_5k, isink_sha0_5k, isink_refbuf0_5k, isink_refbuf1_5k )

    def ref_vmon(self, vmon = "VBGR", avg_points =5  ):
        self.bc.cots_adc_mux_mon_src(src = "VOLTAGE_MON")
        self.bc.cost_adc_v_mon_ena(1)
        self.bc.cost_adc_v_mon_select(vmon)
        self.bc.cots_adc_data(avr = 2)
        val = self.bc.cots_adc_data(avr = avg_points)
        self.bc.cost_adc_v_mon_ena(0)
#        print ("MUX = VOLTAGE_MON, %s = %f"%( vmon, val))
        return val

    def all_ref_vmons(self ):
        vbgr  = self.ref_vmon(vmon = "VBGR"  )
        vcmi  = self.ref_vmon(vmon = "VCMI"  )
        vcmo  = self.ref_vmon(vmon = "VCMO"  )
        vrefp = self.ref_vmon(vmon = "VREFP" )
        vrefn = self.ref_vmon(vmon = "VREFN" )
        vssa  = self.ref_vmon(vmon = "VSSA"  )
        return (vbgr, vcmi, vcmo, vrefp, vrefn, vssa)
    
    def ref_vmons(self ):
        vcmi  = self.ref_vmon(vmon = "VCMI"  )
        vcmo  = self.ref_vmon(vmon = "VCMO"  )
        vrefp = self.ref_vmon(vmon = "VREFP" )
        vrefn = self.ref_vmon(vmon = "VREFN" )
        return (vcmi, vcmo, vrefp, vrefn)

    def ref_imon(self, imon = "ICMOS_REF_5k", avg_points =5  ):
        self.bc.cots_adc_mux_mon_src(src = "CURRENT_MON")
        self.bc.cost_adc_i_mon_ena(1)
        self.bc.cost_adc_i_mon_select(imon)
        self.bc.cots_adc_data(avr = 2)
        val = self.bc.cots_adc_data(avr = avg_points)
        self.bc.cost_adc_i_mon_ena(0)
#        print ("MUX = CURRENT_MON, %s = %f"%( imon, val))
        return val

    def all_ref_imons(self ):
        icmos_ref_5k = self.ref_imon(imon = "ICMOS_REF_5k" )
        isha0_5k     = self.ref_imon(imon = "ISHA0_5k" )
        iadc0_5k     = self.ref_imon(imon = "IADC0_5k" )
        isha1_5k     = self.ref_imon(imon = "ISHA1_5k" )
        iadc1_5k     = self.ref_imon(imon = "IADC1_5k" )
        ibuff_cmos   = self.ref_imon(imon = "IBUFF_CMOS" )
        iref_5k      = self.ref_imon(imon = "IREF_5k" )
        irefbuffer0  = self.ref_imon(imon = "IREFBUFFER0" )
        return (icmos_ref_5k, isha0_5k, iadc0_5k, isha1_5k, iadc1_5k, ibuff_cmos, iref_5k, irefbuffer0 )


    def Converter_Config(self, edge_sel = "Normal", out_format = "two-complement", 
                         adc_sync_mode ="Normal", adc_test_input = "Normal", 
                         adc_output_sel = "cali_ADCdata", adc_bias_uA = 50):
        self.bc.adc_edge_select(mode = edge_sel)
        self.bc.adc_outputformat(oformat = out_format)
        self.bc.adc_sync_mode(mode = adc_sync_mode)
        self.bc.adc_test_input(mode = adc_test_input)
        self.bc.adc_output_select(option = adc_output_sel)
        self.bc.adc_set_adc_bias(val = adc_bias_uA)
        
    def Input_buffer_cfg( self, sdc = "Bypass", db = "Bypass", sha = "Single-ended", curr_src = "BJT-sd"):        
        self.bc.adc_sdc_select(sdc)
        self.bc.adc_db_select(db)
        if (sha == "Single-ended"):
            self.bc.adc_sha_input(1)
        else:
            self.bc.adc_sha_input(0)
        self.bc.adc_ibuff_ctrl(curr_src)      
    
    def get_adcdata(self, PktNum=128, saveraw = False, fn = "" ):
        self.bc.Acq_start_stop(1)
        rawdata = self.bc.udp.get_pure_rawdata(PktNum+1000 )
        if (saveraw):
            with open(fn, 'wb') as f:
                pickle.dump(rawdata, f)
        self.bc.Acq_start_stop(0)
        chns = raw_conv(rawdata, PktNum)[0]
#        self.bc.Acq_start_stop(1)
#        rawdata = self.bc.get_data(PktNum,1, Jumbo="Jumbo") #packet check
#        self.bc.Acq_start_stop(0)
#        frames_inst = Frames(PktNum,rawdata)     
#        frames = frames_inst.packets()
#        #Change it to emit all 16 channels data 
#        chns=[[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]] #16-bit
#        for i in range(PktNum):
#            for j in range(16): #16 channels
#                chns[j].append(frames[i].ADCdata[j]) 
        return chns 
    
    def get_adcdata_raw(self, PktNum=128 ):
        self.bc.Acq_start_stop(1)
        rawdata = self.bc.udp.get_pure_rawdata(PktNum+1000 )
        self.bc.Acq_start_stop(0)
        chns = raw_conv(rawdata, PktNum)[0]
#        rawdata = self.bc.get_data(PktNum,1, Jumbo="Jumbo") #packet check
#        return rawdata
        return chns

    def chn_order_sync(self, PktNum=128 ):  
        print ("Starting ADC physical channel and logical channel mapping...")
        woc_f = False
        for chn_order in range(0,32,4):
            self.bc.adc_load_pattern_0(0x01, 0x01)
            self.bc.adc_load_pattern_1(0x01, 0x01)
            self.bc.adc_framemarker_shift (num = chn_order)
            self.bc.adc_test_data_mode(mode = "Test Pattern")
            chns = self.get_adcdata(PktNum=128)
            nibble_sync_f = True
            for chndata in chns:
                if (chndata[1]&0xFFFF) != 0x0101:
                    nibble_sync_f = False
                    break
            if nibble_sync_f:
                self.bc.adc_test_data_mode(mode = "Normal")
                time.sleep(0.01)
                chns = self.get_adcdata(PktNum=128)
                for i in range(10):
                    chns = self.get_adcdata(PktNum=128)
                    if(( (chns[0][1] & 0xFFFF) > 0xD000) and 
                       ( (chns[1][1] & 0xFFFF) > 0x5000) and  ((chns[1][1] &0xFFFF)  < 0xD000) and
                       ( (chns[2][1] & 0xFFFF) < 0x5000) and 
                       ( (chns[3][1] & 0xFFFF) > 0x5000) and  ((chns[2][1] &0xFFFF)  < 0xD000) and            
                       ( (chns[4][1] & 0xFFFF) > 0x5000) and  ((chns[4][1] &0xFFFF)  < 0xD000) and               
                       ( (chns[5][1] & 0xFFFF) > 0x5000) and  ((chns[5][1] &0xFFFF)  < 0xD000) and               
                       ( (chns[6][1] & 0xFFFF) > 0x5000) and  ((chns[6][1] &0xFFFF)  < 0xD000) and               
                       ( (chns[7][1] & 0xFFFF) > 0x5000) and  ((chns[7][1] &0xFFFF)  < 0xD000) and               
                       ( (chns[8][1] & 0xFFFF) > 0xD000) and 
                       ( (chns[9][1] & 0xFFFF) > 0x5000) and  ((chns[9][1] &0xFFFF)  < 0xD000) and
                       ( (chns[10][1]& 0xFFFF) < 0x5000) and  
                       ( (chns[11][1]& 0xFFFF) > 0x5000) and  ((chns[10][1] &0xFFFF) < 0xD000) and            
                       ( (chns[12][1]& 0xFFFF) > 0x5000) and  ((chns[12][1] &0xFFFF) < 0xD000) and               
                       ( (chns[13][1]& 0xFFFF) > 0x5000) and  ((chns[13][1] &0xFFFF) < 0xD000) and               
                       ( (chns[14][1]& 0xFFFF) > 0x5000) and  ((chns[14][1] &0xFFFF) < 0xD000) and               
                       ( (chns[15][1]& 0xFFFF) > 0x5000) and  ((chns[15][1] &0xFFFF) < 0xD000) ):              
                        woc_f = True
                    else:
                        woc_f = False
                        break
                if woc_f == True:
                    print ("ADC chn order is %d"%chn_order)
                    print ("ADC physical channel and logical channel mapping is done")
                    break
            else:
                woc_f = False
                pass
        if(woc_f == False):
            self.status("FAIL")
            self.err_log("ADC output synchronization failed \n")
        return woc_f

            
    def fe_cfg(self,sts=16*[0], snc=16*[0], sg=16*[3], st=16*[2], sbf = 16*[0], sdc = 0, sdacsw=0, fpga_dac=0,asic_dac=0, delay=10, period=200, width=0xa00 ):  
        self.bc.sts = sts
        self.bc.snc = snc
        self.bc.sg  = sg 
        self.bc.st  = st 
        self.bc.sbf = sbf #buffer on
        self.bc.sdc = sdc #FE AC
        self.bc.sdacsw = sdacsw
        self.bc.sdac = asic_dac
        self.bc.fe_spi_config()
        if sdacsw == 0:
            mode = "RMS"
        elif sdacsw == 1:
            mode = "External"
        elif sdacsw == 2: 
            mode = "Internal"
        self.bc.fe_pulse_config(mode)
        self.bc.fe_fpga_dac(fpga_dac)
        self.bc.fe_pulse_param(delay, period, width)


    def adc_cfg(self, adc_sdc="Bypass", adc_db="Bypass", adc_sha="Single-Ended", adc_curr_src="BJT-sd",  cali = "new weights", fn = ""):
        #default BJT reference
        woc_f = False
        while(woc_f==False):
            self.init_chk()
            self.ref_set(fn)
            time.sleep(1)
            self.Input_buffer_cfg(sdc = adc_sdc, db = adc_db, sha = adc_sha, curr_src = adc_curr_src)      
            #self.Input_buffer_cfg(sdc = "On", db = "Bypass", sha = "Diff", curr_src = "BJT-sd")      
            self.bc.adc_sha_clk_sel(mode = "internal")
            self.Converter_Config(edge_sel = "Normal", out_format = "offset binary", 
                                 adc_sync_mode ="Analog pattern", adc_test_input = "Normal", 
                                 adc_output_sel = "cali_ADCdata", adc_bias_uA = 50)
            self.bc.udp.clr_server_buf()
            woc_f = self.chn_order_sync()
        
        self.Converter_Config(edge_sel = "Normal", out_format = "two-complement", 
                                 adc_sync_mode ="Normal", adc_test_input = "Normal", 
                                 adc_output_sel = "cali_ADCdata", adc_bias_uA = 50)
        
        if(cali == "new weights"):
            print ("Manual Calibration starting, wait...")
            self.bc.udp.clr_server_buf()
            self.bc.adc_autocali(avr=20000,saveflag="undef")
            self.Converter_Config(edge_sel = "Normal", out_format = "offset binary", 
                                     adc_sync_mode ="Normal", adc_test_input = "Normal", 
                                     adc_output_sel = "cali_ADCdata", adc_bias_uA = 50)
            print ("Manual Calibration is done, back to normal")

    def adc_cfg_init(self, adc_sdc="Bypass", adc_db="Bypass", adc_sha="Single-Ended", adc_curr_src="BJT-sd", fn = "" ): 
        self.init_chk()
        time.sleep(1)
        self.Input_buffer_cfg(sdc = adc_sdc, db = adc_db, sha = adc_sha, curr_src = adc_curr_src)         
        if (self.flg_bjt_r):
            fp = fn + "/bjt.bjt"
        else:
            fp = fn + "/cmos.cmos"
        if (not os.path.isfile(fp)):
            self.ref_set_find(fn)
        self.ref_set(fn)
        self.bc.adc_sha_clk_sel(mode = "internal")
        self.Converter_Config(edge_sel = "Normal", out_format = "offset binary", 
                                     adc_sync_mode ="Normal", adc_test_input = "Normal", 
                                     adc_output_sel = "cali_ADCdata", adc_bias_uA = 50)
            
#cq = CMD_ACQ() 
#cq.adc_cfg(adc_sdc="Bypass", adc_db="Bypass", adc_sha="Single-Ended", adc_curr_src="BJT-sd", env="RT", flg_bjt_r=True)
#cq.adc_cfg(adc_sdc="On", adc_db="Bypass", adc_sha="Diff", adc_curr_src="BJT-sd", env="RT", flg_bjt_r=True)
