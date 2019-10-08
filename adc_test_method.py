# -*- coding: utf-8 -*-
"""
Created on Wed Apr 17 16:52:39 2019

@author: JunbinZhang
"""
import math
import numpy as np
from scipy.fftpack import fft,rfft,ifft
class ADC_method:
    
    def data_window(self,data,offset): 
        # ADC code range 0 ~ 2^N -1 = 0~4095
        # normal: code range 1 ~ 2^N -2 = 1~4094
        # offset < 2^(N-1): code range:  for list [offset:-offset]
        xcor = [int(offset+1),int(math.pow(2,self.Nbit)-2-offset)]
        for i in range(len(data)):             
            self.data[i] = data[i][offset+1:-(offset+1)]

        return self.data,xcor
    
    def data_window_cali(self,data): 
        # ADC code range 0 ~ 2^N -1 = 0~4095
        # normal: code range 1 ~ 2^N -2 = 1~4094
        # offset < 2^(N-1): code range:  for list [offset:-offset]
        xcor = [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
        for i in range(len(data)):   
            xcor_t = [j for j, e in enumerate(data[i]) if e!=0]    
            #start = xcor_t[0]+1  
            #end = xcor_t[-1]
            xcor[i] = [xcor_t[1],xcor_t[-2]]
            self.data[i] = data[i][xcor_t[1]:xcor_t[-1]]
        return self.data,xcor     

    def noise_window(self,data): 
        # ADC code range 0 ~ 2^N -1 = 0~65535
        # normal: code range 1 ~ 2^N -2 = 1~4094
        # offset < 2^(N-1): code range:  for list [offset:-offset]
        xcor = [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
        for i in range(len(data)):   
            xcor_t = [j for j, e in enumerate(data[i]) if e!=0]    
            #start = xcor_t[0]+1  
            #end = xcor_t[-1]
            xcor[i] = [xcor_t[0],xcor_t[-1]]
            self.data[i] = data[i][xcor_t[0]:(xcor_t[-1]+1)]
            
            
        return self.data,xcor  
    
    def ramp_dnl_inl_cali(self,data):
        xdata,xcor = self.data_window_cali(data)
        #calculate total number of samples   
        MT=[]
        for i in range(len(xdata)):
            MT.append(sum(xdata[i]))
        #calculate ideal hits    
        Hit_ideal =[]
        for i in range(len(xdata)):
            tem = MT[i]/(xcor[i][1]-xcor[i][0]+1)
            Hit_ideal.append(tem)
        #Calculate DNL
        DNL = [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
        
        for chn in range(len(DNL)):
            for i in range(xcor[chn][1]-xcor[chn][0]+1):
                tem = (xdata[chn][i] / Hit_ideal[chn])-1
                DNL[chn].append(tem)
        
        INL = [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
        
        for chn in range(len(INL)):
            for i in range(xcor[chn][1]-xcor[chn][0]+1):
                if i==0:
                    INL[chn].append(DNL[chn][0])
                else:
                    tem = sum(DNL[chn][0:i+1])
                    INL[chn].append(tem) 
        return xdata,DNL,INL,xcor      
    
    def ramp_dnl_inl(self,data,offset):
        xdata,xcor = self.data_window(data,offset)
        #calculate total number of samples   
        MT=[]
        for i in range(len(xdata)):
            MT.append(sum(xdata[i]))
        #calculate ideal hits    
        Hit_ideal =[]
        for i in range(len(xdata)):
            tem = MT[i]/(xcor[1]-xcor[0]+1)
            Hit_ideal.append(tem)
        #Calculate DNL
        DNL = [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
        
        for chn in range(len(DNL)):
            for i in range(xcor[1]-xcor[0]+1):
                tem = (xdata[chn][i] / Hit_ideal[chn])-1
                DNL[chn].append(tem)
        
        INL = [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
        
        for chn in range(len(INL)):
            for i in range(xcor[1]-xcor[0]+1):
                if i==0:
                    INL[chn].append(DNL[chn][0])
                else:
                    tem = sum(DNL[chn][0:i+1])
                    INL[chn].append(tem)
        
        return xdata,DNL,INL,xcor

    def sine_dnl_inl(self,data, offset):
        xdata,xcor = self.data_window(data,offset)
        
    
        Nu = [] #number of times the upper code is hit
        Nl = [] #number of times the lower code is hit
        Ns = [] #number of samples(total sum of code occurrences)
        for i in range(len(xdata)):
            Nu.append(xdata[i][-1])
            Nl.append(xdata[i][0])
            Ns.append(sum(xdata[i]))
        
        #calculate Xu and Xl
        Xu=[]
        Xl=[]
        for i in range(len(xdata)):
            Xu.append(math.cos(math.pi*Nu[i]/Ns[i]))
            Xl.append(math.cos(math.pi*Nl[i]/Ns[i]))
        #calculate offset
        offset = []
        for i in range(len(xdata)):
            tem = ((Xl[i] - Xu[i])/(Xl[i]+Xu[i]))*(math.pow(2,(self.Nbit -1))-1)
            offset.append(tem)
        
        #Calculate peak
        peak=[]   #(LSB)  
        for i in range(len(xdata)): 
            tem = (math.pow(2,(self.Nbit -1)) - 1- offset[i])/Xu[i]
            peak.append(tem)
        
        #Calculate ideal count for sine
        Ideal_counts = [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
        for i in range(len(xdata)):
            for code in range(xcor[0],xcor[1]+1,1):
                tem = Ns[i]/math.pi * (math.asin((code+1 - math.pow(2,(self.Nbit-1))-offset[i])/peak[i]) - math.asin((code - math.pow(2,(self.Nbit-1))-offset[i])/peak[i]) )
                Ideal_counts[i].append(tem)
        
        #Calculate DNL
        DNL = [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
        
        for chn in range(len(DNL)):
            for i in range(xcor[1]-xcor[0]+1):
                tem = (xdata[chn][i] / Ideal_counts[chn][i]) -1
                DNL[chn].append(tem)
        
        INL = [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
        
        for chn in range(len(INL)):
            for i in range(xcor[1]-xcor[0]+1):
                if i==0:
                    INL[chn].append(DNL[chn][0])
                else:
                    tem = sum(DNL[chn][0:i+1])
                    INL[chn].append(tem)
        
        return xdata,DNL,INL,xcor
    #============================================================#
#    def chn_rfft(chndata,fs=2000000.0,fft_s=2000, avg_cycle = 50):
#        ts = 1.0/fs # sampling internal, fft_s samples, avg_cycle average cycles.
#        
#        if (len(chndata) >= fft_s * avg_cycle):
#            pass
#        else:
#            cycles = len(chndata) // fft_s
        
    def __init__(self): # throw data array here 
        self.Nbit = 12
        self.data = [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
        #self.data = data
