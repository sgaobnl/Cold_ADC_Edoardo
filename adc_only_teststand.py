# -*- coding: utf-8 -*-
"""
Created on Wed Sep  4 11:01:02 2019

@author: Edoardo Lopriore
"""

from brd_config import Brd_Config
import time
from frame import Frames
import numpy as np
from raw_data_decoder import raw_conv
from matplotlib.backends.backend_pdf import PdfPages
import csv 

status = "PASS"
err_str = "ERROR LOG: \n"
class ADC_only:
    def err_log(self, s):
        err_str += s
    
    
    def __init__(self):
#        self.word_order = 0
        self.bc = Brd_Config()

    def pwr_chk(self):
        
    

    def i2c_chk(self):
        self.bc.Acq_start_stop(0)
        self.bc.adc_write_reg(1, 0x22)
        i2c_write = self.bc.adc_read_reg(1)
        if (i2c_write != '0x22'):
            status = "FAIL"
            err_log("I2C check failed. Read/Write not working correctly. \n")        


    def uart_chk(self):
#        self.bc.Acq_start_stop(0)
        self.bc.adc_i2c_uart("UART")
        self.bc.adc_write_reg(1, 0x22)
        uart_write = self.bc.adc_read_reg(1)
        if (uart_write != '0x22'):
            status = "FAIL"
            err_log("UART check failed. Read/Write not working correctly. \n")   
            
    
    def pattern_chk(self):
        self.bc.adc.hard_reset()
        adc0_h = self.bc.adc_read_reg(52)
        adc0_l = self.bc.adc_read_reg(51)
        if (adc0_h != '0xab' or adc0_l != '0xcd'):
            err_log("ADC0 Configuration Pattern: unexpected value \n")
        adc1_h = self.bc.adc_read_reg(54)
        adc1_l = self.bc.adc_read_reg(53)
        if (adc1_h != '0x12' or adc1_l != '0x34'):
            status = "FAIL"
            err_log("ADC1 Configuration Pattern: unexpected value \n")
            
    
    def regs_chk(self):
        self.bc.adc.hard_reset()
        reg = []
        default = [0x52, 0x00, 0x00, 0x00, 0x33, 0x33, 0x33, 0x0a, 0x00, 0x00,
                   0xfa, 0x3a, 0x9a, 0x73, 0xff, 0x99, 0x99, 0x99, 0x99, 0x00,
                   0x00, 0x00, 0x00, 0x00, 0x30, 0x00, 0x00, 0x00, 0x0c, 0x27,
                   0x27, 0x00, 0x7f, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                   0x00, 0x00, 0xa5, 0xca, 0x00, 0x00, 0x00, 0x00, 0x07, 0x00,
                   0x00, 0xcd, 0xab, 0x34, 0x12]
        for i in range(0,50):
            reg.append(i) = self.bc.adc_read_reg(i)
            if(reg[i] != default[i]):
                status = "FAIL"
                err_log("Register %d value %x1 instead of default value %x2 \n"%(i, reg[i], default[i]))

    def ref_vmon(self, vmon = "VBGR", avg_points =5  ):
        self.bc.cots_adc_mux_mon_src(src = "VOLTAGE_MON")
        self.bc.cost_adc_v_mon_ena(1)
        self.bc.cost_adc_v_mon_select(vmon)
        self.bc.cots_adc_data(avr = 2)
        val = self.bc.cots_adc_data(avr = avg_points)
        self.bc.cost_adc_v_mon_ena(0)
        #print ("MUX = VOLTAGE_MON, %s = %f"%( vmon, val))
        return val
    
    def ref_vmons(self ):
        vcmi  = cq.ref_vmon(vmon = "VCMI"  )
        vcmo  = cq.ref_vmon(vmon = "VCMO"  )
        vrefp = cq.ref_vmon(vmon = "VREFP" )
        vrefn = cq.ref_vmon(vmon = "VREFN" )
        return (vcmi, vcmo, vrefp, vrefn)
   
    def bjt_ref_aux(self, imon = "ibuff0_5k", avg_points =5  ):
        self.bc.cots_adc_mux_mon_src(src = "AUX_ISOURCE")
        self.bc.cots_adc_bjt_mon_src(imon) 
        self.bc.cots_adc_data(avr = 2)
        val = self.bc.cots_adc_data(avr = avg_points)
        return val
    
    
    
    def ref_imon(self, imon = "ICMOS_REF_5k", avg_points =5  ):
        self.bc.cots_adc_mux_mon_src(src = "CURRENT_MON")
        self.bc.cost_adc_i_mon_ena(1)
        self.bc.cost_adc_i_mon_select(imon)
        self.bc.cots_adc_data(avr = 2)
        val = self.bc.cots_adc_data(avr = avg_points)
        self.bc.cost_adc_i_mon_ena(0)
        return val
    
    
    def refs_chk(self, flg_bjt_r = True):
        avgs = 10
        if (flg_bjt_r):
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
            if(vbgr > 1.3 or vbgr < 1.1):
                status = "FAIL"
                err_log("Bandgap Reference out of expected range: VBGR = %0.3f \n"%(vbgr))
            self.bc.adc_set_ioffset(vrefp_ioft, vrefn_ioft, vcmo_ioft, vcmi_ioft)
            for i in range (avgs):
                if(i==0):
                    for i in range (256):
                        self.bc.adc_set_vrefs(i, i, i, i)
                        vcmi_bjt.append(i), vcmo_bjt.append(i), vrefp_bjt.append(i), vrefn_bjt.append(i) = self.ref_vmons()
                        self.bc.adc_set_curr_ibuff(i, i)
                        ibuff0_bjt.append(i) = self.bjt_ref_aux("ibuff0_5k")
                        ibuff1_bjt.append(i) = self.bjt_ref_aux("ibuff1_5k")
                        self.bc.adc_set_curr_vdac(i, i)
                        ivdac0_bjt.append(i) = self.bjt_ref_aux("Vdac0_5k")
                        ivdac1_bjt.append(i) =self.bjt_ref_aux("Vdac1_5k")     
                else:
                    for i in range (256):
                        self.bc.adc_set_vrefs(i, i, i, i)
                        vcmi_bjt.append(i), vcmo_bjt.append(i), vrefp_bjt.append(i), vrefn_bjt.append(i) += self.ref_vmons()
                        self.bc.adc_set_curr_ibuff(i, i)
                        ibuff0_bjt.append(i) += self.bjt_ref_aux("ibuff0_5k")
                        ibuff1_bjt.append(i) += self.bjt_ref_aux("ibuff1_5k")
                        self.bc.adc_set_curr_vdac(i, i)
                        ivdac0_bjt.append(i) += self.bjt_ref_aux("Vdac0_5k")
                        ivdac1_bjt.append(i) += self.bjt_ref_aux("Vdac1_5k")     
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
            self.bc.adc_ref_vol_src("CMOS")
            self.bc.adc_bias_curr_src("CMOS")
            vrefp_cmos = []
            vrefn_cmos = []
            vcmi_cmos = []
            vcmo_cmos = []
            ibuff_cmos = []
            for i in range (avgs):
                if (i==0):
                    for i in range (256):
                        self.bc.adc_set_vrefs(i, i, i, i)
                        vcmi_cmos.append(i), vcmo_cmos.append(i), vrefp_cmos.append(i), vrefn_cmos.append(i) = self.ref_vmons()
                        self.bc.adc_set_curr_ibuff(i, i)
                        ibuff_cmos  = self.ref_imon(imon = "IBUFF_CMOS")     
                else:
                    for i in range (256):
                        self.bc.adc_set_vrefs(i, i, i, i)
                        vcmi_cmos.append(i), vcmo_cmos.append(i), vrefp_cmos.append(i), vrefn_cmos.append(i) += self.ref_vmons()
                        self.bc.adc_set_curr_ibuff(i, i)
                        ibuff_cmos  += self.ref_imon(imon = "IBUFF_CMOS")       
            vrefp_cmos[:] = [x / avgs for x in vrefp_cmos]
            vrefn_cmos[:] = [x / avgs for x in vrefn_cmos]
            vcmi_cmos[:] = [x / avgs for x in vcmi_cmos]
            vcmo_cmos[:] = [x / avgs for x in vcmo_cmos]
            ibuff_cmos[:] = [x / avgs for x in ibuff_cmos]
            return (vrefp_cmos, vrefn_cmos, vcmi_cmos, vcmo_cmos, ibuff_cmos)
       
    
    def ref_set(self, flg_bjt_r = True, env = "RT" ):
        if (flg_bjt_r):
            self.bc.adc_ref_vol_src("BJT")
            self.bc.adc_bias_curr_src("BJT")
            if (env == "RT"):
                vrefp_voft = 0xe1#0xe4#0xf0#0xf8#0xe4
                vrefn_voft = 0x27#0x08#0x10#0x24
                vcmi_voft = 0x60#0x60#0x50#0x60
                vcmo_voft = 0x82#0x82
                vrefp_ioft = 1
                vrefn_ioft = 1
                vcmi_ioft = 1
                vcmo_ioft = 1
            else:
                vrefp_voft = 0xeb#0xf1
                vrefn_voft = 0x2b#0x29
                vcmi_voft = 0x64#0x65
                vcmo_voft = 0x7c#0x8d
                vrefp_ioft = 1
                vrefn_ioft = 1
                vcmi_ioft = 1
                vcmo_ioft = 1
            self.bc.adc_set_vrefs(vrefp_voft, vrefn_voft, vcmo_voft, vcmi_voft )
            self.bc.adc_set_ioffset(vrefp_ioft, vrefn_ioft, vcmo_ioft, vcmi_ioft)
            ibuff0_15 = 0x99
            ibuff1_16 = 0x99
            ivdac0_17 = 0x99
            ivdac1_18 = 0x99
            self.bc.adc_set_curr_ibuff(ibuff0_15, ibuff1_16)
            self.bc.adc_set_curr_vdac(ivdac0_17, ivdac1_18)
        else:
            self.bc.adc_ref_vol_src("CMOS")
            self.bc.adc_bias_curr_src("CMOS_INTR")
            if (env == "RT"):
                vrefp_voft = 0xcc#0xce
                vrefn_voft = 0x2b
                vcmi_voft = 0x5b
                vcmo_voft = 0x7b
            else:
                vrefp_voft = 0xc6
                vrefn_voft = 0x30
                vcmi_voft = 0x5b
                vcmo_voft = 0x7b
            self.bc.adc_set_cmos_vrefs(vrefp_voft, vrefn_voft, vcmi_voft, vcmo_voft) 
            iref_trim = 50
            self.bc.adc_set_cmos_iref_trim(iref_trim)
            ibuff0_cmos = 0x27
            ibuff1_cmos = 0x27
            self.bc.adc_set_cmos_ibuff(ibuff0_cmos, ibuff1_cmos)


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

    def get_adcdata(self, PktNum=128 ):
        self.bc.Acq_start_stop(1)
        rawdata = self.bc.get_data(PktNum,1, Jumbo="Jumbo") #packet check
        self.bc.Acq_start_stop(0)
        frames_inst = Frames(PktNum,rawdata)     
        frames = frames_inst.packets()
        #Change it to emit all 16 channels data 
        chns=[[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]] #16-bit
        for i in range(PktNum):
            for j in range(16): #16 channels
                chns[j].append(frames[i].ADCdata[j]) 
        return chns 
    
    def get_adcdata_raw(self, PktNum=128 ):
        self.bc.Acq_start_stop(1)
        rawdata = self.bc.udp.get_pure_rawdata(PktNum+1000 )
        self.bc.Acq_start_stop(0)
