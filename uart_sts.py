# -*- coding: utf-8 -*-
"""
Created on Sun Aug  4 11:26:01 2019

@author: protoDUNE
"""

from udp import UDP
import time
def sts(adr, data_in, wen = 1):
    ladr = (adr&0xff)<<20
    ldata = (data_in&0xff)<<12
    lwen = (wen&0x01)<<7
    data = (ladr&0x0ff00000) + (ldata&0x000ff000) + (lwen&0x80)
    par_cnt = 0
    for i in range(32):
        if (data>>i)&0x01 == 0x01:
            par_cnt = par_cnt + 1
    
    if par_cnt%2 == 1:
        par_chk = 0
    else:
        par_chk =1
    data = ((par_chk<<28)&0x10000000) + data
 #   print (hex(data))
 #   par = XOR     
    B = UDP()
    B.write_reg(1,2)
    time.sleep(1)
    B.write_reg(2, data + 0x01)
    print (hex(adr), hex(data_in), hex(B.read_reg(2)))
    B.write_reg(2, data + 0x00)
#    B.write_reg(1,0)
 #   time.sleep(0.5)