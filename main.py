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
brd_config = Brd_Config()


def xtalk_data(pktnum=512,chn_inject=0):
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
    xpeaks,_=find_peaks(sign,height = 50000)
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
def xtalk_run(pktnum=512,chn_inject=3,cycles=200):
    chns=[[0]*95,[0]*95,[0]*95,[0]*95,[0]*95,[0]*95,[0]*95,[0]*95,[0]*95,[0]*95,[0]*95,[0]*95,[0]*95,[0]*95,[0]*95,[0]*95]
    for i in range(cycles):
        chn_tem = xtalk_data(pktnum,chn_inject)
        for j in range(16):
            chns[j] = list(map(add,chns[j],chn_tem[j]))#chns[j] + chn_tem[j]
    # do the average
    for i in range(16):
       chns[i] = [x / cycles for x in chns[i]]
    #calculate vpp
    chns_mean=[]
    chns_max=[]
    chns_min=[]
    for i in range(16):
        chns_mean.append(np.mean(chns[i]))
        chns_max.append(max(chns[i]))
        chns_min.append(min(chns[i]))
    for i in range(16):
        print('chn%d vpp=%.1f xtalk=%.3f%%'%(i,chns_max[i]-chns_min[i],100*(chns_max[i]-chns_min[i])/(chns_max[chn_inject]-chns_min[chn_inject])))

    return chns,chns_mean,chns_max,chns_min 



def xtalk_plot(chn_inject,chns,chns_max,chns_min):
    fig = plt.figure()
    ax1 = fig.add_subplot(311)
    #plt.xlabel('times')
    plt.ylabel('ADC counts')
    plt.title('Xtalk,pulse--> chn%d, 200 waveforms for average'%(chn_inject))
    plt.plot(chns[chn_inject],'bo-')
    plt.legend(('chn%d'%(chn_inject)))
    plt.text(40,50000, 'vpp=%.1f'%(chns_max[chn_inject]-chns_min[chn_inject]),color='k')
    ax2 = fig.add_subplot(312)
    
    if chn_inject != 0:
        plt.plot(chns[0],'g-',label='chn0')
    if chn_inject != 1:
        plt.plot(chns[1],'r-',label='chn1')
    if chn_inject != 2:
        plt.plot(chns[2],'c-',label='chn2')
    if chn_inject != 3:
        plt.plot(chns[3],'m-',label='chn3')
    if chn_inject != 4:
        plt.plot(chns[4],'y-',label='chn4')
    if chn_inject != 5:
        plt.plot(chns[5],'k-',label='chn5')
    if chn_inject != 6:
        plt.plot(chns[6],'k*-',label='chn6')
    if chn_inject != 7:
        plt.plot(chns[7],'b-',label='chn7')
    plt.legend()
    plt.ylabel('ADC counts')
    
    ax3 = fig.add_subplot(313)
    if chn_inject != 8:
        plt.plot(chns[8],'b-',label='chn8')
    if chn_inject != 9:
        plt.plot(chns[9],'g-',label='chn9')
    if chn_inject != 10:
        plt.plot(chns[10],'r-',label='chn10')
    if chn_inject != 11:
        plt.plot(chns[11],'c-',label='chn11')
    if chn_inject != 12:
        plt.plot(chns[12],'m-',label='chn12')
    if chn_inject != 13:
        plt.plot(chns[13],'y-',label='chn13')
    if chn_inject != 14:
        plt.plot(chns[14],'k-',label='chn14')
    if chn_inject != 15:
        plt.plot(chns[15],'b*-',label='chn15')
    plt.legend()
    plt.xlabel('times')
    plt.ylabel('ADC counts')
    plt.show()
#--------------------------------------------------------------------------------# 
chns,chns_mean,chns_max,chns_min = xtalk_run(pktnum=512,chn_inject=15,cycles=200)
xtalk_plot(chn_inject=15,chns=chns,chns_max=chns_max,chns_min=chns_min)