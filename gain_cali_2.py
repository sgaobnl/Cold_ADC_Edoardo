# -*- coding: utf-8 -*-
"""
Created on Sun Jun  2 20:38:46 2019

@author: JunbinZhang
"""
import numpy as np
import matplotlib.pyplot as plt
import xlrd
loc = ("E:\\Junbin\\DUNEADC_TEST\\DUNE_COLDADC\\Gain\\cmos_ref_gain25.xlsx")
wb = xlrd.open_workbook(loc)
sheet = wb.sheet_by_index(0)

gain4_7_chn_RT=[[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
gain4_7_chn_LN=[[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]

for dac in range(5):
    for i in range(16):
        gain4_7_chn_RT[i].append(sheet.cell_value(i+1,dac+1))
        gain4_7_chn_LN[i].append(sheet.cell_value(i+1,dac+7))


gian4_7_dac_real = [1,2,3,4,5]

gain4_7_dac_charge = []
for dac in gian4_7_dac_real:    
    charge = (0.038294*dac-0.000148)*185
    charge = round(charge,1)
    gain4_7_dac_charge.append(charge)

x = np.arange(5)
gain4_7_dac = [str(x) for x in gain4_7_dac_charge]


fit_gain4_7_RT=[]
fit_fn_gain4_7_RT=[]
fit_gain4_7_LN=[]
fit_fn_gain4_7_LN=[]

for chn in range(16):
    fit_gain4_7_RT_tem = np.polyfit(gain4_7_dac_charge,gain4_7_chn_RT[chn],1)
    fit_fn_gain4_7_RT_tem = np.poly1d(fit_gain4_7_RT_tem)

    fit_gain4_7_LN_tem = np.polyfit(gain4_7_dac_charge,gain4_7_chn_LN[chn],1)
    fit_fn_gain4_7_LN_tem = np.poly1d(fit_gain4_7_LN_tem)
    
    fit_gain4_7_RT.append(fit_gain4_7_RT_tem)
    fit_fn_gain4_7_RT.append(fit_fn_gain4_7_RT_tem)
    fit_gain4_7_LN.append(fit_gain4_7_LN_tem)
    fit_fn_gain4_7_LN.append(fit_fn_gain4_7_LN_tem)

#if 1LSB = 45uV


for chn in range(16):
    print('chn%d-gain-RT/LN=%.2f,%.2f counts/fC'%(chn,fit_gain4_7_RT[chn][0], fit_gain4_7_LN[chn][0]))
    
LSB=0.045 # 1LSB = 45uV = 0.045mV
fig = plt.figure()
plt.title('Gain=4.7mV/fC calibration')
plt.xlabel('Charge(fC)')
plt.ylabel('Amplitude(ADC Counts)')
plt.plot(x,gain4_7_chn_RT[1],'r*-',label='RT-chn1')
plt.plot(x,gain4_7_chn_LN[1],'bo-',label='LN-chn1')

plt.text(1,20000,'chn1-gain=%.2f mV/fC'%(fit_gain4_7_RT[1][0]*LSB),color='r')
plt.text(1,19000,'chn1-gain=%.2f mV/fC'%(fit_gain4_7_LN[1][0]*LSB),color='b')

#plt.xticks(x,gain4_7_dac)
plt.grid(True)
plt.legend()
plt.show()



