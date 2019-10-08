# -*- coding: utf-8 -*-
"""
Created on Wed Jul 24 00:00:54 2019

@author: protoDUNE
"""

import numpy as np
import os
from sys import exit
import os.path
import math
import time

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
import matplotlib.mlab as mlab

import pickle
def xtalk_plot_num(chn_inject, dly_avg_chns, pres = ""):

    #plt.title('Xtalk,pulse--> chn%d, 200 waveforms for average'%(chn_inject))
    sps = 2000
    x = np.arange(sps)*0.01
    
    dly_chn = [val for tup in zip(*dly_avg_chns[chn_inject]) for val in tup] 
    amp_max = np.max(dly_chn[0:sps])    
    amp_min = np.min(dly_chn[0:sps])
    vpp_inject = amp_max - amp_min
    
    colors = ['C0-','C1-','C2-','C3-','C4-','C5-','C6-','C7-']
    if chn_inject == 7:
        xchn=0
    elif chn_inject == 15:
        xchn=8
    else:
        xchn=chn_inject + 1
    dly_chn = [val for tup in zip(*dly_avg_chns[xchn]) for val in tup]
    amp_max = np.max(dly_chn[0:sps])    
    amp_min = np.min(dly_chn[0:sps])
    vpp = amp_max - amp_min
    xtalk = (vpp*100.0) / vpp_inject
    return xtalk

def xtalk_plot_num2(chn_inject, dly_avg_chns, pres = ""):

    #plt.title('Xtalk,pulse--> chn%d, 200 waveforms for average'%(chn_inject))
    sps = 2000
    x = np.arange(sps)*0.01
    
    dly_chn = [val for tup in zip(*dly_avg_chns[chn_inject]) for val in tup] 
    amp_max = np.max(dly_chn[0:sps])    
    amp_min = np.min(dly_chn[0:sps])
    vpp_inject = amp_max - amp_min
    
    colors = ['C0-','C1-','C2-','C3-','C4-','C5-','C6-','C7-']
    if chn_inject == 6:
        xchn=0
    elif chn_inject ==7:
        xchn=1
    elif chn_inject == 14:
        xchn=8
    elif chn_inject ==15:
        xchn=9
    else:
        xchn=chn_inject + 2
    dly_chn = [val for tup in zip(*dly_avg_chns[xchn]) for val in tup]
    amp_max = np.max(dly_chn[0:sps])    
    amp_min = np.min(dly_chn[0:sps])
    vpp = amp_max - amp_min
    xtalk = (vpp*100.0) / vpp_inject
    return xtalk

    

