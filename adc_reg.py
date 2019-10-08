# -*- coding: utf-8 -*-
"""
Created on Wed Jan 23 12:15:17 2019

@author: JunbinZhang
"""
#==================register map==============#
#Version 1.9 corresponding to datasheet Revision 1.9 -- 03/06/2019
#=====COLD ADC Registers=====#
#=1= REGISTER FILE ADC0(address:3F-00)
# 00-1D ADC0, W0 (0x0,0x1,0x2,0x3,0x4,0x5,0x6,0x7,0x8,0x9,0xa,0xb,0xc,0xd)               w0l,w0h
# 1E-1F ADC0, Gain
# 20-3D ADC0, W2 (0x20,0x21,0x22,0x23,0x24,0x25,0x26,0x27,0x28,0x29,0x2a,0x2b,0x2c,0x2d) w2l,w2h
# 3E-3F ADC0 Offset

#=2= REGISTER FILE ADC1(address:7F-40)
# 40-5D ADC1, w0 (0x40,0x41,0x42,0x43,0x44,0x45,0x46,0x47,0x48,0x49,0x4a,0x4b,0x4c,0x4d) w0l,w0h
# 5E-5F ADC1, Gain
# 60-7D ADC1, W2 (0x60,0x61,0x62,0x63,0x64,0x65,0x66,0x67,0x68,0x69,0x6a,0x6b,0x6c,0x6d) w2l,w2h
# 7E-7F ADC1, Offset
#=3= REGISTER FILE CONFIG(address:FF-80)

