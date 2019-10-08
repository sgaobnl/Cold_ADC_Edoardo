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
#give the location of the file

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



for i in range(8):
    chns[i] = chns[i][2:-1]
    counts[i] = counts[i][2:-1]
#now we have the channels and counts, but they are all in str type
    
#convert them to lists of int
for i in range(8):
    chns[i] = list(map(int,chns[i]))
    counts[i] = list(map(int,counts[i]))    


Ns = [] #number of samples(total sum of code occurrences)
for i in range(8):
    Ns.append(sum(counts[i]))

N = 12 #is the convert resolution
A = 1.52
VREFP=1.9
VREFN=0.4
VF = 2*(VREFP-VREFN)

for i in range(8):
    Ns.append(sum(counts[i]))

#Actual posibility
PA = [[],[],[],[],[],[],[],[]]

for chn in range(8):
    for code in range(4096):
         res = counts[chn][code]/Ns[chn]
         PA[chn].append(res)
        
Nrn=[]
Nrp=[]
Nr =[]
for chn in range(8):
    Nrn.append(sum(PA[chn][0:2048]))
    Nrp.append(sum(PA[chn][2049:]))
    Nr.append(sum(PA[chn][0:2048]) + sum(PA[chn][2049:]))

Vos=[]

for chn in range(8):
    offset = 0.5*A*math.pi*math.sin((Nrp[chn] - Nrn[chn])/Nr[chn])
    Vos.append(offset)
    
    
Vi = [[],[],[],[],[],[],[],[]]   

for chn in range(8):
    for code in range(4096):    
        v = (-1)*A*math.cos(math.pi* sum(PA[chn][0:code+1])/Nr[chn])
        Vi[chn].append(v)


DNL_lsbs= [[],[],[],[],[],[],[],[]]  

for chn in range(8):
    #4094
    for code in range(4095):
        res = (Vi[chn][code+1] - Vi[chn][code])*(math.pow(2,N)/VF) -1
        DNL_lsbs[chn].append(res)

#print(len(DNL_lsbs[0]))
DNL_lsbs[0] = DNL_lsbs[0][40:4067]
DNL_lsbs[1] = DNL_lsbs[0][40:4067]   
DNL_lsbs[2] = DNL_lsbs[0][40:4067]   
DNL_lsbs[3] = DNL_lsbs[0][40:4067]   
DNL_lsbs[4] = DNL_lsbs[0][40:4067]   
DNL_lsbs[5] = DNL_lsbs[0][40:4067]          
DNL_lsbs[6] = DNL_lsbs[0][40:4067] 
DNL_lsbs[7] = DNL_lsbs[0][40:4067]        
#DNL_lsbs_linear = [[],[],[],[],[],[],[],[]] 
#for chn in range(8):
#    #4094
#    DNL_lsbs_linear[chn] = DNL_lsbs[chns][40:4067]
# 



INL_lsbs= [[],[],[],[],[],[],[],[]]  
for chn in range(8):
    for code in range(4027):# change range here
        if code == 0:
            INL_lsbs[chn].append(DNL_lsbs[chn][0])
        else:
            res = sum(DNL_lsbs[chn][0:code+1])
            INL_lsbs[chn].append(res)


#def linear_range(lista):
#    arr = [i for i, x in enumerate(lista) if x < 0.5]
#    for i in range(len(arr)-1):
#        if (arr[i+1] - arr[i] != 1):
#            t = i+1
#        else:
#            continue
#    return[arr[t],arr[-1]]

    
#min0,max0 = linear_range(DNL_lsbs[0])
#min1,max1 = linear_range(DNL_lsbs[1])
#min2,max2 = linear_range(DNL_lsbs[2])
#min3,max3 = linear_range(DNL_lsbs[3])
#min4,max4 = linear_range(DNL_lsbs[4])
#min5,max5 = linear_range(DNL_lsbs[5])
#min6,max6 = linear_range(DNL_lsbs[6])
#min7,max7 = linear_range(DNL_lsbs[7])


