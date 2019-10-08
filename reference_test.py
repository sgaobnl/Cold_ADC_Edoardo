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

xcode_300k_9_5pA=[]
xvrefp_300k_9_5pA=[]

xcode_300k_6_3uA=[]
xvrefp_300k_6_3uA=[]

xcode_300k_9_5uA=[]
xvrefp_300k_9_5uA=[]

xcode_300k_12_6uA=[]
xvrefp_300k_12_6uA=[]
#open 1
with open('E:\Junbin\DUNEADC_TEST\DUNE_COLDADC\monitor\\vrefp_vdd2p5_300k_vref_bjt_9.5pA.csv') as csvfile:
    readCSV = csv.reader(csvfile,delimiter=',')
    for row in readCSV:    
        xcode_300k_9_5pA.append(row[0])
        xvrefp_300k_9_5pA.append(row[1])
csvfile.close()

xcode_300k_9_5pA = xcode_300k_9_5pA[1:]
xvrefp_300k_9_5pA= xvrefp_300k_9_5pA[1:]
xcode_300k_9_5pA = list(map(int,xcode_300k_9_5pA))
xvrefp_300k_9_5pA = list(map(float,xvrefp_300k_9_5pA))

fit_300k_9_5pA = np.polyfit(xcode_300k_9_5pA[3:],xvrefp_300k_9_5pA[3:],1)
fit_fn_300k_9_5pA = np.poly1d(fit_300k_9_5pA)


#open 2
with open('E:\Junbin\DUNEADC_TEST\DUNE_COLDADC\monitor\\vrefp_vdd2p5_300k_vref_bjt_6.3uA.csv') as csvfile:
    readCSV = csv.reader(csvfile,delimiter=',')
    for row in readCSV:    
        xcode_300k_6_3uA.append(row[0])
        xvrefp_300k_6_3uA.append(row[1])
csvfile.close()

xcode_300k_6_3uA = xcode_300k_6_3uA[1:]
xvrefp_300k_6_3uA= xvrefp_300k_6_3uA[1:]
xcode_300k_6_3uA = list(map(int,xcode_300k_6_3uA))
xvrefp_300k_6_3uA = list(map(float,xvrefp_300k_6_3uA))

fit_300k_6_3uA = np.polyfit(xcode_300k_6_3uA,xvrefp_300k_6_3uA,1)
fit_fn_300k_6_3uA = np.poly1d(fit_300k_6_3uA)

#open 3
with open('E:\Junbin\DUNEADC_TEST\DUNE_COLDADC\monitor\\vrefp_vdd2p5_300k_vref_bjt_9.5uA.csv') as csvfile:
    readCSV = csv.reader(csvfile,delimiter=',')
    for row in readCSV:    
        xcode_300k_9_5uA.append(row[0])
        xvrefp_300k_9_5uA.append(row[1])
csvfile.close()

xcode_300k_9_5uA = xcode_300k_9_5uA[1:]
xvrefp_300k_9_5uA= xvrefp_300k_9_5uA[1:]
xcode_300k_9_5uA = list(map(int,xcode_300k_9_5uA))
xvrefp_300k_9_5uA = list(map(float,xvrefp_300k_9_5uA))

fit_300k_9_5uA = np.polyfit(xcode_300k_9_5uA,xvrefp_300k_9_5uA,1)
fit_fn_300k_9_5uA = np.poly1d(fit_300k_9_5uA)
#open 4
with open('E:\Junbin\DUNEADC_TEST\DUNE_COLDADC\monitor\\vrefp_vdd2p5_300k_vref_bjt_12.6uA.csv') as csvfile:
    readCSV = csv.reader(csvfile,delimiter=',')
    for row in readCSV:    
        xcode_300k_12_6uA.append(row[0])
        xvrefp_300k_12_6uA.append(row[1])
csvfile.close()

xcode_300k_12_6uA = xcode_300k_12_6uA[1:]
xvrefp_300k_12_6uA= xvrefp_300k_12_6uA[1:]
xcode_300k_12_6uA = list(map(int,xcode_300k_12_6uA))
xvrefp_300k_12_6uA = list(map(float,xvrefp_300k_12_6uA))

fit_300k_12_6uA = np.polyfit(xcode_300k_12_6uA,xvrefp_300k_12_6uA,1)
fit_fn_300k_12_6uA = np.poly1d(fit_300k_12_6uA)


xcode_ibuff1_300k=[]
ibuff1_300k=[]
#open 5 current
with open('E:\Junbin\DUNEADC_TEST\DUNE_COLDADC\monitor\ibuff1_vdd2p5_300k_vref_bjt.csv') as csvfile:
    readCSV = csv.reader(csvfile,delimiter=',')
    for row in readCSV:    
        xcode_ibuff1_300k.append(row[0])
        ibuff1_300k.append(row[1])
csvfile.close()