class ADC_REG:
    def __init__(self):
        #input-buffer configuration
        self.ibuff_sdc_pd   = [0x80,0x1] #1 bit,  0 -> power up signal-to-differential converter in the input buffer. 1-> bypass
        self.ibuff_diff_pd  = [0x80,0x2] #1 bit,  0 -> power up differential buffer, 1-> bypass
        self.ibuff_ctrl     = [0x80,0xf0]#4 bits, BJT or CMOS reference see the datasheet
        
        #Sample-and-Hold (SHA) Amplifier Configuration
        self.freeze_sha0    = [0x81,0x1] #1 bit   0-> normal operation, 1-> Freeze increment of SHA
        self.freeze_sha1    = [0x81,0x2] #1 bits, 0-> normal operation, 1-> Freeze increment of SHA  [1:0] -> ADC1,ADC0
        self.freeze_select0 = [0x81,0x1c]#3 bits, select which SHA is connected to ADC0 when frozen. eg: 000-> SHA0, 001 -> SHA1
        self.freeze_select1 = [0x81,0xe0]#3 bits, select which SHA is connected to ADC1 when frozen
        
        self.sha_pd_0       = [0x82,0xff]#1 bit, Power down individual SHAs associated with ADC0. 0 -> normal operation, 1-> power down SHA
        
        self.sha_pd_1       = [0x83,0xff]#1 bit1, Power down individual SHAs associated with ADC1.
        
        self.sha0_bias      = [0x84,0x7] #3 bits, Bias adjustment for SHA0. SHA bias current is nominally 80uA-10uA*sha0_bias
        self.sha_se_input   = [0x84,0x8] #1 bit, 0-> SHA input is treated as fully differential, 1-> single-ended.
        
        self.sha1_bias      = [0x84,0x70]#3 bits, Bias adjustment for SHA1. SHA bias current is nominally 80uA-10uA*sha1_bias        
        self.sha2_bias      = [0x85,0x7] #3 bits, Bias adjustment for SHA2. SHA bias current is nominally 80uA-10uA*sha2_bias
        self.sha3_bias      = [0x85,0x70]#3 bits, Bias adjustment for SHA3. SHA bias current is nominally 80uA-10uA*sha3_bias
        self.sha4_bias      = [0x86,0x7] #3 bits, Bias adjustment for SHA4. SHA bias current is nominally 80uA-10uA*sha4_bias
        self.sha5_bias      = [0x86,0x70]#3 bits, Bias adjustment for SHA5. SHA bias current is nominally 80uA-10uA*sha5_bias
        self.sha6_bias      = [0x87,0x7] #3 bits, Bias adjustment for SHA6. SHA bias current is nominally 80uA-10uA*sha6_bias
        self.sha7_bias      = [0x87,0x70]#3 bits, Bias adjustment for SHA7. SHA bias current is nominally 80uA-10uA*sha7_bias
        
        self.clk_sha_select = [0x87,0x80]#1 bit, 0 -> use SHA clock sent from Cold ADC backend logic, 1-> use internally generated SHA clock
        
        #Analog-to-Digital Converter Configuration
        self.adc_bias       = [0x88,0x7] #3 bits, Bias adjustment for ADC. ADC bias current is nominally 80uA-10uA*adc_bias
        self.nonov_ctrl     = [0x88,0x18]#2 bits, Allows adjustment of non-overlap time of ADC clocks, use to adjust timing across temperature.
        self.edge_select    = [0x88,0x20]#1 bit, Choose edge of master clock to re-time data. 0-> nominal edge, 1-> 180 out of phase in case of gross clock skew errors.
        
        self.adc_pd         = [0x89,0x3] #2 bits, 0 -> normal operation, 1 -> power down ADC. [1:0] -> [ADC1,ADC0]
        self.adc_disable_gb = [0x89,0x4] #1 bit, 0 -> normal operation, 1-> Gain boosting amplifiers in the ADC MDACs disabled
        self.adc_output_format=[0x89,0x8]#1 bit, Choose format of ADC output codes. 0 -> 2's complement, 1-> offset binary
        self.adc_sync_mode  = [0x89,0x10]#1 bit, 0-> normal operation, 1-> send out known analog pattern for synchronization
        
        self.adc_test_mode  = [0x89,0x20]#1 bit, 0-> normal operation, 1-> ADC converts signal applied to ADC_TEST_INPUT pads
        self.adc_output_select=[0x89,0xc0]#2 bits, selects What ADC output is sent off-chip. 00-> calibrated ADC data, 01-> uncalibrated ADC data, 10-> raw ADC0, 11-> raw ADC1
        
        #BJT-Based Reference Generation Block
        self.vrefp_ctrl      = [0x8a,0xff] #8 bits, Setting to Generate VREFP. Default VREFP is 1.95V
        self.vrefn_ctrl      = [0x8b,0xff] #8 bits, Setting to Generate VREFN. Default VREFN is 0.45V
        self.vcmo_ctrl       = [0x8c,0xff] #8 bits, Setting to Generate VCMO.  Default VCMO is 1.2V
        self.vcmi_ctrl       = [0x8d,0xff] #8 bits, Setting to Generate VCMI.  Default VCMI is 0.9V
        self.vrefp_offset    = [0x8e,0x3]  #2 bits, Adjusts ioffset for VREFP DAC, ioffset= 0-> 9.5pA, 1-> 6.3uA, 2 -> 9.5uA, 3-> 12.6uA.
        self.vrefn_offset    = [0x8e,0xc]  #2 bits, Adjusts ioffset for VREFN DAC, ioffset= 0-> 9.5pA, 1-> 6.3uA, 2 -> 9.5uA, 3-> 12.6uA.
        self.vcmo_offset    =  [0x8e,0x30] #2 bits, Adjusts ioffset for VCMO DAC,  ioffset= 0-> 9.5pA, 1-> 6.3uA, 2 -> 9.5uA, 3-> 12.6uA.
        self.vcmi_offset    =  [0x8e,0xc0] #2 bits, Adjusts ioffset for VCMI DAC,  ioffset= 0-> 9.5pA, 1-> 6.3uA, 2 -> 9.5uA, 3-> 12.6uA.
               
        self.ibuff0_ctrl     = [0x8f,0xff] #8 bits, 200uA nominal current source for input buffer #15
        self.ibuff1_ctrl     = [0x90,0xff] #8 bits, 200uA nominal current source for input buffer #16
        
        self.i_vdac_0_ctrl   = [0x91,0xff] #8 bits, 200uA nominal current source for VDAC. Current is 2 uA #17
        self.i_vdac_1_ctrl   = [0x92,0xff] #8 bits, 200uA nominal current source for VDAC. Current is 2 uA #18   
        
        self.external_reference=[0x93,0x1] #1 bit, 0->internal references used, 1-> external references used.
        self.external_bgr    = [0x93,0x2]  #1 bit, 0->internal bandgap reference used, 1-> external bandgap reference used.
        self.bgr_select      = [0x93,0x4]  #1 bit, Selects which circuit is providing bandgap voltage. 0->BJT-based reference, 1->CMOS-based reference
        self.ref_monitor_L   = [0x94,0xff] #8 bits, LOW byte for reference monitor block control. Each control bit is active high. Each bit corresponds to a different control
        #bit 0 -> VREF           on AUX1
        #bit 1 -> VREFN_BJT_EXT  on AUX1
        #bit 2 -> VREFP_BJT_EXT  on AUX1
        #bit 3 -> VCMO_BJT_EXT   on AUX1
        #bit 4 -> VCMI_BJT_EXT   on AUX1 = AUX_VOLTAGE
        #bit 5 -> Isource_vdac0  on AUX3 = AUX_ISOURCE
        #bit 6 -> Isource_vdac1  on AUX3
        #bit 7 -> Isource_ibuff0 on AUX3
        self.ref_monitor_H   = [0x95,0xff]#8 bits,High byte for reference monitor block control 
        #bit 0 -> Isource_ibuff1 on AUX3
        #bit 1 -> Isink_adc1     on AUX2 = AUX_CURRENT
        #bit 2 -> Isink_adc0     on AUX2
        #bit 3 -> Isink_sha1     on AUX2
        #bit 4 -> Isink_sha0     on AUX2
        #bit 5 -> Isink_refbuffers_0 on AUX2
        #bit 6 -> Isink_refbuffers_1 on AUX2
        #bit 7 -> VBGR on AUX1        
        self.ref_powerdown_L = [0x96,0xff]#8 bits, Power down low byte for reference blocks
        self.ref_powerdown_H = [0x97,0xf] #4 bits, Power down high nibble for reference blocks
        self.ref_bias        = [0x97,0x70]#3 bits, Bias adjustment for ADC reference buffers. Bias current is nominally 80uA-10uA*ref_bias
        
        #CMOS Reference Generation configuration (bgr_select=1)
        self.vrefp_ctrl_cmos = [0x98,0xff] #8 bits, Setting for VREFP(in case CMOS reference is desired)
        self.vrefn_ctrl_cmos = [0x99,0xff] #8 bits, Setting for VREFN
        self.vcmo_ctrl_cmos  = [0x9a,0xff] #8 bits, setting for VCMO
        self.vcmi_ctrl_cmos  = [0x9b,0xff] #8 bits, setting for VCMI
        
        self.iref_sel        = [0x9c,0x3]  #2 bits, Choose where chip bias current generated by the CMOS reference generator come from
        self.vt_iref_trim_ctrl=[0x9c,0x1c] #3 bits, Trim for vt-referenced currents. Nominally the vt-reference current will be.
        
        #self.vt_kickstart    = [0x9c,0x20] #1 bit, Forces CMOS reference away from zero-current state.
        self.ibuff0_cmos     = [0x9d,0x3f] #6 bits, Bias current setting for nominal 200uA source for the input buffers
        self.ibuff1_cmos     = [0x9e,0x3f] #6 bits, Bias current setting for nominal 200uA source for the input buffers
        
        #Calibration Engine configuration
        self.calibrate           =[0x9f,0x3] #2 bits, Triggers calibration. 0-> normal operation, 1-> initiate calibration sequence, Must return to 0 before another calibration can be started.
        self.load_cal_defaults   =[0x9f,0x4] # 1 bit, 0-> normal operation, 1-> restore calibration weights to default, Restores calibration weights to default state
        self.load_config_defaults=[0x9f,0x8] #1 bit, 0-> normal operation 1-> restore configuration settings to default
        
        self.meas_cycles     = [0xa0,0xf] #4 bits, Number of ADC samples taken for each measurement.
        self.cal_stages      = [0xa0,0x70]#3 bits, Number of ADC stages to calibrate. Maximum 7 stages
        self.test_correction_logic=[0xa0,0x80]#1 bit, puts correction logic into test mode.
        self.test_lsb0_L     = [0xa1,0xff] # 8 bits, low byte for correction logic test word, ADC0
        self.test_lsb0_H     = [0xa2,0x7f] # 7 bits, high byte for correction logic test word
        self.test_msb0_L     = [0xa3,0xff] # 8 bits, low byte
        self.test_msb0_H     = [0xa4,0x7f] # 7 bits, high byte
        
        self.test_lsb1_L     = [0xa5,0xff] # 8 bits, low byte for correction logic test word, ADC1
        self.test_lsb1_H     = [0xa6,0x7f] # 7 bits, high byte for correction logic test word
        self.test_msb1_L     = [0xa7,0xff] # 8 bits, low byte
        self.test_msb1_H     = [0xa8,0x7f] # 7 bits, high byte '
        
        # Slow Serial Output (SSO) Configuration
        self.sso_enable      = [0xa9,0x1]  #1 bit, 0-> sso disabled, 1-> sso enabled
        self.sso_op_mode     = [0xa9,0xe]  #3 bits, see the datasheet
        self.sso_testword_L  = [0xaa,0xff] #8 bits, low byte of 16-bit words send out of SSO1 when in testmode, A5h
        self.sso_testword_H  = [0xab,0xff] #8 bits, high byte of 16-bit words send out of SSO1 when in testmode, CAh
        
        #Forcing configuration
        self.force_adc       = [0xac,0x3]  #2 bits, put chip into external forcing mode. 0-> normal operation, 1-> forcing mode. [1:0] -> [ADC1:ADC0]
        self.force_adc0      = [0xac,0x1]  #ADC0 forcing mode,  1= forcing mode, 0=normal mode
        self.force_adc1      = [0xac,0x2]  #ADC1 forcing mode,  1= forcing mode, 0=normal mode
        self.stage_select    = [0xac,0x1c] #3 bits, selects which stage is put into forcing mode
        
        self.force_refp      = [0xac,0x60] #2 bits, Forces conversion of positive differential reference. 0-> no force. 1-> force (VREFP-VREFN) at input
        self.force_refn      = [0xad,0x3]  #2 bits, Forces conversion of negative defferential reference. 0-> no force. 1-> force (VREFN-VREFP) at input
        self.force_cm        = [0xad,0xc]  #2 bits, Forces conversion of input common-mode reference.     0-> no force. 1-> force VCMI at input
        
        self.force_msb_adc   = [0xad,0x30] #2 bits, Force MSB to 1. 0-> no force of MSB, 1-> force MSB to 1
        self.force_msb_adc0  = [0xad,0x10] # force ADC0 MSB to 1
        self.force_msb_adc1  = [0xad,0x20] # force ADC1 MSB to 1
        
        self.force_lsb_adc   = [0xae,0x3]  #2 bits, Force LSB to 1. 0-> no force of LSB, 1-> force LSB to 1
        self.force_lsb_adc0  = [0xae,0x1]  # adc0 lsb force
        self.force_lsb_adc1  = [0xae,0x2]  # adc1 lsb force
        
        self.caldac_ctrl_adc = [0xae,0xc]  #2 bits, Choose forcing DAC setting, 0-> S0, S1 measurement. 1->S2, S3 measurement.
        self.caldac_ctrl_adc0 =[0xae,0x4]  # adc0 s0,s1 or s2,s3
        self.caldac_ctrl_adc1= [0xae,0x8]  # adc1 s0,s1 or s2,s3
        
        self.clear_reg_adc   = [0xae,0x30] #2 bits, Clears calibration registers. Clears from MSB down based on value in cal_stages.
        self.clear_reg_adc0  = [0xae,0x10] # adc0 clear
        self.clear_reg_adc1  = [0xae,0x20]
        #Monitor Configuration
        self.vmonitor_enable = [0xaf,0x1]  #1 bit, 0-> vmonitor disabled, 1-> vmonitor enabled
        self.imonitor_enable = [0xaf,0x2]  #1 bit, 0-> imonitor disabled, 1-> imonitor enabled.
        self.vmonitor_select = [0xaf,0x1c] #3 bits, Select internal voltage to monitor
        self.imonitor_select = [0xaf,0xe0] #3 bits, Select internal current to monitor
        
        #Backend Configuration
        self.config_lvds_i_ctrl = [0xb0,0x7] #3 bits, set output LVDS current
        self.config_start_number= [0xb1,0x1f]#5 bits, choose what ADC clock phase is defined as SHA clock
        self.config_debug_enable= [0xb2,0x1] #1 bit, enables observation of internal digital signals and clocks at ouput pins
        self.config_debug_select= [0xb2,0x1e]#4 bits,selects digital signal to send to debug output.
        self.config_test_data_mode=[0xb2,0x20]#1 bit, select ADC data or test patterns. 0-> normal operation, 1-> test pattern output
        self.config_adc0_pattern_L=[0xb3,0xff]#8 bits, low byte of pattern representing ADC0  #51
        self.config_adc0_pattern_H=[0xb4,0xff]#8 bits, high byte of pattern representing ADC0 #52
        self.config_adc1_pattern_L=[0xb5,0xff]#8 bits, low byte of pattern representing ADC1  #53
        self.config_adc1_pattern_H=[0xb6,0xff]#8 bits, high byte of pattern representing ADC1 #54
        
        #Backend configuration in page2 for I2C, no address offset required.
        self.page2_config_start_number= [0x1,0x1f]#5 bits, choose what ADC clock phase is defined as SHA clock
        self.page2_config_lvds_i_ctrl = [0x2,0x7] #3 bits, set output LVDS current
        self.page2_config_debug_select= [0x3,0xf]#4 bits,selects digital signal to send to debug output.