start = 40
stop  = 4066

fig = plt.figure()
ax1 = fig.add_subplot(2,1,1)




plt.ylabel('LSBs')
plt.title('ADC0 DNL (sine vpp=3.04V, freq=11kHz, test input)')
plt.plot(DNL_lsbs[0][start:stop],'r')
plt.plot(DNL_lsbs[1][start:stop],'g')
plt.plot(DNL_lsbs[2][start:stop],'b')
plt.plot(DNL_lsbs[3][start:stop],'c')
plt.plot(DNL_lsbs[4][start:stop],'m')
plt.plot(DNL_lsbs[5][start:stop],'y')
plt.plot(DNL_lsbs[6][start:stop],'k')
plt.plot(DNL_lsbs[7][start:stop],'k')




plt.xlim(start,stop)

plt.ylim(-1,1)
plt.legend(('chn0','chn1','chn2','chn3','chn4','chn5','chn6','chn7'))
#plt.text(start+100,0.8,'N0=%.2e,N1=%.2e,N2=%.2e,N3=%.2e,N4=%.2e,N5=%.2e,N6=%.2e,N7=%.2e'%(Ns[0],Ns[1],Ns[2],Ns[3],Ns[4],Ns[5],Ns[6],Ns[7]),color='k')
plt.text(start+100,0.8,'N=%.2e samples,confident level > 99 percent with resolution = 0.1LSB,12-bit ADC'%Ns[0])
#plt.text(start+100,0.8,'N=%.2e samples 99%'%Ns[0])
plt.text(start+100,0.6,'vos0=%.2fmV,vos1=%.2fmV,vos2=%.2fmV,vos3=%.2fmV,vos4=%.2fmV,vos5=%.2fmV,vos6=%.2fmV,vos7=%.2fmV'%(Vos[0]*1000,Vos[1]*1000,Vos[2]*1000,Vos[3]*1000,Vos[4]*1000,Vos[5]*1000,Vos[6]*1000,Vos[7]*1000),color='k')
plt.text(start+100,0.4,'code range(%d~%d)'%(start,stop))

#plt.text(start+100,8,'linear range chn0  <0.5lsb(%d~%d)'%(min0,max0))
#plt.text(start+100,7.5,'linear range chn1 <0.5lsb(%d~%d)'%(min1,max1))
#plt.text(start+100,7,'linear range chn2 <0.5lsb(%d~%d)'%(min2,max2))
#plt.text(start+100,6.5,'linear range chn3 <0.5lsb(%d~%d)'%(min3,max3))
#plt.text(start+100,6,'linear range chn4 <0.5lsb(%d~%d)'%(min4,max5))
#plt.text(start+100,5.5,'linear range chn5 <0.5lsb(%d~%d)'%(min6,max6))
#plt.text(start+100,5,'linear range chn6 <0.5lsb(%d~%d)'%(min7,max7))


ax2 = fig.add_subplot(2,1,2)
plt.xlabel('Code')
plt.ylabel('LSBs')
plt.title('INL')
plt.plot(INL_lsbs[0][start:stop],'r')
plt.plot(INL_lsbs[1][start:stop],'g')
plt.plot(INL_lsbs[2][start:stop],'b')
plt.plot(INL_lsbs[3][start:stop],'c')
plt.plot(INL_lsbs[4][start:stop],'m')
plt.plot(INL_lsbs[5][start:stop],'y')
plt.plot(INL_lsbs[6][start:stop],'k')
plt.plot(INL_lsbs[7][start:stop],'k')
plt.xlim(start,stop)
#plt.xticks(xcode,step = 5000)
plt.text(start+100,10,'code range(%d~%d)'%(start,stop))
plt.legend(('chn0','chn1','chn2','chn3','chn4','chn5','chn6','chn7'))
plt.show()

#xtick = np.arange(4096) #0~4095

    