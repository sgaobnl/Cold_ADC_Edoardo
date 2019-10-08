# -*- coding: utf-8 -*-
"""
Created on Wed Feb 27 10:04:12 2019

@author: JunbinZhang
"""

import matplotlib.pyplot as plt
#import os.path
import xlrd #read
import numpy as np
import time

#give the location of the file
uncali_loc = "D:\\python_workspace\\DUNE_COLDADC\\sine_11k_1485_uncali.xls"

wb = xlrd.open_workbook(uncali_loc)

uncali_data = [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]

sheet = wb.sheet_by_index(0)

for col in range(16):
    for row in range(1,1001):
        uncali_data[col].append(sheet.cell_value(row,col))
      
        
adc0_chn0_uncali = uncali_data[0]


adc1_chn0_uncali = uncali_data[8]




        
fig = plt.figure()
ax1 = fig.add_subplot(2,1,1)
plt.xlabel('ADC code')
plt.ylabel('counts')
plt.title('ADC0')
#plt.plot(adc0_chn0_uncali,'b*')
plt.hist(adc0_chn0_uncali,4096)


#plt.legend(('uncali','cali','uncali_fit','cali_fit'))
#plt.text(10,30000,text1)
#plt.text(10,40000,text2)


ax2 = fig.add_subplot(2,1,2)
plt.xlabel('ADC code')
plt.ylabel('counts')
plt.title('ADC1')
#plt.plot(adc1_chn0_uncali,'b*')
plt.hist(adc1_chn0_uncali,4096)

plt.show()