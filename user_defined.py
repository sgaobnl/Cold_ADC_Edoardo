# -*- coding: utf-8 -*-
"""
Created on Mon Mar 26 10:31:31 2018

@author: JunbinZhang
"""
class User_defined:
    def __init__(self):
        #UDP ipaddress definition
        #-----------FE channel parameter----------#
        self.Input={'Direct_Input':0,'Test_Input':1}
        self.Baseline={'900mV':0,'200mV':1}
        self.Gain={'4.7mV/fC':0,'7.8mV/fC':1,'14mV/fC':2,'25mV/fC':3}
        self.Peaktime={'1us':0,'0.5us':1,'3us':2,'2us':3}
        self.Buffer={'off':0,'on':1}
        self.Mon={'off':0,'on':1}
        #----------FE global parameter------------#
        self.Coupled={'DC':0,'AC':1}
        self.Leakage={'500pA':0,'100pA':1,'5nA':2,'1nA':3} #[SLKH:SLK]
        self.S16={'Disconnect':0,'Connect':1}
        self.Monitor={'Analog':0,'Temp':1,'Bandgap':3}
        self.Pulse={'Disable':0,'External':1,'Internal':2,'ExtM':3}
        #---------ADC parameter----------#
#        self.ClkG={'In_sg':0,'External':1,'In_mon':2} #default:1
#        self.FRQC={'2MHz':1,'1MHz':0}                 #default:0
#        self.EN_GR={'Disable':0,'Enable':1}           #default:1
#        self.PCSR=0
#        self.PDSR=0
#        self.SLP=0
#        self.TST=0
#        self.F0=0
#        self.F1=0
#        self.F2=0
#        self.F3=0
#        self.F4=0
#        self.F5={'Normal':0,'Fixed':1} #1 for fixed pattern mode 0 for normal mode
#        self.sLSB=0
#        self.APA = {'Enable':1,'Disable':0}
