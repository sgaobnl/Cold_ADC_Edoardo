# -*- coding: utf-8 -*-
"""
Created on Sun Jun  2 20:38:46 2019

@author: JunbinZhang
"""
import numpy as np
import matplotlib.pyplot as plt
import xlrd


gain4_7_RT = []
gain4_7_LN = []

gain7_8_RT = []
gain7_8_LN = []

gain14_RT  = []
gain14_LN  = []

gain25_RT  = []
gain25_LN  = []

loc = ("E:\\Junbin\\DUNEADC_TEST\\DUNE_COLDADC\\Gain\\cmos_ref_gain.xlsx")
wb = xlrd.open_workbook(loc)
sheet = wb.sheet_by_index(0)

for i in range(16):
    gain4_7_RT.append(sheet.cell_value(i+1,1))
    gain4_7_LN.append(sheet.cell_value(i+1,2))

    gain7_8_RT.append(sheet.cell_value(i+1,3))
    gain7_8_LN.append(sheet.cell_value(i+1,4))
    
    gain14_RT.append(sheet.cell_value(i+1,5))
    gain14_LN.append(sheet.cell_value(i+1,6))
    
    gain25_RT.append(sheet.cell_value(i+1,7))
    gain25_LN.append(sheet.cell_value(i+1,8))


