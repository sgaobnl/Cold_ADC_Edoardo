# -*- coding: utf-8 -*-
"""
Created on Sun Jun  2 20:38:46 2019

@author: JunbinZhang
"""
import numpy as np
import matplotlib.pyplot as plt
import xlrd

loc = ("E:\\Junbin\\DUNEADC_TEST\\DUNE_COLDADC\\xtalk\\xtalk.xlsx")
wb = xlrd.open_workbook(loc)
sheet = wb.sheet_by_index(0)

xtalk_m_chn0 = []
xtalk_m_chn3 = []
xtalk_m_chn7 = []
xtalk_m_chn8 = []
xtalk_m_chn11= []
xtalk_m_chn15= []

xtalk_c_chn0 = []
xtalk_c_chn3 = []
xtalk_c_chn7 = []
xtalk_c_chn8 = []
xtalk_c_chn11= []
xtalk_c_chn15= []

for i in range(16):
    xtalk_m_chn0.append(sheet.cell_value(i+1,0))
    xtalk_m_chn3.append(sheet.cell_value(i+1,1))
    xtalk_m_chn7.append(sheet.cell_value(i+1,2))
    xtalk_m_chn8.append(sheet.cell_value(i+1,3))
    xtalk_m_chn11.append(sheet.cell_value(i+1,4))
    xtalk_m_chn15.append(sheet.cell_value(i+1,5))
    xtalk_c_chn0.append(sheet.cell_value(i+1,6))
    xtalk_c_chn3.append(sheet.cell_value(i+1,7))
    xtalk_c_chn7.append(sheet.cell_value(i+1,8))
    xtalk_c_chn8.append(sheet.cell_value(i+1,9))
    xtalk_c_chn11.append(sheet.cell_value(i+1,10))
    xtalk_c_chn15.append(sheet.cell_value(i+1,11))    

x = np.arange(16)
chn = ['chn0','chn1','chn2','chn3','chn4','chn5','chn6','chn7','chn8','chn9','chn10','chn11','chn12','chn13','chn14','chn15']

fig = plt.figure()
ax1 = fig.add_subplot(2,1,1)
plt.bar(x,xtalk_m_chn0,log=True,width=0.35,color='black',alpha=0.2)
plt.bar(x,xtalk_m_chn3,log=True,width=0.35,color='red',alpha=0.2)
plt.bar(x,xtalk_m_chn7,log=True,width=0.35,color='green',alpha=0.2)
plt.bar(x,xtalk_m_chn8,log=True,width=0.35,color='blue',alpha=0.2)
plt.bar(x,xtalk_m_chn11,log=True,width=0.35,color='cyan',alpha=0.2)
plt.bar(x,xtalk_m_chn15,log=True,width=0.35,color='m',alpha=0.2)
plt.xticks(x,chn)
plt.title("Xtalk at Warm")
plt.ylabel("xtalk")
plt.legend(['pluse chn0','pulse chn3','pulse chn7','pulse chn8','pulse chn11','pulse chn15'])

ax2=fig.add_subplot(2,1,2)
plt.bar(x,xtalk_c_chn0,log=True,width=0.35,color='black',alpha=0.2)
plt.bar(x,xtalk_c_chn3,log=True,width=0.35,color='red',alpha=0.2)
plt.bar(x,xtalk_c_chn7,log=True,width=0.35,color='green',alpha=0.2)
plt.bar(x,xtalk_c_chn8,log=True,width=0.35,color='blue',alpha=0.2)
plt.bar(x,xtalk_c_chn11,log=True,width=0.35,color='cyan',alpha=0.2)
plt.bar(x,xtalk_c_chn15,log=True,width=0.35,color='m',alpha=0.2)
plt.xticks(x,chn)
plt.title("Xtalk at Cold")
plt.ylabel("xtalk")
plt.legend(['pluse chn0','pulse chn3','pulse chn7','pulse chn8','pulse chn11','pulse chn15'])
#plt.yscale('log')
#t = sheet.cell_value(1,0)
#print(type(t))
#xtalk_m_chn0 = [100,0.585,0.151,0.087,0.085,0.083,0.194,0.051,0.067,0.058,0.060,0.063,0.041,0.011,0.034,0.036]

#fig = plt.figure()
#ax1 = fig.add_subplot()
#ax1.plot(xtalk_m_chn0,'ko')
#ax1.grid(True)
#ax1.set(ylabel='percent(%)',title = 'Xtalk chn0')
#ax1.set_xlim(0,10)

#ax2 = fig.add_subplot(212)
#ax2.plot(Attenuation,powdbm,'ko')
#ax2.grid(True)
#ax2.set(xlabel='Attenuation setting (dB)',ylabel='Power/dBm')
#
#ax2.set_xlim(0,10)
#plt.show()
#fig,ax = plt.subplots()
#ax.plot(Attenuation,powdbm,'bo')
#ax.set(xlabel='Attenuation setting (dB)',ylable='MINIPOD_RX1 chn7 power measurement (dBm)', title = 'Power measurement vs Attenuation')
plt.show()