# -*- coding: utf-8 -*-
"""
Created on Tue Apr  9 18:22:20 2019

@author: JunbinZhang
"""
"""
DNL error is defined as the difference between an actual step width and the ideal value of 1 LSB.
For an ideal ADC, in which the differential nonlinearity coincides with DNL=0LSB, each analog step equals
1LSB = VFSR/2^N, where VFSR is the full-scale range and N is the resolution of the ADC and the transition values
are spaced exactly 1LSB apart.A DNL error specification of less than or equal to 1LSB guarantees a monotonic transfer function with
no missing codes.An ADC's monotonicity is guaranteed when its digital output increases (or remains constant) with an increasing
input signal, thereby avoiding sign changes in the slope of the transfer curve. DNL is specified after the
static gain error has been removed. It is defined as follows:
    DNL = |[(Vd+1 -Vd)/Vlsb-ideal  - 1]|, where 0 < d < 2^N -2
    Vd is the physical value corresponding to the digital output code D, N is the ADC resolution, and VLSB-IDEAL is the ideal spacing
    for two adjacent digitlal codes.
"""

"""
INL error is described as the deviation, in LSB or percent of full-scale range (FSR), of an actual transfer
function from a straight line. The INL-error magnitude then depends directly on the position chosen for
this straight line. At least two definitions are common: "best straight-line INL" and "end-point INL"

Best straight-line INL provides information about offset (intercept) and gain (slope) error, plus the
position of the transfer function (discussed below). It determines, in the form of a straight line, the
closest approximation to the ADC's actual transfer function. The exact position of the line is not
clearly defined, but this approach yields the best repeatability, and it serves as a true
representation of linearity. 
End-point INL passes the straight line through end points of the converter's transfer function,
thereby defining a precise position for the line. Thus, the straight line for an N-bit ADC is defined by
its zero (all zeros) and its full-scale (all ones) outputs.

The best straight-line approach is generally preferred, because it produces better results. The INL
specification is measured after both static offset and gain errors have been nullified, and can be
described as follows:
    INL = |[(Vd-Vzero)/VLSB-IDEAL] -d |, where 0 < d < 2^N -1.
    Vd is the analog value represented by the digital output code d, N is the ADC's resolution,Vzero is the minimum analog input
    corresponding to an all-zero output code. and Vlsb-IDEAL is the ideal spacing for two adjacent output codes
"""

import matplotlib.pyplot as plt
import numpy as np
import csv
import math
#give the location of the file

xcode_vrefp_300k=[]
xvrefp_300k=[]

xcode_vrefp_77k=[]
xvrefp_77k=[]


xcode_ibuff_300k=[]
ibuff_300k=[]

xcode_ibuff_77k=[]
ibuff_77k=[]
#open 1
with open('E:\Junbin\DUNEADC_TEST\DUNE_COLDADC\monitor\\vrefp_vdd2p5_300k_cmos.csv') as csvfile:
    readCSV = csv.reader(csvfile,delimiter=',')
    for row in readCSV:    
        xcode_vrefp_300k.append(row[0])
        xvrefp_300k.append(row[1])
csvfile.close()

xcode_vrefp_300k = xcode_vrefp_300k[1:]
xvrefp_300k= xvrefp_300k[1:]
xcode_vrefp_300k = list(map(int,xcode_vrefp_300k))
xvrefp_300k = list(map(float,xvrefp_300k))

fit_300k_vref = np.polyfit(xcode_vrefp_300k,xvrefp_300k,1)
fit_fn_300k_vref = np.poly1d(fit_300k_vref)



#open 2
with open('E:\Junbin\DUNEADC_TEST\DUNE_COLDADC\monitor\\vrefp_vdd2p5_77k_cmos.csv') as csvfile:
    readCSV = csv.reader(csvfile,delimiter=',')
    for row in readCSV:    
        xcode_vrefp_77k.append(row[0])
        xvrefp_77k.append(row[1])
csvfile.close()

xcode_vrefp_77k = xcode_vrefp_77k[1:]
xvrefp_77k= xvrefp_77k[1:]
xcode_vrefp_77k = list(map(int,xcode_vrefp_77k))
xvrefp_77k = list(map(float,xvrefp_77k))

