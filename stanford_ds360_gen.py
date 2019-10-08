# -*- coding: utf-8 -*-
"""
Created on Tue Sep 10 10:09:42 2019

@author: Edoardo Lopriore
"""
#This file is a very limited set of control functions for the DS360 Stanford Low Distortion Generator.
#Options: initialization, status check, output settings.


import struct
import sys 
import string
import time
import copy

import visa
from visa import VisaIOError
from datetime import datetime

class GEN_CTL:
    def status_chk(self, cmd_str):
        sta_chk = self.gen.query("SYST:ERR?")
        if (str(sta_chk[0:2]) == "+0" ):
            pass
        else:
            print (cmd_str)
            print (sta_chk)
            print ("Signal Generator Error! Exit anyway")
            sys.exit()

    def gen_init(self):
        rm = visa.ResourceManager()
        rm_list = rm.list_resources()
        try:
            rm_list.index(self.ADDR)
            print ("Stanford Research SystemsDS360 generator (%s) is locacted"%self.ADDR)
        except ValueError:
            print ("Stanford Research SystemsDS360 generator (%s) is not found, Please check!"%self.ADDR)
            print ("Exit anyway!")
            sys.exit()
        try:
            generator = rm.open_resource(self.ADDR)
        except VisaIOError:
            print ("Stanford Research SystemsDS360 Initialize--> Exact system name not found")
            print ("Exit anyway!")
            sys.exit()
        self.gen = generator


    def gen_set(self, wave_type="SINE", freq="21000", amp="1VP", dc_oft="0.9", load="Hi-Z", out="en"):
        if(out == "dis"):
            cmd_str = 'OUTE0'
            self.gen.write(cmd_str)
            print ("Signal generator output disabled")
            return
        if(load == "Hi-Z"):
            ld = "3"
        if(load == "50"):
            ld = "0"
        if(wave_type == "SINE"):
            wv = "0"
        if(wave_type == "SQUARE"):
            wv = "1"
        if(wave_type == "WHITE"):
            wv = "2"
            #cannot set frequency
            cmd_str = 'AMPL{};OFFS{};TERM{};FUNC{};OUTE1'.format(amp, dc_oft, ld, wv)
            self.gen.write(cmd_str)
            print ("Write: Func={}, Ampl={}, Offs={}, Term={}".format(wave_type, amp, dc_oft, load))
            time.sleep(2)
            return
        cmd_str = 'FUNC{};FREQ{};AMPL{};OFFS{};TERM{};OUTE1'.format(wv, freq, amp, dc_oft, ld)
        self.gen.write(cmd_str)
        time.sleep(2)
        print ("Write: Func={}, Freq={}, Ampl={}, Offs={}, Term={}".format(wave_type, freq, amp, dc_oft, load))


    #__INIT__#
    def __init__(self):
        self.ADDR = u'GPIB0::8::INSTR'
        self.gen = None
