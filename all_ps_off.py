# -*- coding: utf-8 -*-
"""
Created on Thu Sep  5 16:20:54 2019

@author: Edoardo Lopriore
"""

import numpy as np
#from keysight_e36312a_ps import PS_CTL
from rigol_dp832_ps import RIGOL_PS_CTL
from stanford_ds360_gen import GEN_CTL
adc_ps = RIGOL_PS_CTL() 
adc_ps.ADDR =u'USB0::0x1AB1::0x0E11::DP8C184550857::0::INSTR' 
fm_ps = RIGOL_PS_CTL() 
fm_ps.ADDR = u'USB0::0x1AB1::0x0E11::DP8C184450708::0::INSTR'

print ("Turn Generator output off")
gen = GEN_CTL() #signal generator library
gen.gen_init()
gen.gen_set(out = "dis")

print ("Turn ADC PS off")
adc_ps.ps_init()
adc_ps.off([1,2, 3])

print ("Turn FM PS off")
fm_ps.ps_init()
fm_ps.off([1, 2,3])

import time
time.sleep(5)