def xtalk_plot(chn_inject, dly_avg_chns, pres = ""):
    fig = plt.figure(figsize=(6,12))
    ax1 = fig.add_subplot(411)

    #plt.title('Xtalk,pulse--> chn%d, 200 waveforms for average'%(chn_inject))
    sps = 2000
    x = np.arange(sps)*0.01
    
    dly_chn = [val for tup in zip(*dly_avg_chns[chn_inject]) for val in tup] 
    amp_max = np.max(dly_chn[0:sps])    
    amp_min = np.min(dly_chn[0:sps])
    vpp_inject = amp_max - amp_min
    plt.plot(x, dly_chn[0:sps],'b-', label = 'chn%d'%chn_inject)
    plt.ylim([30000,60000])
    plt.legend(loc='upper right')
    plt.grid()
    plt.ylabel('ADC counts')
    
    colors = ['C0-','C1-','C2-','C3-','C4-','C5-','C6-','C7-']
    ax4 = fig.add_subplot(412)
    if chn_inject == 7:
        xchn=0
    elif chn_inject == 15:
        xchn=8
    else:
        xchn=chn_inject + 1
    dly_chn = [val for tup in zip(*dly_avg_chns[xchn]) for val in tup]
    amp_max = np.max(dly_chn[0:sps])    
    amp_min = np.min(dly_chn[0:sps])
    vpp = amp_max - amp_min
    xtalk = (vpp*100.0) / vpp_inject
    plt.plot(x, np.array(dly_chn[0:sps])-dly_chn[0],colors[xchn%8],label='chn%d, xtalk=%.3f%%'%(xchn,xtalk))  
    plt.ylim([-100,400])
    plt.legend(loc='upper right')
    plt.grid()
    plt.ylabel('ADC counts')

    ax2 = fig.add_subplot(413)
    for xchn in range(8):
        if xchn != chn_inject and xchn != (chn_inject+1)%8:
            dly_chn = [val for tup in zip(*dly_avg_chns[xchn]) for val in tup]
            amp_max = np.max(dly_chn[0:sps])    
            amp_min = np.min(dly_chn[0:sps])
            vpp = amp_max - amp_min
            xtalk = (vpp*100.0) / vpp_inject
            plt.plot(x, np.array(dly_chn[0:sps])-dly_chn[0],colors[xchn%8],label='chn%d, xtalk=%.3f%%'%(xchn,xtalk))  
    plt.ylim([-150,150])
    plt.legend(loc='upper right')
    plt.grid()
    plt.ylabel('ADC counts')
    
    ax3 = fig.add_subplot(414)
    for xchn in range(8,16,1):
        if xchn != chn_inject and (xchn-8) != (chn_inject+1)%8:
            dly_chn = [val for tup in zip(*dly_avg_chns[xchn]) for val in tup]
            amp_max = np.max(dly_chn[0:sps])    
            amp_min = np.min(dly_chn[0:sps])
            vpp = amp_max - amp_min
            xtalk = (vpp*100.0) / vpp_inject
            plt.plot(x, np.array(dly_chn[0:sps])-dly_chn[0],colors[xchn%8],label='chn%d, xtalk=%.3f%%'%(xchn,xtalk))  
    plt.ylim([-150,150])
    plt.legend(loc='upper right')
    plt.grid()
    plt.ylabel('ADC counts')
    
    plt.xlabel('Time / $\mu$s')
#    plt.show()
    plt.savefig("d:/ColdADC/xtalk_pic/" + pres  + ".png")    
    plt.close()

