# -*- coding: utf-8 -*-
"""
Created on Sun Mar 24 19:45:06 2019

@author: JunbinZhang
"""

from adc_i2c_uart import COLDADC_tool
from adc_reg import ADC_REG
ADC = COLDADC_tool()
adc_reg = ADC_REG()

chip_id = 0
page = 1

ADC.hard_reset()

ADC.config_tool('I2C')

ADC.ADC_I2C_write(chip_id,page,adc_reg.config_test_data_mode,1) #1-> test pattern output
##print(ADC.ADC_I2C_read(chip_id,page,adc_reg.config_test_data_mode))
ADC.ADC_I2C_write(chip_id,page,adc_reg.config_adc0_pattern_L,0x8a) #1
ADC.ADC_I2C_write(chip_id,page,adc_reg.config_adc0_pattern_H,0x8a) #0

ADC.ADC_I2C_write(chip_id,page,adc_reg.config_adc1_pattern_L,0x8a) #1 #ADC1
ADC.ADC_I2C_write(chip_id,page,adc_reg.config_adc1_pattern_H,0x8a) #0 #ADC1

#ADC.ADC_I2C_write(chip_id,page,adc_reg.config_test_data_mode,0) #1-> test pattern output
#ADC.I2C_write(chip_id,2,adc_reg.page2_config_start_number,0x5) #0
##Addjust niblle received
#
ADC.ADC_I2C_write(chip_id,page,adc_reg.config_test_data_mode,0) #0-> back to normal operation
#

ADC.ADC_I2C_write(chip_id,page,adc_reg.adc_sync_mode,1)       #0-> back to normal operation



ADC.ADC_I2C_write(chip_id,page,adc_reg.adc_output_format,0) #0-> back to normal operation
#
#
#print(ADC.ADC_I2C_read(chip_id,page,adc_reg.config_test_data_mode))
#print(ADC.ADC_I2C_read(chip_id,page,adc_reg.config_adc0_pattern_L))
#print(ADC.ADC_I2C_read(chip_id,page,adc_reg.adc_sync_mode))

#Adjust nibble word
#print(hex(ADC.I2C_read(chip_id,page,0x80)))