noise4_7_chn_RT=[[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
noise4_7_chn_LN=[[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]

noise7_8_chn_RT=[[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
noise7_8_chn_LN=[[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]

noise14_chn_RT =[[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
noise14_chn_LN =[[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]

noise25_chn_RT =[[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
noise25_chn_LN =[[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]

loc = ("E:\\Junbin\\DUNEADC_TEST\\DUNE_COLDADC\\Gain\\noise4_7.xlsx")
wb = xlrd.open_workbook(loc)
sheet = wb.sheet_by_index(0)
for tp in range(4):
    for i in range(16):
        noise4_7_chn_RT[i].append(sheet.cell_value(i+1,tp+1))
        noise4_7_chn_LN[i].append(sheet.cell_value(i+1,tp+6))


loc = ("E:\\Junbin\\DUNEADC_TEST\\DUNE_COLDADC\\Gain\\noise7_8.xlsx")
wb = xlrd.open_workbook(loc)
sheet = wb.sheet_by_index(0)
for tp in range(4):
    for i in range(16):
        noise7_8_chn_RT[i].append(sheet.cell_value(i+1,tp+1))
        noise7_8_chn_LN[i].append(sheet.cell_value(i+1,tp+6))


loc = ("E:\\Junbin\\DUNEADC_TEST\\DUNE_COLDADC\\Gain\\noise14.xlsx")
wb = xlrd.open_workbook(loc)
sheet = wb.sheet_by_index(0)
for tp in range(4):
    for i in range(16):
        noise14_chn_RT[i].append(sheet.cell_value(i+1,tp+1))
        noise14_chn_LN[i].append(sheet.cell_value(i+1,tp+6))

loc = ("E:\\Junbin\\DUNEADC_TEST\\DUNE_COLDADC\\Gain\\noise25.xlsx")
wb = xlrd.open_workbook(loc)
sheet = wb.sheet_by_index(0)
for tp in range(4):
    for i in range(16):
        noise25_chn_RT[i].append(sheet.cell_value(i+1,tp+1))
        noise25_chn_LN[i].append(sheet.cell_value(i+1,tp+6))        



e = 1.602E-4 # 1e = 1.602 E-4 fC
for i in range(16):
    
    noise4_7_chn_RT[i] = [item / (gain4_7_RT[i] * e) for item in noise4_7_chn_RT[i]]
    noise4_7_chn_LN[i] = [item / (gain4_7_LN[i] * e) for item in noise4_7_chn_LN[i]]

    noise7_8_chn_RT[i] = [item / (gain7_8_RT[i] * e) for item in noise7_8_chn_RT[i]]
    noise7_8_chn_LN[i] = [item / (gain7_8_LN[i] * e) for item in noise7_8_chn_LN[i]]

    noise14_chn_RT[i] = [item / (gain14_RT[i] * e) for item in noise14_chn_RT[i]]
    noise14_chn_LN[i] = [item / (gain14_LN[i] * e) for item in noise14_chn_LN[i]]

    noise25_chn_RT[i] = [item / (gain25_RT[i] * e) for item in noise25_chn_RT[i]]
    noise25_chn_LN[i] = [item / (gain25_LN[i] * e) for item in noise25_chn_LN[i]]


noise4_7_chn_RT_0_5us=[]
noise4_7_chn_RT_1us=[]
noise4_7_chn_RT_2us=[]
noise4_7_chn_RT_3us=[]

noise7_8_chn_RT_0_5us=[]
noise7_8_chn_RT_1us=[]
noise7_8_chn_RT_2us=[]
noise7_8_chn_RT_3us=[]

noise14_chn_RT_0_5us=[]
noise14_chn_RT_1us=[]
noise14_chn_RT_2us=[]
noise14_chn_RT_3us=[]

noise25_chn_RT_0_5us=[]
noise25_chn_RT_1us=[]
noise25_chn_RT_2us=[]
noise25_chn_RT_3us=[]


noise4_7_chn_LN_0_5us=[]
noise4_7_chn_LN_1us=[]
noise4_7_chn_LN_2us=[]
noise4_7_chn_LN_3us=[]

noise7_8_chn_LN_0_5us=[]
noise7_8_chn_LN_1us=[]
noise7_8_chn_LN_2us=[]
noise7_8_chn_LN_3us=[]

noise14_chn_LN_0_5us=[]
noise14_chn_LN_1us=[]
noise14_chn_LN_2us=[]
noise14_chn_LN_3us=[]

noise25_chn_LN_0_5us=[]
noise25_chn_LN_1us=[]
noise25_chn_LN_2us=[]
noise25_chn_LN_3us=[]

for i in range(16):
    noise4_7_chn_RT_0_5us.append(noise4_7_chn_RT[i][0])
    noise4_7_chn_RT_1us.append(noise4_7_chn_RT[i][1])
    noise4_7_chn_RT_2us.append(noise4_7_chn_RT[i][2])
    noise4_7_chn_RT_3us.append(noise4_7_chn_RT[i][3])
    
    noise7_8_chn_RT_0_5us.append(noise7_8_chn_RT[i][0])
    noise7_8_chn_RT_1us.append(noise7_8_chn_RT[i][1])
    noise7_8_chn_RT_2us.append(noise7_8_chn_RT[i][2])
    noise7_8_chn_RT_3us.append(noise7_8_chn_RT[i][3])
    
    noise14_chn_RT_0_5us.append(noise14_chn_RT[i][0])
    noise14_chn_RT_1us.append(noise14_chn_RT[i][1])
    noise14_chn_RT_2us.append(noise14_chn_RT[i][2])
    noise14_chn_RT_3us.append(noise14_chn_RT[i][3])
    
    noise25_chn_RT_0_5us.append(noise25_chn_RT[i][0])
    noise25_chn_RT_1us.append(noise25_chn_RT[i][1])
    noise25_chn_RT_2us.append(noise25_chn_RT[i][2])
    noise25_chn_RT_3us.append(noise25_chn_RT[i][3])
    
    noise4_7_chn_LN_0_5us.append(noise4_7_chn_LN[i][0])
    noise4_7_chn_LN_1us.append(noise4_7_chn_LN[i][1])
    noise4_7_chn_LN_2us.append(noise4_7_chn_LN[i][2])
    noise4_7_chn_LN_3us.append(noise4_7_chn_LN[i][3])
    
    noise7_8_chn_LN_0_5us.append(noise7_8_chn_LN[i][0])
    noise7_8_chn_LN_1us.append(noise7_8_chn_LN[i][1])
    noise7_8_chn_LN_2us.append(noise7_8_chn_LN[i][2])
    noise7_8_chn_LN_3us.append(noise7_8_chn_LN[i][3])
    
    noise14_chn_LN_0_5us.append(noise14_chn_LN[i][0])
    noise14_chn_LN_1us.append(noise14_chn_LN[i][1])
    noise14_chn_LN_2us.append(noise14_chn_LN[i][2])
    noise14_chn_LN_3us.append(noise14_chn_LN[i][3])
    
    noise25_chn_LN_0_5us.append(noise25_chn_LN[i][0])
    noise25_chn_LN_1us.append(noise25_chn_LN[i][1])
    noise25_chn_LN_2us.append(noise25_chn_LN[i][2])
    noise25_chn_LN_3us.append(noise25_chn_LN[i][3])

chn_s = 14

chn_rt_0_5us=[noise4_7_chn_RT_0_5us[chn_s],noise7_8_chn_RT_0_5us[chn_s],noise14_chn_RT_0_5us[chn_s],noise25_chn_RT_0_5us[chn_s]]
chn_rt_1us=[noise4_7_chn_RT_1us[chn_s],noise7_8_chn_RT_1us[chn_s],noise14_chn_RT_1us[chn_s],noise25_chn_RT_1us[chn_s]]
chn_rt_2us=[noise4_7_chn_RT_2us[chn_s],noise7_8_chn_RT_2us[chn_s],noise14_chn_RT_2us[chn_s],noise25_chn_RT_2us[chn_s]]
chn_rt_3us=[noise4_7_chn_RT_3us[chn_s],noise7_8_chn_RT_3us[chn_s],noise14_chn_RT_3us[chn_s],noise25_chn_RT_3us[chn_s]]

chn_ln_0_5us=[noise4_7_chn_LN_0_5us[chn_s],noise7_8_chn_LN_0_5us[chn_s],noise14_chn_LN_0_5us[chn_s],noise25_chn_LN_0_5us[chn_s]]
chn_ln_1us=[noise4_7_chn_LN_1us[chn_s],noise7_8_chn_LN_1us[chn_s],noise14_chn_LN_1us[chn_s],noise25_chn_LN_1us[chn_s]]
chn_ln_2us=[noise4_7_chn_LN_2us[chn_s],noise7_8_chn_LN_2us[chn_s],noise14_chn_LN_2us[chn_s],noise25_chn_LN_2us[chn_s]]
chn_ln_3us=[noise4_7_chn_LN_3us[chn_s],noise7_8_chn_LN_3us[chn_s],noise14_chn_LN_3us[chn_s],noise25_chn_LN_3us[chn_s]]

x = np.arange(4)
x_tp = ['4.7mV/fC','7.8mV/fC','14mV/fC','25mV/fC']
fig = plt.figure()
plt.title('Cd=150pF,buffer off')
plt.xlabel('gain')
plt.ylabel('ENC e-')

plt.plot(x,chn_rt_0_5us,'ko-',label='RT-chn14-0.5us')
plt.plot(x,chn_rt_1us,'ro-',label='RT-chn14-1us')
plt.plot(x,chn_rt_2us,'bo-',label='RT-chn14-2us')
plt.plot(x,chn_rt_3us,'go-',label='RT-chn14-3us')

plt.plot(x,chn_ln_0_5us,'k*--',label='LN-chn14-0.5us')
plt.plot(x,chn_ln_1us,'r*--',label='LN-chn14-1us')
plt.plot(x,chn_ln_2us,'b*--',label='LN-chn14-2us')
plt.plot(x,chn_ln_3us,'g*--',label='LN-chn14-3us')

plt.xticks(x,x_tp)
plt.grid(True)
plt.legend(loc='upper right')
plt.show()


#x = np.arange(16)
#fig = plt.figure()
#plt.title('Cd=150pF,peaking time=2us,buffer off')
#plt.xlabel('chn')
#plt.ylabel('ENC e-')
#
#plt.plot(noise4_7_chn_RT_2us,'ko-',label='RT-4.7mV/fC')
#plt.plot(noise7_8_chn_RT_2us,'ro-',label='RT-7.8mV/fC')
#plt.plot(noise14_chn_RT_2us,'bo-',label='RT-14mV/fC')
#plt.plot(noise25_chn_RT_2us,'go-',label='RT-25mV/fC')
#
#plt.plot(noise4_7_chn_LN_2us,'k*--',label='LN-4.7mV/fC')
#plt.plot(noise7_8_chn_LN_2us,'r*--',label='LN-7.8mV/fC')
#plt.plot(noise14_chn_LN_2us,'b*--',label='LN-14mV/fC')
#plt.plot(noise25_chn_LN_2us,'g*--',label='LN-25mV/fC')
#
##plt.xticks(x,x_tp)
#plt.grid(True)
#plt.legend(loc='upper right')
#plt.show()




#x = np.arange(4)
#x_tp = ['0.5us','1us','2us','3us']
#
#fig = plt.figure()
#plt.title('Cd=150pF, noise-chn14')
#plt.xlabel('peaking time')
#plt.ylabel('ENC e-')
#plt.plot(x,noise4_7_chn_RT[chn_s],'ko-',label='RT-chn14-4.7mV/fC')
#plt.plot(x,noise7_8_chn_RT[chn_s],'ro-',label='RT-chn14-7.8mV/fC')
#plt.plot(x,noise14_chn_RT[chn_s],'bo-',label='RT-chn14-14mV/fC')
#plt.plot(x,noise25_chn_RT[chn_s],'go-',label='RT-chn14-25mV/fC')
#
#plt.plot(x,noise4_7_chn_LN[chn_s],'k*--',label='LN-chn14-4.7mV/fC')
#plt.plot(x,noise7_8_chn_LN[chn_s],'r*--',label='LN-chn14-7.8mV/fC')
#plt.plot(x,noise14_chn_LN[chn_s],'b*--',label='LN-chn14-14mV/fC')
#plt.plot(x,noise25_chn_LN[chn_s],'g*--',label='LN-chn14-25mV/fC')
#
#plt.xticks(x,x_tp)
#plt.grid(True)
#plt.legend()
#plt.show()





