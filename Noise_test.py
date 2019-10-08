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

import numpy as np
import matplotlib.pyplot as plt
import xlrd

loc = ("E:\\Junbin\\DUNEADC_TEST\\DUNE_COLDADC\\noise\\full-chain noise.xlsx")
wb = xlrd.open_workbook(loc)
sheet = wb.sheet_by_index(0)

noise_0_5us=[]
noise_1_0us=[]
noise_2_0us=[]
noise_3_0us=[]

noise_0_5us_on=[]
noise_1_0us_on=[]
noise_2_0us_on=[]
noise_3_0us_on=[]

for i in range(16):
    noise_0_5us.append(sheet.cell_value(i+1,8))
    noise_1_0us.append(sheet.cell_value(i+1,9))
    noise_2_0us.append(sheet.cell_value(i+1,10))
    noise_3_0us.append(sheet.cell_value(i+1,11)) 
    
    noise_0_5us_on.append(sheet.cell_value(i+1,12))
    noise_1_0us_on.append(sheet.cell_value(i+1,13))
    noise_2_0us_on.append(sheet.cell_value(i+1,14))
    noise_3_0us_on.append(sheet.cell_value(i+1,15)) 

def enc(rms,gain):
    encc = rms*45/(gain*0.160217)
    return encc


noise_mean=[enc(np.mean(noise_0_5us),14),enc(np.mean(noise_1_0us),14),enc(np.mean(noise_2_0us),14),enc(np.mean(noise_3_0us),14)]
noise_std =[enc(np.std(noise_0_5us)/4,14),enc(np.std(noise_1_0us)/4,14),enc(np.std(noise_2_0us)/4,14),enc(np.std(noise_3_0us)/4,14)]

noise_mean_on=[enc(np.mean(noise_0_5us_on),14),enc(np.mean(noise_1_0us_on),14),enc(np.mean(noise_2_0us_on),14),enc(np.mean(noise_3_0us_on),14)]
noise_std_on =[enc(np.std(noise_0_5us_on)/4,14),enc(np.std(noise_1_0us_on)/4,14),enc(np.std(noise_2_0us_on)/4,14),enc(np.std(noise_3_0us_on)/4,14)]

fig = plt.figure()
#fig, ax1 = plt.subplots()
x = [0,1,2,3]
peakingt=['0.5us','1.0us','2.0us','3us']
#plt.plot(x,[noise_0_5us[0],noise_1_0us[0],noise_2_0us[0],noise_3_0us[0]])
plt.errorbar(x,noise_mean,yerr=noise_std,color='k')
plt.errorbar(x,noise_mean_on,yerr=noise_std_on,color='b')
plt.xticks(x,peakingt)
plt.title("FE+SHA+ADC, gain=14mV/fC, baseline=900mV,300K")
plt.ylabel("noise(ENC e-)")
plt.xlabel("Peaking time")
plt.legend(['buffer off','buffer on'])
plt.grid(True)
plt.show()
