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
from brd_config import Brd_Config
from frame import Frames

chns =   [[],[],[],[],[],[],[],[]]
counts = [[],[],[],[],[],[],[],[]]

with open('D:\python_workspace\DUNE_COLDADC\data\ADC0_all.csv') as csvfile:
    readCSV = csv.reader(csvfile,delimiter=',')
    for row in readCSV:    
        #print(row)       
       chns[0].append(row[0])
       counts[0].append(row[1])
       
       chns[1].append(row[2])
       counts[1].append(row[3])
       
       chns[2].append(row[4])
       counts[2].append(row[5])
       
       chns[3].append(row[6])
       counts[3].append(row[7])
       
       chns[4].append(row[8])
       counts[4].append(row[9])
       
       chns[5].append(row[10])
       counts[5].append(row[11])
       
       chns[6].append(row[12])
       counts[6].append(row[13])
       
       chns[7].append(row[14])
       counts[7].append(row[15])
csvfile.close()

start = 1
stop  = 4094


for i in range(8):
    chns[i] = chns[i][2:-1]
    counts[i] = counts[i][2:-1]
#now we have the channels and counts, but they are all in str type
    
#convert them to lists of int
for i in range(8):
    chns[i] = list(map(int,chns[i][start-1:stop]))
    counts[i] = list(map(int,counts[i][start-1:stop]))






Nu = [] #number of times the upper code is hit
Nl = [] #number of times the lower code is hit
Ns = [] #number of samples(total sum of code occurrences)
N = 12 #is the convert resolution
for i in range(8):
    Nu.append(counts[i][-1])
    Nl.append(counts[i][0])
    Ns.append(sum(counts[i]))

Xu=[] #
Xl=[] #

for i in range(8):    
    Xu_tp = math.cos(math.pi*Nu[i]/Ns[i])
    Xl_tp = math.cos(math.pi*Nl[i]/Ns[i])
    Xu.append(Xu_tp)
    Xl.append(Xl_tp)

    
offset_lsbs=[] #(LSB)
  
for i in range(8):      
    offset_lsbs_tp = ((Xl[i] - Xu[i])/(Xl[i]+Xu[i]))*(math.pow(2,(N-1))-1)
    offset_lsbs.append(offset_lsbs_tp)
    
peak_lsbs=[]   #(LSB)  
for i in range(8):   
    peak_lsbs_tp = (math.pow(2,(N-1)) - 1- offset_lsbs[i])/Xu[i]
    peak_lsbs.append(peak_lsbs_tp)
    
# now we get the offset and amplitude, the ideal distribution of code hits can be calculated.
Ideal_counts = [[],[],[],[],[],[],[],[]]    
for i in range(8):
    for code in range(1,4095,1): #1->4094
        res = Ns[i]/math.pi * (math.asin((code+1 - math.pow(2,(N-1))-offset_lsbs[i])/peak_lsbs[i]) - math.asin((code - math.pow(2,(N-1))-offset_lsbs[i])/peak_lsbs[i]) )
        Ideal_counts[i].append(res)

DNL_lsbs= [[],[],[],[],[],[],[],[]]  

for chn in range(8):
    for code in range(len(counts[0])):
        res = (counts[chn][code]/Ideal_counts[chn][code]) -1
        DNL_lsbs[chn].append(res)


INL_lsbs= [[],[],[],[],[],[],[],[]]  
for chn in range(8):
    for code in range(len(DNL_lsbs[0])):# change range here
        if code == 0:
            INL_lsbs[chn].append(DNL_lsbs[chn][0])
        else:
            res = sum(DNL_lsbs[chn][0:code+1])
            INL_lsbs[chn].append(res)  



fig = plt.figure()
ax3 = fig.add_subplot(3,1,1)

plt.ylabel('counts')
plt.title('ADC0 DNL sine vpp=3.04V freq=11kHz, test input')
plt.plot(counts[0])
plt.xlim(start,stop)
plt.text(start+100,50000,'N=%.2e samples,confident level > 99 percent with resolution = 0.1LSB,12-bit ADC'%Ns[0])
plt.text(start+100,40000,'code range(%d~%d)'%(start,stop))



ax1 = fig.add_subplot(3,1,2)
plt.ylabel('LSBs')
plt.plot(DNL_lsbs[0],'r')
plt.plot(DNL_lsbs[1],'g')
plt.plot(DNL_lsbs[2],'b')
plt.plot(DNL_lsbs[3],'c')
plt.plot(DNL_lsbs[4],'m')
plt.plot(DNL_lsbs[5],'y')
plt.plot(DNL_lsbs[6],'k')
plt.plot(DNL_lsbs[7],'k')
plt.xlim(start,stop)
#plt.ylim(-1,1)
plt.legend(('chn0','chn1','chn2','chn3','chn4','chn5','chn6','chn7'))
plt.text(start+100,0.8,'offset=%.3f LSB'%offset_lsbs[0],color='k')


#plt.text(start+100,8,'linear range chn0  <0.5lsb(%d~%d)'%(min0,max0))
#plt.text(start+100,7.5,'linear range chn1 <0.5lsb(%d~%d)'%(min1,max1))
#plt.text(start+100,7,'linear range chn2 <0.5lsb(%d~%d)'%(min2,max2))
#plt.text(start+100,6.5,'linear range chn3 <0.5lsb(%d~%d)'%(min3,max3))
#plt.text(start+100,6,'linear range chn4 <0.5lsb(%d~%d)'%(min4,max5))
#plt.text(start+100,5.5,'linear range chn5 <0.5lsb(%d~%d)'%(min6,max6))
#plt.text(start+100,5,'linear range chn6 <0.5lsb(%d~%d)'%(min7,max7))


ax2 = fig.add_subplot(3,1,3)
plt.xlabel('Code')
plt.ylabel('LSBs')
plt.title('INL')
plt.plot(INL_lsbs[0],'r')
plt.plot(INL_lsbs[1],'g')
plt.plot(INL_lsbs[2],'b')
plt.plot(INL_lsbs[3],'c')
plt.plot(INL_lsbs[4],'m')
plt.plot(INL_lsbs[5],'y')
plt.plot(INL_lsbs[6],'k')
plt.plot(INL_lsbs[7],'k')
plt.xlim(start,stop)
#plt.xticks(xcode,step = 5000)
#plt.text(start+100,10,'code range(%d~%d)'%(start,stop))
plt.legend(('chn0','chn1','chn2','chn3','chn4','chn5','chn6','chn7'))
plt.show()



#xtick = np.arange(4096) #0~4095

    