fit_77k_vref = np.polyfit(xcode_vrefp_77k,xvrefp_77k,1)
fit_fn_77k_vref = np.poly1d(fit_77k_vref)



#open 5 current
with open('E:\Junbin\DUNEADC_TEST\DUNE_COLDADC\monitor\ibuff_vdd2p5_300k_cmos.csv') as csvfile:
    readCSV = csv.reader(csvfile,delimiter=',')
    for row in readCSV:    
        xcode_ibuff_300k.append(row[0])
        ibuff_300k.append(row[1])
csvfile.close()

xcode_ibuff_300k = xcode_ibuff_300k[1:]
ibuff_300k= ibuff_300k[1:]
xcode_ibuff_300k = list(map(int,xcode_ibuff_300k))
ibuff_300k = list(map(float,ibuff_300k))
ibuff_300k = [i * 200 for i in ibuff_300k]

fit_300k_ibuff = np.polyfit(xcode_ibuff_300k[21:],ibuff_300k[21:],1)
fit_fn_300k_ibuff = np.poly1d(fit_300k_ibuff)

#open 5 current
with open('E:\Junbin\DUNEADC_TEST\DUNE_COLDADC\monitor\ibuff_vdd2p5_77k_cmos.csv') as csvfile:
    readCSV = csv.reader(csvfile,delimiter=',')
    for row in readCSV:    
        xcode_ibuff_77k.append(row[0])
        ibuff_77k.append(row[1])
csvfile.close()

xcode_ibuff_77k = xcode_ibuff_77k[1:]
ibuff_77k= ibuff_77k[1:]
xcode_ibuff_77k = list(map(int,xcode_ibuff_77k))
ibuff_77k = list(map(float,ibuff_77k))
ibuff_77k = [i * 200 for i in ibuff_77k]

fit_77k_ibuff = np.polyfit(xcode_ibuff_77k[18:],ibuff_77k[18:],1)
fit_fn_77k_ibuff = np.poly1d(fit_77k_ibuff)

#fig = plt.figure()
fig, ax1 = plt.subplots()
ax1.set_xlabel('Code')
ax1.set_ylabel('Amplitude(V)')
plt.title('CMOS,Internal R, VDDA2P5=2.5V,VDDD1P2=2.0V,VDDIO=2.25V')
ax1.plot(xcode_vrefp_300k,xvrefp_300k,'ko')
ax1.plot(xcode_vrefp_77k,xvrefp_77k,'bo')
ax1.plot(xcode_vrefp_300k,fit_fn_300k_vref(xcode_vrefp_300k),'k-')
ax1.plot(xcode_vrefp_77k,fit_fn_77k_vref(xcode_vrefp_77k),'b-')

ax1.legend(('VREFP RT','VERFP LN2','VREFP RT fit','VREFP LN fit'),loc='center right')
ax1.grid(True)

#ax1.text(100,0.9,'VBGR=1.20V')
#ax1.text(10,1.3,'VREF_ext = 233mV')

ax1.text(100,0.8,'V_300k = %.4fxcode + %.4f'%(fit_300k_vref[0],fit_300k_vref[1]),color='k')
ax1.text(100,0.6,'V_77k = %.4fxcode + %.4f'%(fit_77k_vref[0],fit_77k_vref[1]),color='b')

ax1.text(100,0.4,'ibuff_300k = %.4fxcode + %.4f'%(fit_300k_ibuff[0],fit_300k_ibuff[1]),color='r')
ax1.text(100,0.2,'ibuff_77k = %.4fxcode + %.4f'%(fit_77k_ibuff[0],fit_77k_ibuff[1]),color='c')

ax2=ax1.twinx()
ax2.set_ylabel('Current(uA)')
ax2.plot(xcode_ibuff_300k,ibuff_300k,'r*')
ax2.plot(xcode_ibuff_77k,ibuff_77k,'c*')

ax2.plot(xcode_ibuff_300k[21:],fit_fn_300k_ibuff(xcode_ibuff_300k[21:]),'r-')
ax2.plot(xcode_ibuff_77k[18:],fit_fn_77k_ibuff(xcode_ibuff_77k[18:]),'c-')

ax2.legend(('ibuff0 RT','ibuff0 LN2', 'ibuff0 RT fit', 'ibuff0 LN2 fit'),loc = 'upper center')