#        rawdata = self.bc.get_data(PktNum,1, Jumbo="Jumbo") #packet check
        return rawdata      
    
    def chn_order_sync(self, PktNum=128 ):  
#        print ("Starting ADC physical channel and logical channel mapping...")
        self.bc.adc_load_pattern_0(0x01, 0x01)
        self.bc.adc_load_pattern_1(0x01, 0x01)
        woc_f = False
        for chn_order in range(32):
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
                chns = self.get_adcdata(PktNum=128)
                for i in range(1):
                    chns = self.get_adcdata(PktNum=128)
                    tmp = []
                    for tmpx in chns:
                        tmp.append(tmpx[1])
                    print (tmp)
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
#                    print ("ADC chn order is %d"%chn_order)
#                    print ("ADC physical channel and logical channel mapping is done")
                    break
            else:
                woc_f = False
                status = "FAIL"
                err_log("ADC output synchronization failed \n")
                pass
        return woc_f

    
    def record_weights(self, reg, val):
        # field names 
        fields = ['Register', 'Branch', 'Year', 'CGPA'] 
          
        # data rows of csv file 
        rows = [ ['Nikhil', 'COE', '2', '9.0'], 
                 ['Sanchit', 'COE', '2', '9.1'], 
                 ['Aditya', 'IT', '2', '9.3'], 
                 ['Sagar', 'SE', '1', '9.5'], 
                 ['Prateek', 'MCE', '3', '7.8'], 
                 ['Sahil', 'EP', '2', '9.1']] 
          
        # name of csv file 
        filename = "university_records.csv"
          
        # writing to csv file 
        with open(filename, 'w') as csvfile: 
            # creating a csv writer object 
            csvwriter = csv.writer(csvfile) 
              
            # writing the fields 
            csvwriter.writerow(fields) 
              
            # writing the data rows 
            csvwriter.writerows(rows)
    

    def init_checkout(self, env = "RT"):
        self._init_()
        self.pwr_chk()
        self.i2c_chk()
        self.uart_chk()
        self.pattern_chk()
        self.regs_chk()
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
        vrefp_bjt, vrefn_bjt, vcmi_bjt, vcmo_bjt, ibuff0_bjt, ibuff1_bjt, ivdac0, ivdac1 = self.refs_chk(flg_bjt_r = True)
        vrefp_cmos, vrefn_cmos, vcmi_cmos, vcmo_cmos, ibuff_cmos = self.refs_chk(flg_bjt_r = False)
        
        
        #plot vrefs 
        
        self.ref_set(flg_bjt_r = True, env=env)
        time.sleep(1)
        self.Input_buffer_cfg(sdc = "Bypass", db = "Bypass", sha = "Single-ended", curr_src = "BJT-sd")
        self.bc.adc_sha_clk_sel(mode = "internal")
        self.Converter_Config(edge_sel = "Normal", out_format = "offset binary", 
                         adc_sync_mode ="Analog pattern", adc_test_input = "Normal", 
                         adc_output_sel = "cali_ADCdata", adc_bias_uA = 50)
        self.bc.udp.clr_server_buf()
        self.chn_order_sync()
        
        #BJT calibration weights
        self.Converter_Config(edge_sel = "Normal", out_format = "two-complement", 
                         adc_sync_mode ="Normal", adc_test_input = "Normal", 
                         adc_output_sel = "cali_ADCdata", adc_bias_uA = 50)
        self.bc.udp.clr_server_buf()
        self.bc.adc_autocali(avr=20000,saveflag="undef")
        self.Converter_Config(edge_sel = "Normal", out_format = "offset binary", 
                         adc_sync_mode ="Analog pattern", adc_test_input = "Normal", 
                         adc_output_sel = "cali_ADCdata", adc_bias_uA = 50)
        reg, weight_bjt = self.bc.adc_read_weights
        self.record_weights(reg, weight_bjt)
    
    
        #CMOS calibration weights
        self.ref_set(flg_bjt_r = False, env=env)
        self.Converter_Config(edge_sel = "Normal", out_format = "two-complement", 
                         adc_sync_mode ="Normal", adc_test_input = "Normal", 
                         adc_output_sel = "cali_ADCdata", adc_bias_uA = 50)
        self.bc.udp.clr_server_buf()
        self.bc.adc_autocali(avr=20000,saveflag="undef")
        self.Converter_Config(edge_sel = "Normal", out_format = "offset binary", 
                         adc_sync_mode ="Analog pattern", adc_test_input = "Normal", 
                         adc_output_sel = "cali_ADCdata", adc_bias_uA = 50)
        reg, weight_cmos = self.bc.adc_read_weights
        self.record_weights(reg, weight_cmos)
    
    