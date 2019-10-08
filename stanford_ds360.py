# -*- coding: utf-8 -*-
"""
Created on Tue Sep 10 10:09:42 2019

@author: Edoardo Lopriore
"""
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
        sta_chk = self.smu.query("SYST:ERR?")
        if (str(sta_chk[0:2]) == "+0" ):
            pass
        else:
            print cmd_str
            print sta_chk
            print ("Signal Generator Error! Exit anyway")
            sys.exit()

    def gen_init(self):
        rm = visa.ResourceManager()
        rm_list = rm.list_resources()
        try:
            rm_list.index(self.ADDR)
            print ("Stanford Research Systems DS360 (%s) is locacted"%self.ADDR)
        except ValueError:
            print ("Stanford Research Systems DS360 (%s) is not found, Please check!"%self.ADDR)
            print ("Exit anyway!")
            sys.exit()
        try:
            gen = rm.open_resource(self.ADDR)
            init_chk = smu.query("SYST:ERR?")
            if (str(init_chk[0:2]) == "+0" ):
                pass
            else:
                print init_chk
                print ("Init Stanford Research Systems DS360 Error! Exit anyway")
                sys.exit()
        except VisaIOError:
            print ("Keysight Initialize--> Exact system name not found")
            print "Exit anyway!"
            sys.exit()
        self.gen = gen


    def smu_chn_on(self, chn, volt, sysflt=50, vrange=20, crange=10, clim=10, nplc=25):
        cmd_str = 'SYST:LFR F{}Hz'.format(sysflt)
        self.smu.write(cmd_str)
        self.status_chk(cmd_str)

        cmd_str = 'VOLT:RANG R{}V, (@{})'.format(vrange,chn)
        self.smu.write(cmd_str)
        self.status_chk(cmd_str)

        cmd_str = 'CURR:RANG R{}mA, (@{})'.format(crange,chn)
        self.smu.write(cmd_str)
        self.status_chk(cmd_str)

        cmd_str = 'CURR:LIM {}mA, (@{})'.format(clim,chn)
        self.smu.write(cmd_str)
        self.status_chk(cmd_str)

        cmd_str = "SENS:VOLT:NPLC {}, (@{})".format(nplc,chn)
        self.smu.write(cmd_str)
        self.status_chk(cmd_str)

        cmd_str = "SENS:CURR:NPLC {}, (@{})".format(nplc,chn)
        self.smu.write(cmd_str)
        self.status_chk(cmd_str)

        cmd_str = "VOLT {}V, (@{})".format(volt,chn)
        self.smu.write(cmd_str)
        self.status_chk(cmd_str)

        cmd_str = "OUTP ON, (@{})".format(chn)
        self.smu.write(cmd_str)
        self.status_chk(cmd_str)


    def smu_chn_off(self, chn):
        cmd_str = "OUTP OFF, (@{})".format(chn)

    def smu_meas(self, chn, mode=0):
        timestampe =  datetime.now().strftime('%m%d%Y_%H%M%S')
        cmd_str = "MEAS:VOLT? (@{})".format(chn)
        m_volt = float(self.smu.query(cmd_str))
        self.status_chk(cmd_str)

        cmd_str = "MEAS:CURR? (@{})".format(chn)
        m_curr = float(self.smu.query(cmd_str))
        self.status_chk(cmd_str)
        #print "{}, smu ChN{}, Volt={}, Curr={}".format(timestampe, chn, m_volt, m_curr)

        return mode, timestampe, chn, m_volt, m_curr

    #__INIT__#
    def __init__(self):
        self.ADDR = u'USB0::0x0957::0x4118::MY57070006::INSTR'
        self.smu = None

