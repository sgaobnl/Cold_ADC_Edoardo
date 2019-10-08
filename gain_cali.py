# -*- coding: utf-8 -*-
"""
Created on Tue Feb 12 16:52:57 2019

@author: JunbinZhang
"""
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import find_peaks
from brd_config import Brd_Config
from frame import Frames
from operator import add
import xlwt
#from xlwt import Workbook

brd_config = Brd_Config()

def xtalk_data(pktnum=512,chn_inject=0, height = 50000):
    brd_config.Acq_start_stop(1)
    ################################################
    adcdata = brd_config.get_data(pktnum,1,'Jumbo')
    brd_config.Acq_start_stop(0)
    frames_inst = Frames(pktnum,adcdata)
    frames = frames_inst.packets()
    ###############################################
    chns=[[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
    for i in range(len(frames)-10):
        for j in range(16): #16 channels
            chns[j].append(frames[i].ADCdata[j])
    
    sign =  np.array(chns[chn_inject])       
    #find peaks
    xpeaks,_=find_peaks(sign,height)
    delete_i = []
    for i in range(len(xpeaks)):
        if xpeaks[i] < 20 or xpeaks[i] > (pktnum-80) :
            delete_i.append(i)
    xpeaks = np.delete(xpeaks,delete_i)
    #add a position
    pos = xpeaks[0]
    start_p=pos-20
    end_p = pos+75
    #data output
    for i in range(len(chns)):
        chns[i] = chns[i][start_p : end_p]

    return chns
    
#chns = xtalk_data(pktnum=512,chn_inject=0)
def xtalk_run(pktnum=512,chn_inject=3,cycles=200,height = 50000):
    chns=[[0]*95,[0]*95,[0]*95,[0]*95,[0]*95,[0]*95,[0]*95,[0]*95,[0]*95,[0]*95,[0]*95,[0]*95,[0]*95,[0]*95,[0]*95,[0]*95]
    for i in range(cycles):
        chn_tem = xtalk_data(pktnum,chn_inject,height)
        for j in range(16):
            chns[j] = list(map(add,chns[j],chn_tem[j]))#chns[j] + chn_tem[j]
    # do the average
    for i in range(16):
       chns[i] = [x / cycles for x in chns[i]]
    #calculate vpp
    chns_mean=[]
    chns_max=[]
    #chns_min=[]
    for i in range(16):
        chns_mean.append(np.mean(chns[i]))
        chns_max.append(max(chns[i]))
        #chns_min.append(min(chns[i]))
    #write something in excel
    for i in range(16):
        print('%.1f'%(chns_max[i]-chns_mean[i]))
    return chns,chns_mean,chns_max



def xtalk_plot(chns,chns_mean,chns_max):
    fig = plt.figure()
    ax1 = fig.add_subplot(211)
    
    
    plt.ylabel('ADC counts')
    plt.title('Warm,FPGA DAC=0x1,900mV,25mV/fC,3us,bufoff,200 times average')
    plt.plot(chns[0],'g-',label='chn0')

    plt.plot(chns[1],'r-',label='chn1')

    plt.plot(chns[2],'c-',label='chn2')

    plt.plot(chns[3],'m-',label='chn3')

    plt.plot(chns[4],'y-',label='chn4')

    plt.plot(chns[5],'k-',label='chn5')

    plt.plot(chns[6],'k*-',label='chn6')

    plt.plot(chns[7],'b-',label='chn7')
    plt.legend()
    plt.ylabel('ADC counts')
    
    ax2 = fig.add_subplot(212)
    plt.plot(chns[8],'b-',label='chn8')

    plt.plot(chns[9],'g-',label='chn9')

    plt.plot(chns[10],'r-',label='chn10')

    plt.plot(chns[11],'c-',label='chn11')

    plt.plot(chns[12],'m-',label='chn12')

    plt.plot(chns[13],'y-',label='chn13')

    plt.plot(chns[14],'k-',label='chn14')

    plt.plot(chns[15],'b*-',label='chn15')
    plt.legend()
    plt.xlabel('times')
    plt.ylabel('ADC counts')
    plt.show()
#--------------------------------------------------------------------------------# 
chns,chns_mean,chns_max = xtalk_run(pktnum=512,chn_inject=0,cycles=200,height = 38000)
#xtalk_plot(chns=chns,chns_mean=chns_mean,chns_max=chns_max)