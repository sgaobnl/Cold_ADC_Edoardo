# -*- coding: utf-8 -*-
"""
Created on Tue Feb 19 16:08:47 2019

@author: JunbinZhang


"""
import numpy as np
class Frame:
    def info(self):
        print('CHECKSUM =%x'%self.chksum)
        print('TIMESTAMP=%d'%self.timestamp)
        print('ADC_ERROR=%d'%self.ADCerr)
        print('RESERVED =%x'%self.reserved)
        print('HEADER   =%x'%self.header)
    def chn_probe(self,chn):
        if(0<= chn <=15):
            return self.ADCdata[chn]
        else:
            print("Error, chn should be (0~15)")
    def __init__(self,frame_ptr,raw_data):
        self.frame_length = 22
        self.frame_data = raw_data[int(frame_ptr):int(frame_ptr+self.frame_length)]
        self.chksum    = self.frame_data[1]
        self.timestamp = self.frame_data[2]
        self.ADCerr    = self.frame_data[3]
        self.reserved  = self.frame_data[4]
        self.header    = self.frame_data[5]

        if (self.reserved&0x0001):      
            self.ADCdata   = 0x10000 + np.array(self.frame_data[6:])
            self.ADCdata = list(self.ADCdata)
        else: 
            self.ADCdata   = self.frame_data[6:]
        
class Frames(Frame):
    def packets(self):
        frame_recv = []
        for i in range(self.pkt_num):
            frame_ptr = self.frame_len * i
            frame_recv.append(Frame(frame_ptr,self.frames_data))
        return frame_recv
    def __init__(self,pkt_num,frames_data):
        self.pkt_num = pkt_num
        self.frames_data = frames_data
        self.pkt_len = 44 # 44 bytes
        self.frame_len = int(self.pkt_len/2)