fig.tight_layout()
plt.show()
#plt.xlabel('Code')
#plt.ylabel('Amplitude(V)')
#plt.title('VREFP,300K,Internal reference, VDDA2P5=2.5V,VDDD1P2=2.0V,VDDIO=2.25V')
#plt.plot(xcode_300k_9_5pA,xvrefp_300k_9_5pA,'ko-')
#plt.plot(xcode_300k_9_5pA,xvrefp_300k_6_3uA,'go-')
#plt.plot(xcode_300k_9_5pA,xvrefp_300k_9_5uA,'bo-')
#plt.plot(xcode_300k_9_5pA,xvrefp_300k_12_6uA,'co-')
#plt.legend(('ioffset=9.5pA','ioffset=6.3uA','ioffset=9.5uA','ioffset=12.6uA'))
#plt.grid(True)
#plt.show()

    
#plt.plot(DNL_lsbs[0],'r')
#plt.plot(DNL_lsbs[1],'g')
#plt.plot(DNL_lsbs[2],'b')
#plt.plot(DNL_lsbs[3],'c')
#plt.plot(DNL_lsbs[4],'m')
#plt.plot(DNL_lsbs[5],'y')
#plt.plot(DNL_lsbs[6],'k')
#plt.plot(DNL_lsbs[7],'k')
#
#plt.xlim(start,stop)
##plt.ylim(-1,1)
#plt.legend(('chn0','chn1','chn2','chn3','chn4','chn5','chn6','chn7'))
#plt.text(start+100,0.8,'N0=%.2e,N1=%.2e,N2=%.2e,N3=%.2e,N4=%.2e,N5=%.2e,N6=%.2e,N7=%.2e'%(Ns[0],Ns[1],Ns[2],Ns[3],Ns[4],Ns[5],Ns[6],Ns[7]),color='k')
#plt.text(start+100,0.8,'N=%.2e samples,confident level > 99 percent with resolution = 0.1LSB,12-bit ADC'%Ns[0])
##plt.text(start+100,0.8,'N=%.2e samples 99%'%Ns[0])
#plt.text(start+100,0.6,'vos0=%.2fmV,vos1=%.2fmV,vos2=%.2fmV,vos3=%.2fmV,vos4=%.2fmV,vos5=%.2fmV,vos6=%.2fmV,vos7=%.2fmV'%(Vos[0]*1000,Vos[1]*1000,Vos[2]*1000,Vos[3]*1000,Vos[4]*1000,Vos[5]*1000,Vos[6]*1000,Vos[7]*1000),color='k')
#plt.text(start+100,0.4,'code range(%d~%d)'%(start,stop))
#plt.text(start+100,8,'linear range chn0  <0.5lsb(%d~%d)'%(min0,max0))
#plt.text(start+100,7.5,'linear range chn1 <0.5lsb(%d~%d)'%(min1,max1))
#plt.text(start+100,7,'linear range chn2 <0.5lsb(%d~%d)'%(min2,max2))
#plt.text(start+100,6.5,'linear range chn3 <0.5lsb(%d~%d)'%(min3,max3))
#plt.text(start+100,6,'linear range chn4 <0.5lsb(%d~%d)'%(min4,max5))
#plt.text(start+100,5.5,'linear range chn5 <0.5lsb(%d~%d)'%(min6,max6))
#plt.text(start+100,5,'linear range chn6 <0.5lsb(%d~%d)'%(min7,max7))


#ax2 = fig.add_subplot(2,1,2)
#plt.xlabel('Code')
#plt.ylabel('LSBs')
#plt.title('INL')
#plt.plot(INL_lsbs[0],'r')
#plt.plot(INL_lsbs[1],'g')
#plt.plot(INL_lsbs[2],'b')
#plt.plot(INL_lsbs[3],'c')
#plt.plot(INL_lsbs[4],'m')
#plt.plot(INL_lsbs[5],'y')
#plt.plot(INL_lsbs[6],'k')
#plt.plot(INL_lsbs[7],'k')
#plt.xlim(start,stop)
##plt.xticks(xcode,step = 5000)
##plt.text(start+100,10,'code range(%d~%d)'%(start,stop))
#plt.legend(('chn0','chn1','chn2','chn3','chn4','chn5','chn6','chn7'))
#plt.show()

#xtick = np.arange(4096) #0~4095

    