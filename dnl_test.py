# -*- coding: utf-8 -*-
"""
Created on Tue Apr 16 15:33:39 2019

@author: JunbinZhang
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
    chns[i] = chns[i][1:]
    counts[i] = counts[i][1:]

e = counts[0][0] # convet str to int




print(type(e))
print(e)
print(type(counts[0]))


d = counts[0]
d = list(map(int,d))

print(type(d))
print(d[0])
print(type(d[0]))
print(sum(d))
 
#x = counts[0]
#y = sum(map(int,x.(',')))
#print(y)
#print(len(counts[0]))
#for i in range(8):
#    print(sum(counts[i]))