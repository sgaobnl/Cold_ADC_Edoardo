# -*- coding: utf-8 -*-
"""
Created on Fri Mar 29 14:03:46 2019

@author: JunbinZhang
"""
import matplotlib.pyplot as plt
import numpy as np
import re
#from brd_config import Brd_Config

filename = "E:\\Junbin\\DUNEADC_TEST\\DUNE_COLDADC\\calis\\time23_stage1.txt"
adc0_s0=[]
adc0_s1=[]
adc0_s2=[]
adc0_s3=[]
adc1_s0=[]
adc1_s1=[]
adc1_s2=[]
adc1_s3=[]

file = open(filename,'r')
for line in file:
    if line[0] == '#':
        continue
    else:
        c = [int(e,0) for e in line.split(",")]
        adc0_s0.append(c[0])
        adc0_s1.append(c[1])
        adc0_s2.append(c[2])
        adc0_s3.append(c[3])
        
        adc1_s0.append(c[4])
        adc1_s1.append(c[5])
        adc1_s2.append(c[6])
        adc1_s3.append(c[7])        
file.close()

#print(adc0_s0[0])
#print(adc0_s1[0])
#print(adc0_s2[0])
#print(adc0_s3[0])


fig = plt.figure(1,figsize=(10.0,8.0))
fig.add_subplot(2,2,1)
plt.ylabel('counts')
plt.title('S0')
plt.hist(adc0_s0)

fig.add_subplot(2,2,2)
plt.ylabel('counts')
plt.title('S1')
plt.hist(adc0_s1)

fig.add_subplot(2,2,3)
plt.xlabel('ADC code')
plt.ylabel('counts')
plt.title('S2')
plt.hist(adc0_s2)

fig.add_subplot(2,2,4)
plt.xlabel('ADC code')
plt.ylabel('counts')
plt.title('S3')

plt.hist(adc0_s3)

#Figure2
fig = plt.figure(2,figsize=(10.0,8.0))
fig.add_subplot(2,2,1)
plt.ylabel('counts')
plt.title('S0')
plt.hist(adc1_s0)

fig.add_subplot(2,2,2)
plt.ylabel('counts')
plt.title('S1')
plt.hist(adc1_s1)

fig.add_subplot(2,2,3)
plt.xlabel('ADC code')
plt.ylabel('counts')
plt.title('S2')
plt.hist(adc1_s2)

fig.add_subplot(2,2,4)
plt.xlabel('ADC code')
plt.ylabel('counts')
plt.title('S3')

plt.hist(adc1_s3)




plt.show()