xtalks =[[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
for chn in range(16):
    xtalks_tp = []
    for tp in ["05","10","20","30"]:
#    for chn in [0,7]:
        dly_avg_chns = [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
        tmpr = "D2_Xtalk"
        f_dir = "D:/ColdADC/" + tmpr + "_asicdac8/"
        fn_pre = "Data_chn%d_"%chn + tp + "us_"
        for dly in range(0,50,1):
            fn = f_dir + fn_pre + "dly%d.bin"%dly
            with open (fn, 'rb') as fp:
                chns = pickle.load(fp)
            oft = 100
            poft = oft + np.where(np.array(chns[0][oft:])>0xffff)[0][0]
            avg_chns = [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
        
            avg_n = 50
            for i in range(0,avg_n):
                for j in range(len(avg_chns)):
                    if i == 0:
                        avg_chns[j] = np.array(chns[j][poft+200*i:poft+200+200*i])
                    else:
                        avg_chns[j] = avg_chns[j] + np.array(chns[j][poft+200*i:poft+200+200*i])
            for j in range(len(avg_chns)):
                avg_chns[j] = avg_chns[j]//avg_n
                dly_avg_chns[j].append( list(avg_chns[j]&0xffff)    )
        
        for i in range(len(dly_avg_chns)):
            tmp = reversed(dly_avg_chns[i])
            dly_avg_chns[i] = tmp
            
#        xtalk_plot(chn, dly_avg_chns, pres = tmpr+fn_pre)    
#        tmp = xtalk_plot_num(chn, dly_avg_chns, pres = tmpr+fn_pre)    
        tmp = xtalk_plot_num2(chn, dly_avg_chns, pres = tmpr+fn_pre)    
        xtalks_tp.append(tmp)
    xtalks[chn] = xtalks_tp
    print (xtalks_tp)
print (xtalks)

#    fig = plt.figure(figsize=(12,12))
#    for i in range(16):
#        ax = plt.subplot2grid((8,2), (i%8, i//8), colspan=1, rowspan=1)
#        dly_chn = [val for tup in zip(*dly_avg_chns[i]) for val in tup]  
#        sps = (len(dly_chn))
#        x = np.arange(sps)*0.01
#        ax.scatter(x[0:500], dly_chn[0:500], marker ='.')
#    #    
#    plt.tight_layout()
#    plt.savefig("d:/ColdADC/pics/" + fn_pre + tmpr + ".png")
#    plt.close()
    
    #fig = plt.figure(figsize=(12,8))
    #for i in [3]:
     #   ax = plt.subplot2grid((8,2), (i%8, i//8), colspan=1, rowspan=1)
    #    dly_chn = [val for tup in zip(*dly_avg_chns[i]) for val in tup]  
    #    sps = (len(dly_chn))
    #    x = np.arange(sps)*0.01
    #    plt.scatter(x[100:600], dly_chn[100:600], marker ='.')    
    
#dly_chn = [val for tup in zip(*dly_avg_chns[0]) for val in tup]  
#sps = (len(dly_chn))
#x = np.arange(sps)*0.01
#
#
#plt.scatter(x[100:1000], dly_chn[100:1000], marker ='.')


#lists = [l1, l2, ...]
#[val for tup in zip(*lists) for val in tup]      
#    sps = 100
#    x = np.arange(sps)*0.5 - dly*0.01
##    print (x)
##    plt.plot(x, avg_chns[0][0: sps])
##    plt.plot(x, avg_chns[1][1: sps+1])
#    plt.scatter(x, avg_chns[1][1: sps+1], marker ='.')

    
#    plt.scatter(x, avg_chns[0][0:sps], marker = '.')
##    plt.plot(x, chns[0][poft:poft+sps])
##    plt.scatter(x, chns[0][poft:poft+sps], marker = '.')
#
##plt.savefig("d:\abc.png")
#plt.show()

#print ("xxxx")
#plt.close()
#    if chn_inject != 0:
#        dly_chn = [val for tup in zip(*dly_avg_chns[0]) for val in tup]
#        plt.plot(x, dly_chn[0:sps],'g-',label='chn0')    
#    if chn_inject != 1:
#        dly_chn = [val for tup in zip(*dly_avg_chns[1]) for val in tup]
#        plt.plot(x, dly_chn[0:sps],'r-',label='chn1')    
#    if chn_inject != 2:
#        dly_chn = [val for tup in zip(*dly_avg_chns[2]) for val in tup]
#        plt.plot(x, dly_chn[0:sps],'c-',label='chn2')    
#    if chn_inject != 3:
#        dly_chn = [val for tup in zip(*dly_avg_chns[3]) for val in tup]
#        plt.plot(x, dly_chn[0:sps],'m-',label='chn3')    
#    if chn_inject != 4:
#        dly_chn = [val for tup in zip(*dly_avg_chns[4]) for val in tup]
#        plt.plot(x, dly_chn[0:sps],'y-',label='chn4')    
#    if chn_inject != 5:
#        dly_chn = [val for tup in zip(*dly_avg_chns[5]) for val in tup]
#        plt.plot(x, dly_chn[0:sps],'k-',label='chn5')    
#    if chn_inject != 6:
#        dly_chn = [val for tup in zip(*dly_avg_chns[6]) for val in tup]
#        plt.plot(x, dly_chn[0:sps],'k*-',label='chn6')    
#    if chn_inject != 7:
#        dly_chn = [val for tup in zip(*dly_avg_chns[7]) for val in tup]
#        plt.plot(x, dly_chn[0:sps],'b-',label='chn7')    
#    ax3 = fig.add_subplot(313)
#    if chn_inject != 8:
#        plt.plot(chns[8],'b-',label='chn8')
#    if chn_inject != 9:
#        plt.plot(chns[9],'g-',label='chn9')
#    if chn_inject != 10:
#        plt.plot(chns[10],'r-',label='chn10')
#    if chn_inject != 11:
#        plt.plot(chns[11],'c-',label='chn11')
#    if chn_inject != 12:
#        plt.plot(chns[12],'m-',label='chn12')
#    if chn_inject != 13:
#        plt.plot(chns[13],'y-',label='chn13')
#    if chn_inject != 14:
#        plt.plot(chns[14],'k-',label='chn14')
#    if chn_inject != 15:
#        plt.plot(chns[15],'b*-',label='chn15')
#    plt.legend()
#    plt.xlabel('times')
#    plt.ylabel('ADC counts')