xcode_ibuff1_300k = xcode_ibuff1_300k[1:]
ibuff1_300k= ibuff1_300k[1:]
xcode_ibuff1_300k = list(map(int,xcode_ibuff1_300k))
ibuff1_300k = list(map(float,ibuff1_300k))
ibuff1_300k = [i * 200 for i in ibuff1_300k]

fit_ibuff1_300k = np.polyfit(xcode_ibuff1_300k[12:],ibuff1_300k[12:],1)
fit_fn_ibuff1_300k = np.poly1d(fit_ibuff1_300k)


xcode_ivdac1_300k=[]
ivdac1_300k=[]
#open 5 current
with open('E:\Junbin\DUNEADC_TEST\DUNE_COLDADC\monitor\ivdac1_vdd2p5_300k_vref_bjt.csv') as csvfile:
    readCSV = csv.reader(csvfile,delimiter=',')
    for row in readCSV:    
        xcode_ivdac1_300k.append(row[0])
        ivdac1_300k.append(row[1])
csvfile.close()

xcode_ivdac1_300k = xcode_ivdac1_300k[1:]
ivdac1_300k= ivdac1_300k[1:]
xcode_ivdac1_300k = list(map(int,xcode_ivdac1_300k))
ivdac1_300k = list(map(float,ivdac1_300k))
ivdac1_300k = [i * 200 for i in ivdac1_300k]

fit_ivdac1_300k = np.polyfit(xcode_ivdac1_300k[12:],ivdac1_300k[12:],1)
fit_fn_ivdac1_300k = np.poly1d(fit_ivdac1_300k)

#fig = plt.figure()
fig, ax1 = plt.subplots()
ax1.set_xlabel('Code')
ax1.set_ylabel('Amplitude(V)')
plt.title('BJT,300K,Internal reference, VDDA2P5=2.5V,VDDD1P2=2.0V,VDDIO=2.25V')
ax1.plot(xcode_300k_9_5pA,xvrefp_300k_9_5pA,'ko')
ax1.plot(xcode_300k_9_5pA,xvrefp_300k_6_3uA,'go')
ax1.plot(xcode_300k_9_5pA,xvrefp_300k_9_5uA,'bo')
ax1.plot(xcode_300k_9_5pA,xvrefp_300k_12_6uA,'co')

ax1.plot(xcode_300k_9_5pA[3:],fit_fn_300k_9_5pA(xcode_300k_9_5pA[3:]),'k-')
ax1.plot(xcode_300k_9_5pA,fit_fn_300k_6_3uA(xcode_300k_9_5pA),'g-')
ax1.plot(xcode_300k_9_5pA,fit_fn_300k_9_5uA(xcode_300k_9_5pA),'b-')
ax1.plot(xcode_300k_9_5pA,fit_fn_300k_12_6uA(xcode_300k_9_5pA),'c-')

ax1.legend(('VREFP ioffset=9.5pA','VERFP ioffset=6.3uA','VREFP ioffset=9.5uA','VREFP ioffset=12.6uA','fit-ioffset=9.5pA','fit-ioffset=6.3uA','fit-ioffset=9.5uA','fit-ioffset=12.6uA'),loc = 'lower center')
ax1.grid(True)
ax1.text(0,2.2,'VBGR=1.20V')
ax1.text(0,2.1,'VREF_ext = 233mV')

#fit_300k_9_5pA
ax1.text(0,1.9,'V(9.5pA) = %.4fxcode + (%.4f)'%(fit_300k_9_5pA[0],fit_300k_9_5pA[1]),color='k')
ax1.text(0,1.8,'V(6.3uA) = %.4fxcode + %.4f'%(fit_300k_6_3uA[0],fit_300k_6_3uA[1]),color='g')
ax1.text(0,1.7,'V(9.5uA) = %.4fxcode + %.4f'%(fit_300k_9_5uA[0],fit_300k_9_5uA[1]),color='b')
ax1.text(0,1.6,'V(12.6uA) = %.4fxcode + %.4f'%(fit_300k_12_6uA[0],fit_300k_12_6uA[1]),color='c')

ax1.text(0,1.4,'ibuff1 = %.4fxcode + %.4f'%(fit_ibuff1_300k[0], fit_ibuff1_300k[1]),color='m')
ax1.text(0,1.3,'ivdac1 = %.4fxcode + %.4f'%(fit_ivdac1_300k[0], fit_ivdac1_300k[1]),color='r')

ax2=ax1.twinx()
ax2.set_ylabel('Current(uA)')
ax2.plot(xcode_ibuff1_300k,ibuff1_300k,'m*')
ax2.plot(xcode_ibuff1_300k,ivdac1_300k,'r*')
ax2.plot(xcode_ibuff1_300k[12:],fit_fn_ibuff1_300k(xcode_ibuff1_300k[12:]),'m-')
ax2.plot(xcode_ibuff1_300k[12:],fit_fn_ivdac1_300k(xcode_ibuff1_300k[12:]),'r-')


ax2.legend(('ibuff1 current','ivdac1 current','fit-ibuff1','fit-ivdac1'),loc = 'upper center')



fig.tight_layout()
plt.show()

    