# -*- coding: utf-8 -*-
"""
Created on Tue Feb 12 16:54:04 2019

@author: JunbinZhang
"""
from udp import UDP #change file name here
from fpga_reg import FPGA_REG
from fe_reg import FE_REG
from user_defined import User_defined
from adc_i2c_uart import COLDADC_tool
from adc_reg import ADC_REG
from frame import Frames
import sys
import time
import math
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import os.path
class Brd_Config:
    #----------------initialization----------------------#
    #-----------------------FPGA-----------------------------#
    def Acq_mode(self,mode,Value = None):          
        if mode == 'fake1':
            self.udp.write(self.fpga_reg.ADC_TST_PATT,Value)
            self.udp.write(self.fpga_reg.ADC_TST_PATT_MODE,0)
            self.udp.write(self.fpga_reg.ADC_TST_PATT_EN,1)
        elif mode == 'fake2':
            self.udp.write(self.fpga_reg.ADC_TST_PATT_MODE,1)
            self.udp.write(self.fpga_reg.ADC_TST_PATT_EN,1)
        else:
            self.udp.write(self.fpga_reg.ADC_TST_PATT_EN,0);
    
    def udp_fifo_clear(self):
        self.udp.write(self.fpga_reg.udp_fifo_clr,1)
        self.udp.write(self.fpga_reg.udp_fifo_clr,1)
        time.sleep(0.1)
        self.udp.write(self.fpga_reg.udp_fifo_clr,0)
                
    def Acq_start_stop(self,Val):
        if Val == 1:
            self.udp_fifo_clear()        
            self.udp.write(self.fpga_reg.ACQ_START,1)
        else:
            self.udp.write(self.fpga_reg.ACQ_START,0)
        
    def get_data(self,PktNum,chkflg,Jumbo):
        data = self.udp.get_rawdata(PktNum,chkflg,Jumbo)
        #print(data)
        return data
    
    def check_board(self):
        result = self.udp.read(self.fpga_reg.BRD_V)
        if result == 0x0c0d0a03:
            return True
        else:
            return False
        
    def write_fpga_reg(self,reg,value):
        self.udp.write_reg(reg,value)
    
    def read_fpga_reg(self,reg):
        result = self.udp.read_reg(reg)
        return hex(result)
    
    def word_order_slider(self,num):
        self.udp.write(self.fpga_reg.word_order,num)
#    def I2C_DEV(self,page):
#        self.udp.write(self.fpga_reg.I2C_DEV_ADDR,page)
    #-------------------front-end-control bits----------------#    
