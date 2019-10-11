# -*- coding: utf-8 -*-
"""
Created on Thu Sep  5 16:20:54 2019

@author: Edoardo Lopriore
"""

import numpy as np
from keysight_e36312a_ps import PS_CTL
from rigol_dp832_ps import RIGOL_PS_CTL
from stanford_ds360_gen import GEN_CTL

def power_on_init():
    #Turn FM on
    print ("Turn FM on")
    fm_ps.ps_init()
    fm_ps.off([1,2,3])
    fm_ps.set_channel(channel=1, voltage = 2.8,  v_limit = 3.5, c_limit = 1)
    fm_ps.set_channel(channel=2, voltage = 2.8,  v_limit = 3.5, c_limit = 1)
    fm_ps.set_channel(channel=3, voltage = 5,  c_limit = 1)
    fm_ps.on([1,2,3])
    time.sleep(3)
    #FPGA reset
    print ("FM Reset")
    cq.bc.udp.write_reg(0,1) 
    time.sleep(0.01)
    cq.bc.udp.write_reg(0,1) 
    time.sleep(1)


    #initilize ADC PS
    print ("ADC is powered on")
    ps.ps_init()
    ps.off([1,2,3])
    ps.set_channel(1,2.5)
    ps.set_channel(2,2.1)
    ps.set_channel(3,2.25)
    ps.on([1,2,3])
    time.sleep(2)

    #initilize Genetor 
    print ("Generator output off")
    gen_output_dis()
    time.sleep(3)