#    def fe_config(self,mode):
#        if mode == 'FDAC': #FPGA DAC mode
#            self.sts = self.user.Input['Test_Input']
#            self.sdacsw = self.user.Pulse['External']
#        elif mode == 'ADAC': #ASIC DAC mode
#            self.sts = self.user.Input['Test_Input']
#            self.sdacsw = self.user.Pulse['Internal']
#        else:                #RMS default
#            self.sts = self.user.Input['Direct_Input']
#            self.sdacsw = self.user.Pulse['Disable']
            
    def fe_chn_input(self,modes):
        for i in range(len(modes)):
            if modes[i] == 'Direct_Input':
                self.sts[i] = self.user.Input['Direct_Input']
            else:
                self.sts[i] = self.user.Input['Test_Input']
            
    def fe_chn_baseline(self,modes):
        for i in range(len(modes)):
            if modes[i] == "900mV":
                self.snc[i] = self.user.Baseline['900mV']
            else:
                self.snc[i] = self.user.Baseline['200mV']
            
    def fe_chn_gain(self,gains):
        for i in range(len(gains)):
            if gains[i] == "4.7mV/fC":
                self.sg[i] = self.user.Gain['4.7mV/fC']
            elif gains[i] == "7.8mV/fC":
                self.sg[i] = self.user.Gain['7.8mV/fC']
            elif gains[i] == "14mV/fC":
                self.sg[i] = self.user.Gain['14mV/fC']
            else:
                self.sg[i] = self.user.Gain['25mV/fC']
    
    def fe_chn_peaktime(self, modes):
        for i in range(len(modes)):       
            if modes[i] == "1us":
                self.st[i] = self.user.Peaktime['1us']
            elif modes[i] == "0.5us":
                self.st[i] = self.user.Peaktime['0.5us']
            elif modes[i] == "2us":
                self.st[i] = self.user.Peaktime['2us']
            else:
                self.st[i] = self.user.Peaktime['3us']
            
    def fe_chn_monitor(self,modes):
        for i in range(len(modes)):
            if modes[i] == "off":
                self.smn[i] = self.user.Mon['off']
            else:
                self.smn[i] = self.user.Mon['on']
            
    def fe_chn_buffer(self,modes):
        for i in range(len(modes)):
            if modes[i] == "off":
                self.sbf[i] = self.user.Buffer['off']
            else:
                self.sbf[i] = self.user.Buffer['on']
    #---------FE global register settings---------#
    def fe_pulse_src(self,mode):
        if mode == "Disable":
            self.sdacsw = self.user.Pulse['Disable']
        elif mode == "External":
            self.sdacsw = self.user.Pulse['External']
        elif mode == "Internal":
            self.sdacsw = self.user.Pulse['Internal']
        else:
            self.sdacsw = self.user.Pulse['ExtM']

    def fe_Coupled(self,mode):
        if mode == "DC":
            self.sdc = self.user.Coupled['DC']
        else:
            self.sdc = self.user.Coupled['AC']

    def fe_Leakage(self,mode):
        if mode == "500pA":
            self.slkh = (self.user.Leakage['500pA'] & 0x2) >> 1
            self.slk = self.user.Leakage['500pA'] & 0x1 
        elif mode == "100pA":
            self.slkh = (self.user.Leakage['100pA'] & 0x2) >> 1
            self.slk = self.user.Leakage['100pA'] & 0x1  
        elif mode == "5nA":
            self.slkh = (self.user.Leakage['5nA'] & 0x2) >> 1
            self.slk = self.user.Leakage['5nA'] & 0x1 
        else:
            self.slkh = (self.user.Leakage['1nA'] & 0x2) >> 1
            self.slk = self.user.Leakage['1nA'] & 0x1 
    
    def fe_monitor_type(self,mode):
        if mode == "Analog":
            self.stb = self.user.Monitor['Analog']
        elif mode == "Temp":
            self.stb = self.user.Monitor['Temp']
        else:
            self.stb = self.user.Monitor['Bandgap']

    def fe_sdac(self,dac):
        self.sdac = dac
    #-----------------------------------------------#    
    def fe_spi_config(self):
        #write twice in order to get the feedback
        #generate data.
        for chn in range(16):
            self.fe_reg.FE_CHN[chn].fe_chn_reg(self.sts[chn],self.snc[chn],self.sg[chn],self.st[chn],self.smn[chn],self.sbf[chn])   #change parameter here
        self.fe_reg.FE_GLOBAL.fe_glbl_reg(self.sdc, self.slkh, self.s16, self.stb, self.slk, self.sdac, self.sdacsw)    
        
        fe_spi_data = self.fe_reg.spi_data()        
        #print(fe_spi_data), currect
        #for i in fe_spi_data:
        #    print(hex(i))
        for times in range(2):
            for i in range(len(fe_spi_data)):
                #load data
                self.udp.write_reg(self.fpga_reg.SPI_WRITE_BASE+i, fe_spi_data[i])
                time.sleep(0.01)
            #write SPI
            self.udp.write(self.fpga_reg.WRITE_SPI,1)
            time.sleep(0.5)
            self.udp.write(self.fpga_reg.WRITE_SPI,0)
        else: #Check if there are something wrong and get the feedback
            spi_data_fb=[]
            time.sleep(0.5) #need a delay here too fast
            for i in range(len(fe_spi_data)):
                spi_data_fb.append(self.udp.read_reg(self.fpga_reg.SPI_READ_BASE + i))
                time.sleep(0.01)
            #print(spi_data_fb)
            p = [i for i, j in enumerate(zip(spi_data_fb,fe_spi_data)) if all(j[0]!=k for k in j[1:])]
            if not p:
                #print('FE SPI configuration success') #feadback is equels to the original
                time.sleep(0.01)
            else:
                print('FE SPI configuration failed!')
                sys.exit     
                
    def fe_pulse_config(self,mode):
        #-------------register 0x10------------------------#
        #bit0 FPGA_TP_EN, set to enable FPGA calibration DAC
        #bit1 ASIC_TP_EN, set to enable ASIC calibration, pulse will be sent to ASIC ck pin
        #bit8 DAC_SELECT, select analog pulse source, 0= FM on board DAC;1=Analog pulse from the WIB
        #bit10 ANALOG/Jtag, set to select analog monitor to be driver over JTAG TDO
        #-------------register 0x12------------------------#
        #bit0 INT_TP_EN, set to enable internal pulse generator,period set by register 5
        #bit1 EXT_TP_EN, set to allow test pulses to be received by external timing control interface,register 5 delay & amplitude can be used.
        if(mode == "External"):
            #self.udp.write_reg(0xc,0x39)
            self.udp.write_reg(0xc,0)
            time.sleep(0.01) 
            self.udp.write(self.fpga_reg.FPGA_DAC_SELECT,1) #select analog pulse source
            time.sleep(0.01)   
            self.udp.write(self.fpga_reg.FPGA_TP_EN,1)      #enable FPGA calibration DAC
            time.sleep(0.01)
            self.udp.write(self.fpga_reg.INT_TP_EN,1)       #enable pulse injection
            
        elif(mode == "Internal"):
            #self.udp.write_reg(0xc,0x56)
            self.udp.write_reg(0xc,0)
            time.sleep(0.01) 
            self.udp.write(self.fpga_reg.FPGA_DAC_SELECT,1)#select analog pulse source
            time.sleep(0.01)   
            self.udp.write(self.fpga_reg.ASIC_TP_EN,1) #enable ASIC DAC
            time.sleep(0.01)
            self.udp.write(self.fpga_reg.INT_TP_EN,1) #enable pulse injection

        else: #No pulse, RMS mode
            self.udp.write_reg(0xc,0x0)
    #Pulse paramter settings
    def fe_pulse_param(self,delay,period,width):
        #-------------register 0x05------------------------#    
        #bit15:8, TEST_PULSE_DELAY,Controls test pulse sample shift by 10ns step, 0=0, 1=10ns, 2= 20ns ...
        #bit31:16,TEST_PULSE_PERIOD, set to control test pulse period(dependent on ADC SAMPLE RATE) 0=500ns, 01=1us, 02=1.5us
        #Note: Amplitude here affects FPGA dac only, delay and period affect FPGA_DAC and ASIC_DAC both 1lsb = 1.8V/64 = 0.028125       
        self.udp.write(self.fpga_reg.TP_DLY,delay)      #77
        self.udp.write(self.fpga_reg.TP_FREQ,period)    #500
        self.udp.write(self.fpga_reg.PULSE_WIDTH,width) #0xa00

    def fe_fpga_dac(self,amp):
        #bit5:0, TEST_PULSE_AMPLITUDE, set to control 5 bit DAC for test pulse, 0=disable,1=DAC LSB 2=2LSB ....
        self.udp.write(self.fpga_reg.TP_AMPL,amp)       #8
        
    #------------------------ADC------------------#
    def adc_hard_reset(self):
        self.adc.hard_reset()

    def adc_soft_reset(self):
        self.adc.I2C_write(0,0,6,0)
        time.sleep(0.05)
        self.adc.I2C_write(0,0,0,0)
        
    def adc_i2c_uart(self,tool=None): #I2C
        if tool == None:    
            self.adc.config_tool("I2C")
        else:
            self.adc.config_tool(tool) 
            
    def adc_write_reg(self,reg,data):
        offset = 0x80
        regaddr = reg + offset
        self.adc.I2C_write(self.chip_id,self.page,regaddr,data)
        
    def adc_read_reg(self,reg):
        offset = 0x80
        regaddr = offset + reg
        result = self.adc.I2C_read(self.chip_id,self.page,regaddr)
        return hex(result)
        
    def adc_larasic_interface(self,sdc,db,ndiff,ref_val):
        #sdc=1 bypass, db=1 bypass, ndiff=1 single-ended, ref_val=0
        self.adc.ADC_I2C_write(self.chip_id,self.page,self.adc_reg.ibuff_sdc_pd,sdc)
        self.adc.ADC_I2C_write(self.chip_id,self.page,self.adc_reg.ibuff_diff_pd,db)
        self.adc.ADC_I2C_write(self.chip_id,self.page,self.adc_reg.sha_se_input,ndiff)
        #control of current multiplexer. BJT or CMOS reference Direct current to SDC or DB
        self.adc.ADC_I2C_write(self.chip_id,self.page,self.adc_reg.ibuff_ctrl,ref_val)
    
    def adc_sha_input(self,ndiff):
        self.adc.ADC_I2C_write(self.chip_id,self.page,self.adc_reg.sha_se_input,ndiff)
        
    def adc_ref_vol_src(self,src):
        if src == "BJT":
            bit0 = 0
            bit1 = 0
            bit2 = 0
        elif src =="BJT_EXT":
            bit0 = 0
            bit1 = 1
            bit2 = 0
        elif src =="CMOS":
            bit0 = 0
            bit1 = 0
            bit2 = 1
        elif src =="EXTERNAL":
            bit0 = 1
            bit1 = 0
            bit2 = 1
        else:
            print("Error")
        self.adc.ADC_I2C_write(self.chip_id,self.page,self.adc_reg.external_reference,bit0) #internal reference 0, external reference 1
        self.adc.ADC_I2C_write(self.chip_id,self.page,self.adc_reg.external_bgr,bit1)       #internal bandgap reference used 0, otherwise 1
        self.adc.ADC_I2C_write(self.chip_id,self.page,self.adc_reg.bgr_select,bit2)         #BJT reference for bandgap 0, CMOS for bandgap
    
    def adc_bias_curr_src(self,src):
        if src == "BJT":
            sel = 0
        elif src == "CMOS_INTR":
            sel = 1
        elif src == "CMOS_EXTR":
            sel = 2
        elif src == "PlanB":
            sel = 3
        self.adc.ADC_I2C_write(self.chip_id,self.page,self.adc_reg.iref_sel,sel)
        self.adc.ADC_I2C_write(self.chip_id,self.page,self.adc_reg.vt_iref_trim_ctrl,3)
    
    def adc_set_ioffset(self,vrefp_c,vrefn_c,vcmo_c,vcmi_c):
        self.adc.ADC_I2C_write(self.chip_id,self.page,self.adc_reg.vrefp_offset,vrefp_c)
        self.adc.ADC_I2C_write(self.chip_id,self.page,self.adc_reg.vrefn_offset,vrefn_c)
        self.adc.ADC_I2C_write(self.chip_id,self.page,self.adc_reg.vcmo_offset,vcmo_c)
        self.adc.ADC_I2C_write(self.chip_id,self.page,self.adc_reg.vcmi_offset,vcmi_c)
        
    def adc_set_vrefs(self,vrefp_c,vrefn_c,vcmo_c,vcmi_c):
        self.adc.ADC_I2C_write(self.chip_id,self.page,self.adc_reg.vrefp_ctrl,vrefp_c)
        self.adc.ADC_I2C_write(self.chip_id,self.page,self.adc_reg.vrefn_ctrl,vrefn_c)
        self.adc.ADC_I2C_write(self.chip_id,self.page,self.adc_reg.vcmo_ctrl,vcmo_c)
        self.adc.ADC_I2C_write(self.chip_id,self.page,self.adc_reg.vcmi_ctrl,vcmi_c)
    
    def adc_set_curr_vdac(self,vdac0,vdac1):
        self.adc.ADC_I2C_write(self.chip_id,self.page,self.adc_reg.i_vdac_0_ctrl,vdac0)
        self.adc.ADC_I2C_write(self.chip_id,self.page,self.adc_reg.i_vdac_1_ctrl,vdac1)  
        
    def adc_set_curr_ibuff(self,ibuff0,ibuff1):
        self.adc.ADC_I2C_write(self.chip_id,self.page,self.adc_reg.ibuff0_ctrl,ibuff0)
        self.adc.ADC_I2C_write(self.chip_id,self.page,self.adc_reg.ibuff1_ctrl,ibuff1)          
    
    def adc_ref_monitor(self,byteL,byteH):
        self.adc.ADC_I2C_write(self.chip_id,self.page,self.adc_reg.ref_monitor_L,byteL)
        self.adc.ADC_I2C_write(self.chip_id,self.page,self.adc_reg.ref_monitor_H,byteH)

    def adc_ref_powerdown(self,byteL,byteH):
        self.adc.ADC_I2C_write(self.chip_id,self.page,self.adc_reg.ref_powerdown_L,byteL)
        self.adc.ADC_I2C_write(self.chip_id,self.page,self.adc_reg.ref_powerdown_H,byteH)   
    
    def adc_load_pattern_0(self,byteL,byteH):
        self.adc.ADC_I2C_write(self.chip_id,self.page,self.adc_reg.config_adc0_pattern_L,byteL)
        self.adc.ADC_I2C_write(self.chip_id,self.page,self.adc_reg.config_adc0_pattern_H,byteH)
        
    def adc_load_pattern_1(self,byteL,byteH):
        self.adc.ADC_I2C_write(self.chip_id,self.page,self.adc_reg.config_adc1_pattern_L,byteL)
        self.adc.ADC_I2C_write(self.chip_id,self.page,self.adc_reg.config_adc1_pattern_H,byteH)
    #CMOS reference
    def adc_set_cmos_vrefs(self,vrefp_c,vrefn_c,vcmi_c,vcmo_c):
        self.adc.ADC_I2C_write(self.chip_id,self.page,self.adc_reg.vrefp_ctrl_cmos,vrefp_c)
        time.sleep(0.02)
        self.adc.ADC_I2C_write(self.chip_id,self.page,self.adc_reg.vrefn_ctrl_cmos,vrefn_c)
        time.sleep(0.02) 
        self.adc.ADC_I2C_write(self.chip_id,self.page,self.adc_reg.vcmi_ctrl_cmos,vcmi_c)
        time.sleep(0.02) 
        self.adc.ADC_I2C_write(self.chip_id,self.page,self.adc_reg.vcmo_ctrl_cmos,vcmo_c)
        #time.sleep(0.01) 
    
    def adc_set_cmos_ibuff(self,ibuff0,ibuff1):
        self.adc.ADC_I2C_write(self.chip_id,self.page,self.adc_reg.ibuff0_cmos,ibuff0)
        self.adc.ADC_I2C_write(self.chip_id,self.page,self.adc_reg.ibuff1_cmos,ibuff1)
        
    def adc_set_cmos_iref_trim(self,val):
        value = int((int(val)-35)/5)
        self.adc.ADC_I2C_write(self.chip_id,self.page,self.adc_reg.vt_iref_trim_ctrl,value)
    #test data mode    
    def adc_test_data_mode(self,mode):
        if mode == "Normal":
            self.adc.ADC_I2C_write(self.chip_id,self.page,self.adc_reg.config_test_data_mode,0)
        else:
            self.adc.ADC_I2C_write(self.chip_id,self.page,self.adc_reg.config_test_data_mode,1)
            
    def adc_set_adc_bias(self,val):
        value = int((80-int(val))/10)
        self.adc.ADC_I2C_write(self.chip_id,self.page,self.adc_reg.adc_bias,value)

    def adc_edge_select(self,mode):
        if mode == "Normal":
            self.adc.ADC_I2C_write(self.chip_id,self.page,self.adc_reg.edge_select,0)
        else:
            self.adc.ADC_I2C_write(self.chip_id,self.page,self.adc_reg.edge_select,1) 
    #choose format of ADC output codes
    def adc_outputformat(self,oformat):
        if oformat == "two-complement" :
            self.adc.ADC_I2C_write(self.chip_id,self.page,self.adc_reg.adc_output_format,0)
        else:
            self.adc.ADC_I2C_write(self.chip_id,self.page,self.adc_reg.adc_output_format,1) 
    def adc_sync_mode(self,mode):
        if mode == "Normal":
            self.adc.ADC_I2C_write(self.chip_id,self.page,self.adc_reg.adc_sync_mode,0)
        else:
            self.adc.ADC_I2C_write(self.chip_id,self.page,self.adc_reg.adc_sync_mode,1)
    def adc_test_input(self,mode):
        if mode == "Normal":
            self.adc.ADC_I2C_write(self.chip_id,self.page,self.adc_reg.adc_test_mode,0)
        else:
            self.adc.ADC_I2C_write(self.chip_id,self.page,self.adc_reg.adc_test_mode,1)
            
    def adc_output_select(self,option):
        if option == "cali_ADCdata":
            self.adc.ADC_I2C_write(self.chip_id,self.page,self.adc_reg.adc_output_select,0)
        elif option == "uncali_ADCdata":
            self.adc.ADC_I2C_write(self.chip_id,self.page,self.adc_reg.adc_output_select,1)
        elif option == "raw_ADC0":
            self.adc.ADC_I2C_write(self.chip_id,self.page,self.adc_reg.adc_output_select,2)
        elif option == "raw_ADC1":
            self.adc.ADC_I2C_write(self.chip_id,self.page,self.adc_reg.adc_output_select,3)
            
    def adc_sdc_select(self,mode):
        if mode == "On":
            self.adc.ADC_I2C_write(self.chip_id,self.page,self.adc_reg.ibuff_sdc_pd,0)
        else:
            self.adc.ADC_I2C_write(self.chip_id,self.page,self.adc_reg.ibuff_sdc_pd,1)
    
    def adc_db_select(self,mode):
        if mode == "Bypass":
            self.adc.ADC_I2C_write(self.chip_id,self.page,self.adc_reg.ibuff_diff_pd,1)
        else:
            self.adc.ADC_I2C_write(self.chip_id,self.page,self.adc_reg.ibuff_diff_pd,0)
    
    def adc_ibuff_ctrl(self,mode):
        if mode == "BJT-sd":
            self.adc.ADC_I2C_write(self.chip_id,self.page,self.adc_reg.ibuff_ctrl,0x5)
        elif mode =="BJT-db":
            self.adc.ADC_I2C_write(self.chip_id,self.page,self.adc_reg.ibuff_ctrl,0x9)
        elif mode =="CMOS-sd":
            self.adc.ADC_I2C_write(self.chip_id,self.page,self.adc_reg.ibuff_ctrl,0x6)
        elif mode =="CMOS-db":
            self.adc.ADC_I2C_write(self.chip_id,self.page,self.adc_reg.ibuff_ctrl,0xa)
        else:
            self.adc.ADC_I2C_write(self.chip_id,self.page,self.adc_reg.ibuff_ctrl,0)
            
    def adc_framemarker_shift(self,num):
        self.adc.ADC_I2C_write(self.chip_id,2, self.adc_reg.page2_config_start_number,num)
    
    
    def adc_freeze_sha0(self,mode):
        if mode == "Normal":
           self.adc.ADC_I2C_write(self.chip_id,self.page,self.adc_reg.freeze_sha0,0)
        else:
           self.adc.ADC_I2C_write(self.chip_id,self.page,self.adc_reg.freeze_sha0,1) 
    def adc_freeze_sha1(self,mode):
        if mode == "Normal":
            self.adc.ADC_I2C_write(self.chip_id,self.page,self.adc_reg.freeze_sha1,0)
        else:
            self.adc.ADC_I2C_write(self.chip_id,self.page,self.adc_reg.freeze_sha1,1)
            
    def adc_freeze_select_0(self,num):
        self.adc.ADC_I2C_write(self.chip_id,self.page,self.adc_reg.freeze_select0,num)
    
    def adc_freeze_select_1(self,num):
        self.adc.ADC_I2C_write(self.chip_id,self.page,self.adc_reg.freeze_select1,num)
        
    def adc_sha0_bias(self,num):
        self.adc.ADC_I2C_write(self.chip_id,self.page,self.adc_reg.sha0_bias,num)
        
    def adc_sha1_bias(self,num):
        self.adc.ADC_I2C_write(self.chip_id,self.page,self.adc_reg.sha1_bias,num)
        
    def adc_sha2_bias(self,num):
        self.adc.ADC_I2C_write(self.chip_id,self.page,self.adc_reg.sha2_bias,num)
        
    def adc_sha3_bias(self,num):
        self.adc.ADC_I2C_write(self.chip_id,self.page,self.adc_reg.sha3_bias,num)
        
    def adc_sha4_bias(self,num):
        self.adc.ADC_I2C_write(self.chip_id,self.page,self.adc_reg.sha4_bias,num)
        
    def adc_sha5_bias(self,num):
        self.adc.ADC_I2C_write(self.chip_id,self.page,self.adc_reg.sha5_bias,num)
        
    def adc_sha6_bias(self,num):
        self.adc.ADC_I2C_write(self.chip_id,self.page,self.adc_reg.sha6_bias,num)
        
    def adc_sha7_bias(self,num):
        self.adc.ADC_I2C_write(self.chip_id,self.page,self.adc_reg.sha7_bias,num)
        
    def adc_sha_pd_0(self,mode):
        if mode == "Normal":
            self.adc.ADC_I2C_write(self.chip_id,self.page,self.adc_reg.sha_pd_0,0)
        else:
            self.adc.ADC_I2C_write(self.chip_id,self.page,self.adc_reg.sha_pd_0,0xff) 
            
    def adc_sha_pd_1(self,mode):
        if mode == "Normal":
            self.adc.ADC_I2C_write(self.chip_id,self.page,self.adc_reg.sha_pd_1,0)
        else:
            self.adc.ADC_I2C_write(self.chip_id,self.page,self.adc_reg.sha_pd_1,0xff) 
            
    def adc_sha_clk_sel(self,mode):
        if mode == "backend":
            self.adc.ADC_I2C_write(self.chip_id,self.page,self.adc_reg.clk_sha_select,0)
        else:
            self.adc.ADC_I2C_write(self.chip_id,self.page,self.adc_reg.clk_sha_select,1) 
            
    def complement(self,num,complete):
        if complete == "2s":
            if (num <= 32767):
                result = num
            else:
                result = (num%32768 - 32768)
        else:
            result = num
        return result
    
    def subtract(self,num):
        return (int(num) & 0xffff) #ignore the bit17

    def adc_average(self,pktnum,neg=None):
        #add for test  
        self.Acq_start_stop(1)
        #pktnum = 16000 # up to 128k points
        adcdata = self.get_data(pktnum,1,'Jumbo')
        #time.sleep(1)
        self.Acq_start_stop(0)
        
        frames_inst = Frames(pktnum,adcdata)
        frames = frames_inst.packets()
    
        chns=[[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
        for i in range(len(frames)):
            for j in range(16): #16 channels
                chns[j].append(self.complement(frames[i].ADCdata[j],"none"))
        
        temp0 = chns[0] + chns[1] + chns[2] + chns[3] + chns[4] + chns[5] + chns[6] + chns[7]
        temp1 = chns[8] + chns[9] + chns[10]+ chns[11]+ chns[12]+ chns[13]+ chns[14]+ chns[15]
          
        val0 = round(sum(temp0)/len(temp0))
        val1 = round(sum(temp1)/len(temp1))
        
        if neg == None:
            return (val0,val1, temp0, temp1)
        else:
            return ((65536-val0),(65536-val1), temp0, temp1)
        
    #ADC0 calibration one after one
    def adc_autocali_onebyone(self,samples):
        
        #----------ADC0 Calibration---------------#
        #Measure S0, S1,S2 and S3 for stage 6 (most significant stage=stage0)
        self.adc_write_reg(32,0x7F)
        self.adc_write_reg(44,0x19)
        self.adc_write_reg(46,0x10)
        self.adc_write_reg(46,0x0) #S0 appears at ADC output
        adc0_S0,_ = self.adc_average(samples,"neg")
        self.adc_write_reg(46,0x1) #S1 appears at ADC output
        adc0_S1,_ = self.adc_average(samples)
        self.adc_write_reg(46,0x5) #S2 appears at ADC output
        adc0_S2,_ = self.adc_average(samples)
        self.adc_write_reg(46,0x4)
        self.adc_write_reg(45,0x10)#S3 appears at ADC output
        adc0_S3,_ = self.adc_average(samples,"neg")
        self.adc_write_reg(44,0x0)
        self.adc_write_reg(45,0x0)
        self.adc_write_reg(46,0x0)
        adc0_W0 = self.subtract(adc0_S1 + adc0_S0)
        adc0_W2 = self.subtract(adc0_S2 + adc0_S3)
        adc0_w0l = adc0_W0 & 0xff
        adc0_w0h = (adc0_W0 >> 8) & 0xff
        adc0_w2l = adc0_W2 & 0xff
        adc0_w2h = (adc0_W2 >> 8) & 0xff     
        self.adc.I2C_write_checked(self.chip_id,self.page,12,adc0_w0l)
        self.adc.I2C_write_checked(self.chip_id,self.page,13,adc0_w0h)
        self.adc.I2C_write_checked(self.chip_id,self.page,44,adc0_w2l)
        self.adc.I2C_write_checked(self.chip_id,self.page,45,adc0_w2h)
        #Measure S0, S1,S2 and S3 for stage 5 (most significant stage=stage0)
        self.adc_write_reg(32,0x6F)
        self.adc_write_reg(44,0x15)
        self.adc_write_reg(46,0x10)        
        self.adc_write_reg(46,0x0) #S0 appears at ADC output
        adc0_S0,_ = self.adc_average(samples,"neg")
        self.adc_write_reg(46,0x1) #S1 appears at ADC output
        adc0_S1,_ = self.adc_average(samples)
        self.adc_write_reg(46,0x5) #S2 appears at ADC output
        adc0_S2,_ = self.adc_average(samples)
        self.adc_write_reg(46,0x4)
        self.adc_write_reg(45,0x10)#S3 appears at ADC output
        adc0_S3,_ = self.adc_average(samples,"neg")
        self.adc_write_reg(44,0x0)
        self.adc_write_reg(45,0x0)
        self.adc_write_reg(46,0x0)        
        adc0_W0 = self.subtract(adc0_S1 + adc0_S0)
        adc0_W2 = self.subtract(adc0_S2 + adc0_S3)
        adc0_w0l = adc0_W0 & 0xff
        adc0_w0h = (adc0_W0 >> 8) & 0xff
        adc0_w2l = adc0_W2 & 0xff
        adc0_w2h = (adc0_W2 >> 8) & 0xff     
        self.adc.I2C_write_checked(self.chip_id,self.page,10,adc0_w0l)
        self.adc.I2C_write_checked(self.chip_id,self.page,11,adc0_w0h)
        self.adc.I2C_write_checked(self.chip_id,self.page,42,adc0_w2l)
        self.adc.I2C_write_checked(self.chip_id,self.page,43,adc0_w2h)        
        #Measure S0, S1,S2 and S3 for stage 4 (most significant stage=stage0)
        self.adc_write_reg(32,0x5F)
        self.adc_write_reg(44,0x11)
        self.adc_write_reg(46,0x10)        
        self.adc_write_reg(46,0x0) #S0 appears at ADC output
        adc0_S0,_ = self.adc_average(samples,"neg")
        self.adc_write_reg(46,0x1) #S1 appears at ADC output
        adc0_S1,_ = self.adc_average(samples)
        self.adc_write_reg(46,0x5) #S2 appears at ADC output
        adc0_S2,_ = self.adc_average(samples)
        self.adc_write_reg(46,0x4)
        self.adc_write_reg(45,0x10)#S3 appears at ADC output
        adc0_S3,_ = self.adc_average(samples,"neg")
        self.adc_write_reg(44,0x0)
        self.adc_write_reg(45,0x0)
        self.adc_write_reg(46,0x0)        
        adc0_W0 = self.subtract(adc0_S1 + adc0_S0)
        adc0_W2 = self.subtract(adc0_S2 + adc0_S3)
        adc0_w0l = adc0_W0 & 0xff
        adc0_w0h = (adc0_W0 >> 8) & 0xff
        adc0_w2l = adc0_W2 & 0xff
        adc0_w2h = (adc0_W2 >> 8) & 0xff     
        self.adc.I2C_write_checked(self.chip_id,self.page,8,adc0_w0l)
        self.adc.I2C_write_checked(self.chip_id,self.page,9,adc0_w0h)
        self.adc.I2C_write_checked(self.chip_id,self.page,40,adc0_w2l)
        self.adc.I2C_write_checked(self.chip_id,self.page,41,adc0_w2h)
        
        #Measure S0, S1,S2 and S3 for stage 3 (most significant stage=stage0)
        self.adc_write_reg(32,0x4F)
        self.adc_write_reg(44,0xd)
        self.adc_write_reg(46,0x10)        
        self.adc_write_reg(46,0x0) #S0 appears at ADC output
        adc0_S0,_ = self.adc_average(samples,"neg")
        self.adc_write_reg(46,0x1) #S1 appears at ADC output
        adc0_S1,_ = self.adc_average(samples)
        self.adc_write_reg(46,0x5) #S2 appears at ADC output
        adc0_S2,_ = self.adc_average(samples)
        self.adc_write_reg(46,0x4)
        self.adc_write_reg(45,0x10)#S3 appears at ADC output
        adc0_S3,_ = self.adc_average(samples,"neg")
        self.adc_write_reg(44,0x0)
        self.adc_write_reg(45,0x0)
        self.adc_write_reg(46,0x0)        
        adc0_W0 = self.subtract(adc0_S1 + adc0_S0)
        adc0_W2 = self.subtract(adc0_S2 + adc0_S3)
        adc0_w0l = adc0_W0 & 0xff
        adc0_w0h = (adc0_W0 >> 8) & 0xff
        adc0_w2l = adc0_W2 & 0xff
        adc0_w2h = (adc0_W2 >> 8) & 0xff     
        self.adc.I2C_write_checked(self.chip_id,self.page,6,adc0_w0l)
        self.adc.I2C_write_checked(self.chip_id,self.page,7,adc0_w0h)
        self.adc.I2C_write_checked(self.chip_id,self.page,38,adc0_w2l)
        self.adc.I2C_write_checked(self.chip_id,self.page,39,adc0_w2h)        
        
        #Measure S0, S1,S2 and S3 for stage 2 (most significant stage=stage0)
        self.adc_write_reg(32,0x3F)
        self.adc_write_reg(44,0x9)
        self.adc_write_reg(46,0x10)        
        self.adc_write_reg(46,0x0) #S0 appears at ADC output
        adc0_S0,_ = self.adc_average(samples,"neg")
        self.adc_write_reg(46,0x1) #S1 appears at ADC output
        adc0_S1,_ = self.adc_average(samples)
        self.adc_write_reg(46,0x5) #S2 appears at ADC output
        adc0_S2,_ = self.adc_average(samples)
        self.adc_write_reg(46,0x4)
        self.adc_write_reg(45,0x10)#S3 appears at ADC output
        adc0_S3,_ = self.adc_average(samples,"neg")
        self.adc_write_reg(44,0x0)
        self.adc_write_reg(45,0x0)
        self.adc_write_reg(46,0x0)        
        adc0_W0 = self.subtract(adc0_S1 + adc0_S0)
        adc0_W2 = self.subtract(adc0_S2 + adc0_S3)
        adc0_w0l = adc0_W0 & 0xff
        adc0_w0h = (adc0_W0 >> 8) & 0xff
        adc0_w2l = adc0_W2 & 0xff
        adc0_w2h = (adc0_W2 >> 8) & 0xff     
        self.adc.I2C_write_checked(self.chip_id,self.page,4,adc0_w0l)
        self.adc.I2C_write_checked(self.chip_id,self.page,5,adc0_w0h)
        self.adc.I2C_write_checked(self.chip_id,self.page,36,adc0_w2l)
        self.adc.I2C_write_checked(self.chip_id,self.page,37,adc0_w2h)           
        #Measure S0, S1,S2 and S3 for stage 1 (most significant stage=stage0)
        self.adc_write_reg(32,0x2F)
        self.adc_write_reg(44,0x5)
        self.adc_write_reg(46,0x10)        
        self.adc_write_reg(46,0x0) #S0 appears at ADC output
        adc0_S0,_ = self.adc_average(samples,"neg")
        self.adc_write_reg(46,0x1) #S1 appears at ADC output
        adc0_S1,_ = self.adc_average(samples)
        self.adc_write_reg(46,0x5) #S2 appears at ADC output
        adc0_S2,_ = self.adc_average(samples)
        self.adc_write_reg(46,0x4)
        self.adc_write_reg(45,0x10)#S3 appears at ADC output
        adc0_S3,_ = self.adc_average(samples,"neg")
        self.adc_write_reg(44,0x0)
        self.adc_write_reg(45,0x0)
        self.adc_write_reg(46,0x0)        
        adc0_W0 = self.subtract(adc0_S1 + adc0_S0)
        adc0_W2 = self.subtract(adc0_S2 + adc0_S3)
        adc0_w0l = adc0_W0 & 0xff
        adc0_w0h = (adc0_W0 >> 8) & 0xff
        adc0_w2l = adc0_W2 & 0xff
        adc0_w2h = (adc0_W2 >> 8) & 0xff     
        self.adc.I2C_write_checked(self.chip_id,self.page,2,adc0_w0l)
        self.adc.I2C_write_checked(self.chip_id,self.page,3,adc0_w0h)
        self.adc.I2C_write_checked(self.chip_id,self.page,34,adc0_w2l)
        self.adc.I2C_write_checked(self.chip_id,self.page,35,adc0_w2h) 
        #Measure S0, S1,S2 and S3 for stage 0 (most significant stage=stage0)
        self.adc_write_reg(32,0x1F)
        self.adc_write_reg(44,0x1)
        self.adc_write_reg(46,0x10)        
        self.adc_write_reg(46,0x0) #S0 appears at ADC output
        adc0_S0,_ = self.adc_average(samples,"neg")
        self.adc_write_reg(46,0x1) #S1 appears at ADC output
        adc0_S1,_ = self.adc_average(samples)
        self.adc_write_reg(46,0x5) #S2 appears at ADC output
        adc0_S2,_ = self.adc_average(samples)
        self.adc_write_reg(46,0x4)
        self.adc_write_reg(45,0x10)#S3 appears at ADC output
        adc0_S3,_ = self.adc_average(samples,"neg")
        self.adc_write_reg(44,0x0)
        self.adc_write_reg(45,0x0)
        self.adc_write_reg(46,0x0)        
        adc0_W0 = self.subtract(adc0_S1 + adc0_S0)
        adc0_W2 = self.subtract(adc0_S2 + adc0_S3)
        adc0_w0l = adc0_W0 & 0xff
        adc0_w0h = (adc0_W0 >> 8) & 0xff
        adc0_w2l = adc0_W2 & 0xff
        adc0_w2h = (adc0_W2 >> 8) & 0xff     
        self.adc.I2C_write_checked(self.chip_id,self.page,0,adc0_w0l)
        self.adc.I2C_write_checked(self.chip_id,self.page,1,adc0_w0h)
        self.adc.I2C_write_checked(self.chip_id,self.page,32,adc0_w2l)
        self.adc.I2C_write_checked(self.chip_id,self.page,33,adc0_w2h)     
        
        #----------ADC1 Calibration---------------#
        #Measure S0, S1,S2 and S3 for stage 6 (most significant stage=stage0)
        self.adc_write_reg(32,0x7F)
        self.adc_write_reg(44,0x1a)
        self.adc_write_reg(46,0x20) #clear
        self.adc_write_reg(46,0x0) #S0 appears at ADC output
        _,adc1_S0 = self.adc_average(samples,"neg")
        self.adc_write_reg(46,0x2) #S1 appears at ADC output
        _,adc1_S1 = self.adc_average(samples)
        self.adc_write_reg(46,0xa) #S2 appears at ADC output
        _,adc1_S2 = self.adc_average(samples)
        self.adc_write_reg(46,0x8)
        
        self.adc_write_reg(45,0x20)#S3 appears at ADC output
        _,adc1_S3 = self.adc_average(samples,"neg")
        
        self.adc_write_reg(44,0x0)
        self.adc_write_reg(45,0x0)
        self.adc_write_reg(46,0x0)
        adc1_W0 = self.subtract(adc1_S1 + adc1_S0)
        adc1_W2 = self.subtract(adc1_S2 + adc1_S3)
        
        adc1_w0l = adc1_W0 & 0xff
        adc1_w0h = (adc1_W0 >> 8) & 0xff
        adc1_w2l = adc1_W2 & 0xff
        adc1_w2h = (adc1_W2 >> 8) & 0xff     
        self.adc.I2C_write_checked(self.chip_id,self.page,0x4c,adc1_w0l)
        self.adc.I2C_write_checked(self.chip_id,self.page,0x4d,adc1_w0h)
        self.adc.I2C_write_checked(self.chip_id,self.page,0x6c,adc1_w2l)
        self.adc.I2C_write_checked(self.chip_id,self.page,0x6d,adc1_w2h)
        #Measure S0, S1,S2 and S3 for stage 5 (most significant stage=stage0)
        self.adc_write_reg(32,0x6F)
        self.adc_write_reg(44,0x16)
        self.adc_write_reg(46,0x20) #clear
        self.adc_write_reg(46,0x0) #S0 appears at ADC output
        _,adc1_S0 = self.adc_average(samples,"neg")
        self.adc_write_reg(46,0x2) #S1 appears at ADC output
        _,adc1_S1 = self.adc_average(samples)
        self.adc_write_reg(46,0xa) #S2 appears at ADC output
        _,adc1_S2 = self.adc_average(samples)
        self.adc_write_reg(46,0x8)
        
        self.adc_write_reg(45,0x20)#S3 appears at ADC output
        _,adc1_S3 = self.adc_average(samples,"neg")
        
        self.adc_write_reg(44,0x0)
        self.adc_write_reg(45,0x0)
        self.adc_write_reg(46,0x0)
        adc1_W0 = self.subtract(adc1_S1 + adc1_S0)
        adc1_W2 = self.subtract(adc1_S2 + adc1_S3)
        
        adc1_w0l = adc1_W0 & 0xff
        adc1_w0h = (adc1_W0 >> 8) & 0xff
        adc1_w2l = adc1_W2 & 0xff
        adc1_w2h = (adc1_W2 >> 8) & 0xff     
        self.adc.I2C_write_checked(self.chip_id,self.page,0x4a,adc1_w0l)
        self.adc.I2C_write_checked(self.chip_id,self.page,0x4b,adc1_w0h)
        self.adc.I2C_write_checked(self.chip_id,self.page,0x6a,adc1_w2l)
        self.adc.I2C_write_checked(self.chip_id,self.page,0x6b,adc1_w2h)    
        #Measure S0, S1,S2 and S3 for stage 4 (most significant stage=stage0)
        self.adc_write_reg(32,0x5F)
        self.adc_write_reg(44,0x12)
        self.adc_write_reg(46,0x20) #clear
        self.adc_write_reg(46,0x0) #S0 appears at ADC output
        _,adc1_S0 = self.adc_average(samples,"neg")
        self.adc_write_reg(46,0x2) #S1 appears at ADC output
        _,adc1_S1 = self.adc_average(samples)
        self.adc_write_reg(46,0xa) #S2 appears at ADC output
        _,adc1_S2 = self.adc_average(samples)
        self.adc_write_reg(46,0x8)
        
        self.adc_write_reg(45,0x20)#S3 appears at ADC output
        _,adc1_S3 = self.adc_average(samples,"neg")
        
        self.adc_write_reg(44,0x0)
        self.adc_write_reg(45,0x0)
        self.adc_write_reg(46,0x0)
        adc1_W0 = self.subtract(adc1_S1 + adc1_S0)
        adc1_W2 = self.subtract(adc1_S2 + adc1_S3)
        
        adc1_w0l = adc1_W0 & 0xff
        adc1_w0h = (adc1_W0 >> 8) & 0xff
        adc1_w2l = adc1_W2 & 0xff
        adc1_w2h = (adc1_W2 >> 8) & 0xff     
        self.adc.I2C_write_checked(self.chip_id,self.page,0x48,adc1_w0l)
        self.adc.I2C_write_checked(self.chip_id,self.page,0x49,adc1_w0h)
        self.adc.I2C_write_checked(self.chip_id,self.page,0x68,adc1_w2l)
        self.adc.I2C_write_checked(self.chip_id,self.page,0x69,adc1_w2h)  
        
        #Measure S0, S1,S2 and S3 for stage 3 (most significant stage=stage0)
        self.adc_write_reg(32,0x4F)
        self.adc_write_reg(44,0xe)
        self.adc_write_reg(46,0x20) #clear
        self.adc_write_reg(46,0x0) #S0 appears at ADC output
        _,adc1_S0 = self.adc_average(samples,"neg")
        self.adc_write_reg(46,0x2) #S1 appears at ADC output
        _,adc1_S1 = self.adc_average(samples)
        self.adc_write_reg(46,0xa) #S2 appears at ADC output
        _,adc1_S2 = self.adc_average(samples)
        self.adc_write_reg(46,0x8)
        
        self.adc_write_reg(45,0x20)#S3 appears at ADC output
        _,adc1_S3 = self.adc_average(samples,"neg")
        
        self.adc_write_reg(44,0x0)
        self.adc_write_reg(45,0x0)
        self.adc_write_reg(46,0x0)
        adc1_W0 = self.subtract(adc1_S1 + adc1_S0)
        adc1_W2 = self.subtract(adc1_S2 + adc1_S3)        
        adc1_w0l = adc1_W0 & 0xff
        adc1_w0h = (adc1_W0 >> 8) & 0xff
        adc1_w2l = adc1_W2 & 0xff
        adc1_w2h = (adc1_W2 >> 8) & 0xff     
        self.adc.I2C_write_checked(self.chip_id,self.page,0x46,adc1_w0l)
        self.adc.I2C_write_checked(self.chip_id,self.page,0x47,adc1_w0h)
        self.adc.I2C_write_checked(self.chip_id,self.page,0x66,adc1_w2l)
        self.adc.I2C_write_checked(self.chip_id,self.page,0x67,adc1_w2h)       
        
        #Measure S0, S1,S2 and S3 for stage 2 (most significant stage=stage0)
        self.adc_write_reg(32,0x3F)
        self.adc_write_reg(44,0xa)
        self.adc_write_reg(46,0x20) #clear
        self.adc_write_reg(46,0x0) #S0 appears at ADC output
        _,adc1_S0 = self.adc_average(samples,"neg")
        self.adc_write_reg(46,0x2) #S1 appears at ADC output
        _,adc1_S1 = self.adc_average(samples)
        self.adc_write_reg(46,0xa) #S2 appears at ADC output
        _,adc1_S2 = self.adc_average(samples)
        self.adc_write_reg(46,0x8)
        self.adc_write_reg(45,0x20)#S3 appears at ADC output
        _,adc1_S3 = self.adc_average(samples,"neg")
        
        self.adc_write_reg(44,0x0)
        self.adc_write_reg(45,0x0)
        self.adc_write_reg(46,0x0)
        adc1_W0 = self.subtract(adc1_S1 + adc1_S0)
        adc1_W2 = self.subtract(adc1_S2 + adc1_S3)
        
        adc1_w0l = adc1_W0 & 0xff
        adc1_w0h = (adc1_W0 >> 8) & 0xff
        adc1_w2l = adc1_W2 & 0xff
        adc1_w2h = (adc1_W2 >> 8) & 0xff     
        self.adc.I2C_write_checked(self.chip_id,self.page,0x44,adc1_w0l)
        self.adc.I2C_write_checked(self.chip_id,self.page,0x45,adc1_w0h)
        self.adc.I2C_write_checked(self.chip_id,self.page,0x64,adc1_w2l)
        self.adc.I2C_write_checked(self.chip_id,self.page,0x65,adc1_w2h)             
        #Measure S0, S1,S2 and S3 for stage 1 (most significant stage=stage0)
        self.adc_write_reg(32,0x2F)
        self.adc_write_reg(44,0x6)
        self.adc_write_reg(46,0x20) #clear
        self.adc_write_reg(46,0x0) #S0 appears at ADC output
        _,adc1_S0 = self.adc_average(samples,"neg")
        self.adc_write_reg(46,0x2) #S1 appears at ADC output
        _,adc1_S1 = self.adc_average(samples)
        self.adc_write_reg(46,0xa) #S2 appears at ADC output
        _,adc1_S2 = self.adc_average(samples)
        self.adc_write_reg(46,0x8)
        self.adc_write_reg(45,0x20)#S3 appears at ADC output
        _,adc1_S3 = self.adc_average(samples,"neg")
        
        self.adc_write_reg(44,0x0)
        self.adc_write_reg(45,0x0)
        self.adc_write_reg(46,0x0)
        adc1_W0 = self.subtract(adc1_S1 + adc1_S0)
        adc1_W2 = self.subtract(adc1_S2 + adc1_S3)
        
        adc1_w0l = adc1_W0 & 0xff
        adc1_w0h = (adc1_W0 >> 8) & 0xff
        adc1_w2l = adc1_W2 & 0xff
        adc1_w2h = (adc1_W2 >> 8) & 0xff     
        self.adc.I2C_write_checked(self.chip_id,self.page,0x42,adc1_w0l)
        self.adc.I2C_write_checked(self.chip_id,self.page,0x43,adc1_w0h)
        self.adc.I2C_write_checked(self.chip_id,self.page,0x62,adc1_w2l)
        self.adc.I2C_write_checked(self.chip_id,self.page,0x63,adc1_w2h)   
        #Measure S0, S1,S2 and S3 for stage 0 (most significant stage=stage0)
        self.adc_write_reg(32,0x1F)
        self.adc_write_reg(44,0x2)
        self.adc_write_reg(46,0x20) #clear
        self.adc_write_reg(46,0x0) #S0 appears at ADC output
        _,adc1_S0 = self.adc_average(samples,"neg")
        self.adc_write_reg(46,0x2) #S1 appears at ADC output
        _,adc1_S1 = self.adc_average(samples)
        self.adc_write_reg(46,0xa) #S2 appears at ADC output
        _,adc1_S2 = self.adc_average(samples)
        self.adc_write_reg(46,0x8)
        self.adc_write_reg(45,0x20)#S3 appears at ADC output
        _,adc1_S3 = self.adc_average(samples,"neg")
        
        self.adc_write_reg(44,0x0)
        self.adc_write_reg(45,0x0)
        self.adc_write_reg(46,0x0)
        adc1_W0 = self.subtract(adc1_S1 + adc1_S0)
        adc1_W2 = self.subtract(adc1_S2 + adc1_S3)
        
        adc1_w0l = adc1_W0 & 0xff
        adc1_w0h = (adc1_W0 >> 8) & 0xff
        adc1_w2l = adc1_W2 & 0xff
        adc1_w2h = (adc1_W2 >> 8) & 0xff     
        self.adc.I2C_write_checked(self.chip_id,self.page,0x40,adc1_w0l)
        self.adc.I2C_write_checked(self.chip_id,self.page,0x41,adc1_w0h)
        self.adc.I2C_write_checked(self.chip_id,self.page,0x60,adc1_w2l)
        self.adc.I2C_write_checked(self.chip_id,self.page,0x61,adc1_w2h)             

    #ADC0, ADC1 calibration at the same time
    def adc_autocali(self,avr,saveflag):
        #Measure S0, S1,S2 and S3 for stage 6 (most significant stage=stage0)
        self.adc.ADC_I2C_write_checked(self.chip_id,self.page,self.adc_reg.meas_cycles,0xf) #set to maxium ADC samples
        for i in range(7):
            #print("stage = %d"%(6-i)) most significant stage =stage 0
            #samples = int(avr/math.pow(2,(6-i))) #change 16000 to avr
            samples = int(avr) #change 16000 to avr
            self.adc.ADC_I2C_write_checked(self.chip_id,self.page,self.adc_reg.cal_stages,(0x7-i))  # calibrate stage6
            tdly = 0.1
            time.sleep(tdly)
            #reg 44 setting
            self.adc.ADC_I2C_write_checked(self.chip_id,self.page,self.adc_reg.force_adc,0x3)   #force adc0,adc1
            time.sleep(tdly)
            self.adc.ADC_I2C_write_checked(self.chip_id,self.page,self.adc_reg.stage_select,(0x6-i)) #put stage6 in forcing mode
            #reg 46 setting
            time.sleep(tdly)
            self.adc.ADC_I2C_write_checked(self.chip_id,self.page,self.adc_reg.clear_reg_adc,0x3) # clear adc0,adc1 calibration registers
            time.sleep(tdly)
            self.adc.ADC_I2C_write_checked(self.chip_id,self.page,self.adc_reg.clear_reg_adc,0x0) # S0 appears at ADC0,ADC1 output
            #record an average value for S0
            time.sleep(tdly)
            
            adc0_S0,adc1_S0, adc0_s0_statics, adc1_s0_statics = self.adc_average(samples,"neg")
            self.adc.ADC_I2C_write_checked(self.chip_id,self.page,self.adc_reg.force_lsb_adc,0x3) #force adc0 LSB to 1, s1 appears at ADC0,ADC1 output
            #record an average value for S1
            time.sleep(tdly)
            adc0_S1,adc1_S1, adc0_s1_statics, adc1_s1_statics = self.adc_average(samples)
            time.sleep(tdly)
            self.adc.ADC_I2C_write_checked(self.chip_id,self.page,self.adc_reg.caldac_ctrl_adc,0x3) # S2 and S3 measurement, S2 appears at ADC0,ADC1 output 
            #record on average value for s2
            time.sleep(tdly)
            adc0_S2,adc1_S2, adc0_s2_statics, adc1_s2_statics = self.adc_average(samples)
            self.adc.ADC_I2C_write_checked(self.chip_id,self.page,self.adc_reg.force_lsb_adc,0x0) #ADC0 ADC1 back to normal mode
            #reg 45
            time.sleep(tdly)
            self.adc.ADC_I2C_write_checked(self.chip_id,self.page,self.adc_reg.force_msb_adc,0x3) #force adc0 adc1 msb to 1, S3 appears at the ADC output
        
            #record on average value for S3
            time.sleep(tdly)
            adc0_S3,adc1_S3,adc0_s3_statics, adc1_s3_statics = self.adc_average(samples,"neg")
            time.sleep(tdly)
            self.adc.ADC_I2C_write_checked(self.chip_id,self.page,self.adc_reg.force_adc,0x0)      #clear reg44
            time.sleep(tdly)
            self.adc.ADC_I2C_write_checked(self.chip_id,self.page,self.adc_reg.force_msb_adc,0x0)  #clear reg45
            time.sleep(tdly)
            self.adc.ADC_I2C_write_checked(self.chip_id,self.page,self.adc_reg.caldac_ctrl_adc,0x0)#clear reg46
            time.sleep(tdly)
            #Compute W0 = S1 + (-S0) W2 = S2 + (-S3)
            adc0_W0 = self.subtract(adc0_S1 + adc0_S0)
            adc0_W2 = self.subtract(adc0_S2 + adc0_S3)
            adc0_w0l = adc0_W0 & 0xff
            adc0_w0h = (adc0_W0 >> 8) & 0xff
            adc0_w2l = adc0_W2 & 0xff
            adc0_w2h = (adc0_W2 >> 8) & 0xff
            
            adc1_W0 = self.subtract(adc1_S1 + adc1_S0)
            adc1_W2 = self.subtract(adc1_S2 + adc1_S3)            
            adc1_w0l = adc1_W0 & 0xff
            adc1_w0h = (adc1_W0 >> 8) & 0xff
            adc1_w2l = adc1_W2 & 0xff
            adc1_w2h = (adc1_W2 >> 8) & 0xff            
            
            self.adc.I2C_write_checked(self.chip_id,self.page,(0xc-2*i),adc0_w0l)
            time.sleep(tdly)
            self.adc.I2C_write_checked(self.chip_id,self.page,(0xd-2*i),adc0_w0h)
            time.sleep(tdly)
            self.adc.I2C_write_checked(self.chip_id,self.page,(0x2c-2*i),adc0_w2l)
            time.sleep(tdly)
            self.adc.I2C_write_checked(self.chip_id,self.page,(0x2d-2*i),adc0_w2h)
            time.sleep(tdly)
            self.adc.I2C_write_checked(self.chip_id,self.page,(0x4c-2*i),adc1_w0l)
            time.sleep(tdly)
            self.adc.I2C_write_checked(self.chip_id,self.page,(0x4d-2*i),adc1_w0h)
            time.sleep(tdly)
            self.adc.I2C_write_checked(self.chip_id,self.page,(0x6c-2*i),adc1_w2l)
            time.sleep(tdly)
            self.adc.I2C_write_checked(self.chip_id,self.page,(0x6d-2*i),adc1_w2h)   

            if saveflag == "savefig":
                fileDir = os.path.dirname(__file__)#get the directory
                directory = os.path.join(fileDir,'newcalis')
                if not os.path.exists(directory):
                    os.makedirs(directory)
                else:
                    pass            
                #----------------------------#
                name = 'stage%d_time%d'%(6-i,self.plotnum)
                figname = 'ADC_stage%d_time%d'%(6-i,self.plotnum)
                figpath = os.path.join(directory,figname + '.pdf')
                with PdfPages(figpath) as pdf:
                    #save figures.
                    fig1 = plt.figure(1,figsize=(10.0,8.0))
                    fig1.add_subplot(2,2,1)
                    plt.ylabel('counts')
                    plt.title('S0')
                    plt.hist(adc0_s0_statics)
                    
                    fig1.add_subplot(2,2,2)
                    plt.ylabel('counts')
                    plt.title('S1')
                    plt.hist(adc0_s1_statics)
                    
                    fig1.add_subplot(2,2,3)
                    plt.xlabel('ADC code')
                    plt.ylabel('counts')
                    plt.title('S2')
                    plt.hist(adc0_s2_statics)
                    
                    fig1.add_subplot(2,2,4)
                    plt.xlabel('ADC code')
                    plt.ylabel('counts')
                    plt.title('S3')
                    plt.hist(adc0_s3_statics)
                    
                    pdf.savefig(fig1)
                    plt.close()            
                    
                    #Figure2
                    fig2 = plt.figure(2,figsize=(10.0,8.0))
                    fig2.add_subplot(2,2,1)
                    plt.ylabel('counts')
                    plt.title('S0')
                    plt.hist(adc1_s0_statics)
                    
                    fig2.add_subplot(2,2,2)
                    plt.ylabel('counts')
                    plt.title('S1')
                    plt.hist(adc1_s1_statics)
                    
                    fig2.add_subplot(2,2,3)
                    plt.xlabel('ADC code')
                    plt.ylabel('counts')
                    plt.title('S2')
                    plt.hist(adc1_s2_statics)
                    
                    fig2.add_subplot(2,2,4)
                    plt.xlabel('ADC code')
                    plt.ylabel('counts')
                    plt.title('S3')
                    plt.hist(adc1_s3_statics)         
                    pdf.savefig(fig2)
                    plt.close()   
                #record file    
                filename = os.path.join(directory,name+'.txt')
                file = open(filename,"a+")
                file.write("#    ADC0 stage%d         ADC1 stage%d\n"%(6-i,6-i))
                file.write("# S0, S1, S2, S3; S0, S1, S2, S3\n")      
    
                for i in range(len(adc0_s0_statics)):
                    file.write("%d,%d,%d,%d,%d,%d,%d,%d\n"%(adc0_s0_statics[i],adc0_s1_statics[i],adc0_s2_statics[i],adc0_s3_statics[i],adc1_s0_statics[i],adc1_s1_statics[i],adc1_s2_statics[i],adc1_s3_statics[i]))                   
                file.close()   
              
        self.plotnum = self.plotnum+1    
        #Plot ---histogram
    def adc_read_weights(self):
        reg=[]
        val=[]
        #read weights from ADC0
        for addr in range(0,0xe,1):    
            value = self.adc.I2C_read(self.chip_id,self.page,addr)
            value = self.adc.I2C_read(self.chip_id,self.page,addr)
            reg.append(addr)
            val.append(value)
            
        for addr in range(0x20,0x2e,1):
            value = self.adc.I2C_read(self.chip_id,self.page,addr)
            value = self.adc.I2C_read(self.chip_id,self.page,addr)
            reg.append(addr)
            val.append(value)
            
        #read weights from ADC1    
        for addr in range(0x40,0x4e,1):
            value = self.adc.I2C_read(self.chip_id,self.page,addr)
            value = self.adc.I2C_read(self.chip_id,self.page,addr)
            reg.append(addr)
            val.append(value)            
        
        for addr in range(0x60,0x6e,1):
            value = self.adc.I2C_read(self.chip_id,self.page,addr)
            value = self.adc.I2C_read(self.chip_id,self.page,addr)
            reg.append(addr)
            val.append(value)
        return reg, val
    
    def adc_load_weights(self,reg,val):
        # load weights for ADC
        if (len(reg) != len(val)):
            print("loading error")
        else:
            for i in range(len(reg)):
                self.adc.I2C_write_checked(self.chip_id,self.page,reg[i],val[i])
                time.sleep(0.05)

    def adc_read_config_regs(self):
        page1_reg=[]
        page1_val=[]
        for i in range(55):
            regaddr=0x80+i
            regval = self.adc.I2C_read(self.chip_id,self.page,regaddr)
            page1_reg.append(i)
            page1_val.append(regval)            
            #time.sleep(0.05)
            
        page2_reg=[]
        page2_val=[]
        
        for reg in [1,2,3]:
            regval = self.adc.I2C_read(self.chip_id,2,reg)
            page2_reg.append(reg)
            page2_val.append(regval)
            #time.sleep(0.05)
        
        return [page1_reg,page1_val,page2_reg,page2_val]
    
#--------functions for COTS ADC-------------#
    #BJT reference monitor output selection
    def cots_adc_bjt_mon_src(self,src):
        if src == "None":
            reg20=0x0
            reg21=0x0
        elif src == "VREF_ext":
            reg20=0x1
            reg21=0x0
        elif src == "VREFN":
            reg20=0x2
            reg21=0x0
            self.dac_reg = 11
        elif src == "VREFP":
            reg20=0x4
            reg21=0x0
            self.dac_reg = 10
        elif src == "VCMI":
            reg20=0x8
            reg21=0x0
            self.dac_reg = 13
        elif src == "VCMO":
            reg20=0x10
            reg21=0x0
            self.dac_reg = 12
        elif src == "VBGR_1.2V":
            reg20=0x0
            reg21=0x80
        elif src == "Vdac0_5k":
            reg20=0x20
            reg21=0x0
            self.dac_reg = 17
        elif src == "Vdac1_5k":
            reg20=0x40
            reg21=0x0
            self.dac_reg = 18
        elif src == "ibuff0_5k":
            reg20=0x80
            reg21=0x0
            self.dac_reg = 15
        elif src == "ibuff1_5k":
            reg20=0x0
            reg21=0x1
            self.dac_reg = 16
        elif src == "Isink_adc1_5k":
            reg20=0x0
            reg21=0x2
        elif src == "Isink_adc0_5k":
            reg20=0x0
            reg21=0x4
        elif src == "Isink_sha1_5k":
            reg20=0x0
            reg21=0x8
        elif src == "Isink_sha0_5k":
            reg20=0x0
            reg21=0x10
        elif src == "Isink_refbuf0_5k":
            reg20=0x0
            reg21=0x20
        elif src == "Isink_refbuf1_5k":
            reg20=0x0
            reg21=0x40
        self.adc.ADC_I2C_write(self.chip_id,self.page,self.adc_reg.ref_monitor_L,reg20)
        self.adc.ADC_I2C_write(self.chip_id,self.page,self.adc_reg.ref_monitor_H,reg21)
    #MUX output selection
    def cots_adc_mux_mon_src(self,src):
        if src == "AUX_ISINK":
            val = 0
        elif src == "AUX_VOLTAGE":
            val = 1
        elif src == "AUX_ISOURCE":
            val = 2
        elif src == "VOLTAGE_MON":
            val = 3
        elif src == "CURRENT_MON":
            val = 4    
        self.udp.write(self.fpga_reg.MUX_ADDR,val)
    #Vmonitor enable    
    def cost_adc_v_mon_ena(self,val):
        self.adc.ADC_I2C_write(self.chip_id,self.page,self.adc_reg.vmonitor_enable,val)
    #Imonitor enable    
    def cost_adc_i_mon_ena(self,val):
        self.adc.ADC_I2C_write(self.chip_id,self.page,self.adc_reg.imonitor_enable,val)
    # Vmonitor select
    def cost_adc_v_mon_select(self,src):
        if src == "VBGR":
            val = 0
        elif src == "VCMI":
            val = 1
            self.dac_reg = 27
        elif src == "VCMO":
            val = 2
            self.dac_reg = 26
        elif src == "VREFP":
            val = 3
            self.dac_reg = 24
        elif src == "VREFN":
            val = 4
            self.dac_reg = 25
        elif src == "VSSA":
            val = 6
        self.adc.ADC_I2C_write(self.chip_id,self.page,self.adc_reg.vmonitor_select,val)
    # Imonitor select
    def cost_adc_i_mon_select(self,src):
        if src == "ICMOS_REF_5k":
            val = 0
        elif src == "ISHA0_5k":
            val = 1
        elif src == "IADC0_5k":
            val = 2
        elif src == "ISHA1_5k":
            val = 3
        elif src == "IADC1_5k":
            val = 4
        elif src == "IBUFF_CMOS":
            val = 5
            self.dac_reg = 29
        elif src == "IREF_5k":
            val = 6
        elif src == "IREFBUFFER0":
            val = 7
        self.adc.ADC_I2C_write(self.chip_id,self.page,self.adc_reg.imonitor_select,val)
    #Read ADC data
    def cots_adc_data(self,avr):
        result = 0
        for i in range(avr):
            self.udp.write(self.fpga_reg.cots_adc_start,1)
            #time.sleep(0.1)
            check_done =1
            while(check_done):
                check_done = self.udp.read(self.fpga_reg.cots_adc_busy)
                #print(self.udp.read(self.fpga_reg.i2c_ack_error))
            temp = self.udp.read(self.fpga_reg.cost_adc_data)
            self.udp.write(self.fpga_reg.cots_adc_start,0)
            result = result + temp
            time.sleep(0.3)
        else:
            code = result / avr
            amp = int(code)
            #---conversion---#
            amp = code * 2.5 / 4096
        return amp    
    
    
    def __init__(self):
        self.udp = UDP()
        
        self.fpga_reg = FPGA_REG()
        self.fe_reg = FE_REG()
        self.adc = COLDADC_tool()
        self.adc_reg = ADC_REG()
        self.chip_id = 4
        self.page = 1
        self.user = User_defined()
        
        #---parameter settings as a default----#
        #---------FE_channel------------------#
        self.sts = [self.user.Input['Direct_Input']]*16
        self.snc = [self.user.Baseline['900mV']]*16
        self.sg  = [self.user.Gain['14mV/fC']]*16
        self.st  = [self.user.Peaktime['2us']]*16
        self.smn = [self.user.Mon['off']]*16
        self.sbf = [self.user.Buffer['off']]*16
        #---------FE global----------------#
        self.sdacsw = self.user.Pulse['Disable']
        self.sdc    = self.user.Coupled['DC']
        self.slkh = (self.user.Leakage['500pA'] & 0x2) >> 1
        self.s16 = self.user.S16['Disconnect']
        self.stb = self.user.Monitor['Analog']
        self.slk = self.user.Leakage['500pA'] & 0x1
        self.sdac = 0x5
        #-------------------------------------#
        self.dac_reg = 0
        self.cmos_dac_reg=0
        self.plotnum=0
        
## Start Qt Event
if __name__ == '__main__':
    brd_config = Brd_Config()
    for times in range(5,6,1):
        brd_config.adc_autocali_test(10000,times)


