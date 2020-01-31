# -*- coding: utf-8 -*-
"""
Created on Wed Jul 24 00:00:54 2019

@author: protoDUNE
"""

import numpy as np
import os
from sys import exit
import os.path
import math
import time
import statsmodels.api as sm

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
import matplotlib.mlab as mlab
import pickle
from scipy.stats import norm

runpath = "D:/ColdADC/QC_Data/"

if (os.path.exists(runpath)):
    for root, dirs, files in os.walk(runpath):
        break
rt_dirs = []
ln_dirs =[]
for adir in dirs:
    if ("BoardS2_" in adir):
        if ("_RT" in adir):
            rt_dirs.append(runpath + adir + "/")
        elif ("_LN" in adir):
            ln_dirs.append(runpath + adir + "/")
#if (True):
if (False):
    dirs = ln_dirs
#    fp0 = "Channel_Characterization_CMOS_ADC0.csv"
#    fp1 = "Channel_Characterization_CMOS_ADC1.csv"
    fp0 = "Channel_Characterization_BJT_ADC0.csv"
    fp1 = "Channel_Characterization_BJT_ADC1.csv"

    wdnls_16    = []
    winls_16    = []
    enobs_16    = []
    rmss200_16  = []
    rmss900_16  = []
    wdnls_4     = []
    winls_4     = []
    enobs_4     = []
    rmss200_4   = []
    rmss900_4   = []

    for adir in dirs:
        for fp in [fp0, fp1]:
            aaf = adir + fp
            with open(aaf, "r") as f:
                lines = []
                for line in f:
                    lines.append(line)

                lines = lines[len(lines)-10:]

                for al in lines:
                    tmp = al.split(",")
                    tmpf = []
                    if ( "Noise" in tmp[0]):
                        for i in tmp[2:]:
                            tmpf.append(float(i))
                    else:
                        for i in tmp[1:]:
                            tmpf.append(float(i))

                    if ("Worst DNL (16 Ms/s)" in tmp[0]):
                        if tmp[0] not in lines[0]:
                            print (0, aaf)
                            break
                        wdnls_16 = wdnls_16 + tmpf

                    elif ( "Worst INL (16 Ms/s)"     in tmp[0] ): 
                        if tmp[0] not in lines[1]:
                            print (1, aaf)
                            break
                        if max(tmpf) > 10:
                            print (1, aaf)
                            break
                            
                        winls_16   = winls_16   + tmpf 

                    elif ( "ENOB (16 Ms/s)"          in tmp[0] ) : 
                        if tmp[0] not in lines[2]:
                            print (2, aaf)
                            break
                        enobs_16   = enobs_16   + tmpf 

                    elif ( "Noise (200"  in tmp[0] ) and  ("16 Ms/s)" in tmp[1]):      
                        if tmp[0] not in lines[3]:
                            print (3, aaf)
                            break
                        rmss200_16 = rmss200_16 + tmpf 

                    elif ( "Noise (900"  in tmp[0] ) and  ("16 Ms/s)" in tmp[1]):       
                        if tmp[0] not in lines[4]:
                            print (4, aaf)
                            break
                        rmss900_16 = rmss900_16 + tmpf 

                    elif ( "Worst DNL (4 Ms/s)"      in tmp[0] ):      
                        if tmp[0] not in lines[5]:
                            print (5, aaf)
                            break
                        wdnls_4    = wdnls_4    + tmpf 

                    elif ( "Worst INL (4 Ms/s)"      in tmp[0] ) :     
                        if tmp[0] not in lines[6]:
                            print (6, aaf)
                            break
                        winls_4    = winls_4    + tmpf 

                    elif ( "ENOB (4 Ms/s)"           in tmp[0] ): 
                        if tmp[0] not in lines[7]:
                            print (7, aaf)
                            break
                        enobs_4    = enobs_4    + tmpf 

                    elif ( "Noise (200"  in tmp[0] ) and  ("4 Ms/s)" in tmp[1]):      
                        if tmp[0] not in lines[8]:
                            print (8, aaf)
                            break
                        rmss200_4  = rmss200_4  + tmpf 

                    elif ( "Noise (900"  in tmp[0] ) and  ("4 Ms/s)" in tmp[1]):       
                        if tmp[0] not in lines[9]:
                            print (9, aaf)
                            break
                        rmss900_4  = rmss900_4  + tmpf 
   
    print (len(wdnls_16  )) 
    print (len(winls_16  )) 
    print (len(enobs_16  )) 
    print (len(rmss200_16)) 
    print (len(rmss900_16)) 
    print (len(wdnls_4   )) 
    print (len(winls_4   )) 
    print (len(enobs_4   )) 
    print (len(rmss200_4 )) 
    print (len(rmss900_4 )) 


    titles = ["Histogram of Worst DNL (2 MS/s)", "Histogram of Worst INL (2 MS/s)", \
              "Histogram of ENOB (2 MS/s)", "Histogram of Noise at 900mV (2 MS/s)", \
              "Histogram of Noise at 200mV (2 MS/s)", \
              "Histogram of Worst DNL (500 kS/s)", "Histogram of Worst INL (500 kS/s)", \
              "Histogram of ENOB (500 kS/s)", "Histogram of Noise at 900mV (500 kS/s)", \
              "Histogram of Noise at 200mV (500 kS/s)", \
              ]


    xlable = ["Worst DNL / LSB", "Worst INL / LSB",
              "ENOB / bit", "Noise at 900mV / LSB",
               "Noise at 200mV / LSB" ,
               "Worst DNL / LSB", "Worst INL / LSB",
               "ENOB / bit", "Noise at 900mV / LSB",
               "Noise at 200mV / LSB" ,
               ]

    i = 0
    for datai in [ wdnls_16  , winls_16  , enobs_16  , rmss200_16, rmss900_16, \
            wdnls_4   , winls_4   , enobs_4   , rmss200_4 , rmss900_4 ]:
        plt.rcParams.update({'font.size': 16})
        fig = plt.figure(figsize=(8,6))
        m = np.mean(datai)
        s = np.std(datai)
        plt.hist(datai, histtype='bar',  bins=10, label = "Total CHNs = 512 \n Mean = %.2f \n RMS = %.2f"%(m, s), rwidth=0.9)
        plt.ylabel('ADC Channel Counts')
        
        plt.xlabel(xlable[i])
        plt.title(titles[i])
        i = i + 1
        plt.legend()
        plt.grid()
        plt.savefig(runpath+"ADC_per_LN_%d.png"%i)
#       plt.close()

#if (True):
if (False):
    dirs = rt_dirs
#    fp0 = "Channel_Characterization_CMOS_ADC0.csv"
#    fp1 = "Channel_Characterization_CMOS_ADC1.csv"
    fp0 = "Channel_Characterization_BJT_ADC0.csv"
    fp1 = "Channel_Characterization_BJT_ADC1.csv"

    wdnls_16    = []
    winls_16    = []
    enobs_16    = []
    rmss200_16  = []
    rmss900_16  = []
    wdnls_4     = []
    winls_4     = []
    enobs_4     = []
    rmss200_4   = []
    rmss900_4   = []

    for adir in dirs:
        for fp in [fp0, fp1]:
            aaf = adir + fp
            with open(aaf, "r") as f:
                lines = []
                for line in f:
                    lines.append(line)

                lines = lines[len(lines)-10:]

                for al in lines:
                    tmp = al.split(",")
                    tmpf = []
                    if ( "Noise" in tmp[0]):
                        for i in tmp[2:]:
                            tmpf.append(float(i))
                    else:
                        for i in tmp[1:]:
                            tmpf.append(float(i))

                    if ("Worst DNL (16 Ms/s)" in tmp[0]):
                        if tmp[0] not in lines[0]:
                            print (0, aaf)
                            break
                        wdnls_16 = wdnls_16 + tmpf

                    elif ( "Worst INL (16 Ms/s)"     in tmp[0] ): 
                        if tmp[0] not in lines[1]:
                            print (1, aaf)
                            break
#                        if max(tmpf) > 10:
#                            print (1, aaf)
#                            break
                            
                        winls_16   = winls_16   + tmpf 

                    elif ( "ENOB (16 Ms/s)"          in tmp[0] ) : 
                        if tmp[0] not in lines[2]:
                            print (2, aaf)
                            break
                        enobs_16   = enobs_16   + tmpf 
#                        if min(tmpf) < 10.5:
#                            print (1, aaf)
#                            break

                    elif ( "Noise (200"  in tmp[0] ) and  ("16 Ms/s)" in tmp[1]):      
                        if tmp[0] not in lines[3]:
                            print (3, aaf)
                            break
                        rmss200_16 = rmss200_16 + tmpf 

                    elif ( "Noise (900"  in tmp[0] ) and  ("16 Ms/s)" in tmp[1]):       
                        if tmp[0] not in lines[4]:
                            print (4, aaf)
                            break
                        rmss900_16 = rmss900_16 + tmpf 

                    elif ( "Worst DNL (4 Ms/s)"      in tmp[0] ):      
                        if tmp[0] not in lines[5]:
                            print (5, aaf)
                            break
                        wdnls_4    = wdnls_4    + tmpf 

                    elif ( "Worst INL (4 Ms/s)"      in tmp[0] ) :     
                        if tmp[0] not in lines[6]:
                            print (6, aaf)
                            break
                        winls_4    = winls_4    + tmpf 

                    elif ( "ENOB (4 Ms/s)"           in tmp[0] ): 
                        if tmp[0] not in lines[7]:
                            print (7, aaf)
                            break
                        enobs_4    = enobs_4    + tmpf 
#                        if min(tmpf) < 10.5:
#                            print (1, aaf)
#                            break

                    elif ( "Noise (200"  in tmp[0] ) and  ("4 Ms/s)" in tmp[1]):      
                        if tmp[0] not in lines[8]:
                            print (8, aaf)
                            break
                        rmss200_4  = rmss200_4  + tmpf 

                    elif ( "Noise (900"  in tmp[0] ) and  ("4 Ms/s)" in tmp[1]):       
                        if tmp[0] not in lines[9]:
                            print (9, aaf)
                            break
                        rmss900_4  = rmss900_4  + tmpf 
   
    print (len(wdnls_16  )) 
    print (len(winls_16  )) 
    print (len(enobs_16  )) 
    print (len(rmss200_16)) 
    print (len(rmss900_16)) 
    print (len(wdnls_4   )) 
    print (len(winls_4   )) 
    print (len(enobs_4   )) 
    print (len(rmss200_4 )) 
    print (len(rmss900_4 )) 


    titles = ["Histogram of Worst DNL (2 MS/s)", "Histogram of Worst INL (2 MS/s)", \
              "Histogram of ENOB (2 MS/s)", "Histogram of Noise at 900mV (2 MS/s)", \
              "Histogram of Noise at 200mV (2 MS/s)", \
              "Histogram of Worst DNL (500 kS/s)", "Histogram of Worst INL (500 kS/s)", \
              "Histogram of ENOB (500 kS/s)", "Histogram of Noise at 900mV (500 kS/s)", \
              "Histogram of Noise at 200mV (500 kS/s)", \
              ]


    xlable = ["Worst DNL / LSB", "Worst INL / LSB",
              "ENOB / bit", "Noise at 900mV / LSB",
               "Noise at 200mV / LSB" ,
               "Worst DNL / LSB", "Worst INL / LSB",
               "ENOB / bit", "Noise at 900mV / LSB",
               "Noise at 200mV / LSB" ,
               ]

    i = 0
    for datai in [ wdnls_16  , winls_16  , enobs_16  , rmss200_16, rmss900_16, \
            wdnls_4   , winls_4   , enobs_4   , rmss200_4 , rmss900_4 ]:
        plt.rcParams.update({'font.size': 16})
        fig = plt.figure(figsize=(8,6))
        m = np.mean(datai)
        s = np.std(datai)
        plt.hist(datai, histtype='bar',  bins=10, label = "Total CHNs = 512 \nMean = %.2f \n RMS = %.2f"%(m, s), rwidth=0.9)
        plt.ylabel('ADC Channel Counts')
        
        plt.xlabel(xlable[i])
        plt.title(titles[i])
        i = i + 1
        plt.legend()
        plt.grid()
        plt.savefig(runpath+"ADC_per_RT_%d.png"%i)
#       plt.close()

#if (True):
if (False):
    dirs = ln_dirs
    subdir = "ADC_TST_IN/16Mss/"
    #fp = "Channel_Characterization_CMOS.csv"
    fp = "Channel_Characterization_BJT.csv"
    wdnls = []
    winls = []
    enobs = []
    rmss = []

    for adir in dirs:
        aadir = adir + subdir
        aaf = aadir + fp
        with open(aaf, "r") as f:
            for line in f:
                tmp = line.split(",")
                if ("DNL" in tmp[0]):
                    wdnls.append(float(tmp[1]))
                if ("INL" in tmp[0]):
                    winls.append(float(tmp[1]))
                if ("ENOB" in tmp[0]):
                    enobs.append(float(tmp[1]))
                if ("Noise" in tmp[0]):
                    rmss.append(float(tmp[1]))
    
    #titles = ["Histogram of Worst DNL", "Histogram of Worst INL", "Histogram of ENOB", "Histogram of Noise at 900mV"]
    titles = ["Histogram of Worst DNL (ADC core only)", "Histogram of Worst INL (ADC core only)", "Histogram of ENOB (ADC core only)", "Histogram of Noise at 900mV (ADC core only)"]
    xlable = ["Worst DNL / LSB", "Worst INL / LSB", "ENOB / bit", "Noise at 900mV / LSB"]
    i = 0
    for datai in [ wdnls, winls, enobs, rmss]:
        plt.rcParams.update({'font.size': 16})
        fig = plt.figure(figsize=(8,6))
        m = np.mean(datai)
        s = np.std(datai)
        plt.hist(datai, histtype='bar',  bins=10, label = "Total CHNs = 512 \nMean = %.2f \n RMS = %.2f"%(m, s), rwidth=0.9)
        plt.ylabel('ADC Channel Counts')
        
        plt.xlabel(xlable[i])
        plt.title(titles[i])
        i = i + 1
        plt.legend()
        plt.grid()
        plt.savefig(runpath+"LN_ADC_TST_IN_16Mss_%d.png"%i)

#if (True):
if (False):
    dirs = ln_dirs
    subdir = "ADC_TST_IN/4Mss/"
    #fp = "Channel_Characterization_CMOS.csv"
    fp = "Channel_Characterization_BJT.csv"
    wdnls = []
    winls = []
    enobs = []
    rmss = []

    for adir in dirs:
        aadir = adir + subdir
        aaf = aadir + fp
        with open(aaf, "r") as f:
            for line in f:
                tmp = line.split(",")
                if ("DNL" in tmp[0]):
                    wdnls.append(float(tmp[1]))
                if ("INL" in tmp[0]):
                    winls.append(float(tmp[1]))
                if ("ENOB" in tmp[0]):
                    enobs.append(float(tmp[1]))
                if ("Noise" in tmp[0]):
                    rmss.append(float(tmp[1]))
    
    titles = ["Histogram of Worst DNL (ADC core only)", "Histogram of Worst INL (ADC core only)", "Histogram of ENOB (ADC core only)", "Histogram of Noise at 900mV (ADC core only)"]
    xlable = ["Worst DNL / LSB", "Worst INL / LSB", "ENOB / bit", "Noise at 900mV / LSB"]
    i = 0
    for datai in [ wdnls, winls, enobs, rmss]:
        plt.rcParams.update({'font.size': 16})
        fig = plt.figure(figsize=(8,6))
        m = np.mean(datai)
        s = np.std(datai)
        plt.hist(datai, histtype='bar',  bins=10, label = "Total CHNs = 32 \nMean = %.2f \n RMS = %.2f"%(m, s), rwidth=0.9)
        plt.ylabel('ADC Counts')
        
        plt.xlabel(xlable[i])
        plt.title(titles[i])
        i = i + 1
        plt.legend()
        plt.grid()
        plt.savefig(runpath+"LN_ADC_TST_IN_4Mss_%d.png"%i)
#       plt.close()

#if (True):
if (False):
    dirs = rt_dirs
    subdir = "ADC_TST_IN/16Mss/"
    #fp = "Channel_Characterization_CMOS.csv"
    fp = "Channel_Characterization_BJT.csv"
    dirs = rt_dirs
    wdnls = []
    winls = []
    enobs = []
    rmss = []

    for adir in dirs:
        aadir = adir + subdir
        aaf = aadir + fp
        with open(aaf, "r") as f:
            for line in f:
                tmp = line.split(",")
                if ("DNL" in tmp[0]):
                    wdnls.append(float(tmp[1]))
                if ("INL" in tmp[0]):
                    winls.append(float(tmp[1]))
                if ("ENOB" in tmp[0]):
                    enobs.append(float(tmp[1]))
                if ("Noise" in tmp[0]):
                    rmss.append(float(tmp[1]))
    
    titles = ["Histogram of Worst DNL (ADC core only)", "Histogram of Worst INL (ADC core only)", "Histogram of ENOB (ADC core only)", "Histogram of Noise at 900mV (ADC core only)"]
    xlable = ["Worst DNL / LSB", "Worst INL / LSB", "ENOB / bit", "Noise at 900mV / LSB"]
    i = 0
    for datai in [ wdnls, winls, enobs, rmss]:
        plt.rcParams.update({'font.size': 16})
        fig = plt.figure(figsize=(8,6))
        m = np.mean(datai)
        s = np.std(datai)
        plt.hist(datai, histtype='bar',  bins=10, label = "Total CHNs = 32 \nMean = %.2f \n RMS = %.2f"%(m, s), rwidth=0.9)
        plt.ylabel('ADC Counts')
        
        plt.xlabel(xlable[i])
        plt.title(titles[i])
        i = i + 1
        plt.legend()
        plt.grid()
        plt.savefig(runpath+"RT_ADC_TST_IN_16Mss_%d.png"%i)
#       plt.close()

#if (True):
if (False):
    dirs = rt_dirs
    subdir = "ADC_TST_IN/4Mss/"
    #fp = "Channel_Characterization_CMOS.csv"
    fp = "Channel_Characterization_BJT.csv"
    wdnls = []
    winls = []
    enobs = []
    rmss = []

    for adir in dirs:
        aadir = adir + subdir
        aaf = aadir + fp
        with open(aaf, "r") as f:
            for line in f:
                tmp = line.split(",")
                if ("DNL" in tmp[0]):
                    wdnls.append(float(tmp[1]))
                if ("INL" in tmp[0]):
                    winls.append(float(tmp[1]))
                if ("ENOB" in tmp[0]):
                    enobs.append(float(tmp[1]))
                if ("Noise" in tmp[0]):
                    rmss.append(float(tmp[1]))
    
    titles = ["Histogram of Worst DNL (ADC core only)", "Histogram of Worst INL (ADC core only)", "Histogram of ENOB (ADC core only)", "Histogram of Noise at 900mV (ADC core only)"]
    xlable = ["Worst DNL / LSB", "Worst INL / LSB", "ENOB / bit", "Noise at 900mV / LSB"]
    i = 0
    for datai in [ wdnls, winls, enobs, rmss]:
        plt.rcParams.update({'font.size': 16})
        fig = plt.figure(figsize=(8,6))
        m = np.mean(datai)
        s = np.std(datai)
        plt.hist(datai, histtype='bar',  bins=10, label = "Total CHNs = 32 \nMean = %.2f \n RMS = %.2f"%(m, s), rwidth=0.9)
        plt.ylabel('ADC Counts')
        
        plt.xlabel(xlable[i])
        plt.title(titles[i])
        i = i + 1
        plt.legend()
        plt.grid()
        plt.savefig(runpath+"RT_ADC_TST_IN_4Mss_%d.png"%i)
#       plt.close()

if (True):
    dirs = rt_dirs
    subdir = "Power_Check/"
    fp = "Power_Check_CMOS.csv"
    #fp = "Power_Check_BJT.csv"
    
    chip_pcs = []
    for adir in dirs:
        aadir = adir + subdir
        aaf = aadir + fp
        with open(aaf, "r") as f:
            for line in f:
                if ("mW" in line):
                    break
            pcs = line.split(",")
            pc1 = float(pcs[1])
            pc2 = float(pcs[2])
            pc3 = float(pcs[3])
            pc = pc1 + pc2 + pc3
            chip_pcs.append(pc)
    
    plt.rcParams.update({'font.size': 16})
    fig = plt.figure(figsize=(8,6))
    pmean = np.mean(chip_pcs)
    pstd = np.std(chip_pcs)
    plt.hist(chip_pcs, histtype='bar', range=(350, 500), bins=15, label = "Mean = %d \n RMS = %d"%(pmean, pstd), rwidth=0.9)
    plt.title('Power Consumption at RT (Total chips = %d)'%len(chip_pcs))
    plt.ylabel('ADC Channel Counts')
    plt.xlabel('Power Consumption / mW')
    plt.legend()
    plt.grid()
    plt.savefig(runpath+"PC_atRT.png")
    plt.close()

if (True):
    dirs = ln_dirs
    subdir = "Power_Check/"
    fp = "Power_Check_CMOS.csv"
    #fp = "Power_Check_BJT.csv"
    
    chip_pcs = []
    for adir in dirs:
        aadir = adir + subdir
        aaf = aadir + fp
        with open(aaf, "r") as f:
            for line in f:
                if ("mW" in line):
                    break
            pcs = line.split(",")
            pc1 = float(pcs[1])
            pc2 = float(pcs[2])
            pc3 = float(pcs[3])
            pc = pc1 + pc2 + pc3
            chip_pcs.append(pc)
    
    plt.rcParams.update({'font.size': 16})
    fig = plt.figure(figsize=(8,6))
    pmean = np.mean(chip_pcs)
    pstd = np.std(chip_pcs)
    plt.hist(chip_pcs, histtype='bar', range=(350, 500), bins=15, label = "Mean = %d \n RMS = %d"%(pmean, pstd), rwidth=0.9)
    plt.title('Power Consumption at LN (Total chips = %d)'%len(chip_pcs))
    plt.ylabel('ADC Channel Counts')
    plt.xlabel('Power Consumption / mW')
    plt.legend()
    plt.grid()
    plt.savefig(runpath+"PC_atLN.png")
    plt.close()

#def Chn_Plot(asic_cali, chnno = 0, mode16bit=True, fpic = "gain.png"):
#    if (mode16bit):
#        fs = 65535
#        adc_bits = "ADC16bit"
#    else:
#        fs = 4095
#        adc_bits = "ADC12bit"
#        
#    p = Chn_Ana(asic_cali, chnno = chnno, sg=fpic)  
#        
#    fig = plt.figure(figsize=(12,4))
#    #plt.title("Gain Measurment of Channel %d"%chnno)
#    ax1 = fig.add_subplot(131)
#    ax2 = fig.add_subplot(132)
#    ax3 = fig.add_subplot(133)
#    sps = 20
#    for wf in p[4]:
#        max_pos = np.where(wf == np.max(wf))[0][0]
#        ax1.plot(np.arange(sps)*0.5, wf[max_pos-10: max_pos+10])
#        min_pos = np.where(wf == np.min(wf))[0][0]
#        ax2.plot(np.arange(sps)*0.5, wf[max_pos+40: max_pos+60])
#    ax3.scatter(np.array(p[1]), np.array(p[0])/6250, marker = 'o')
#    ax3.scatter(np.array(p[2]), -np.array(p[0])/6250, marker = '*')
#    ax3.scatter ([p[3][0]], [0], marker = "s")
#    x = np.linspace(0, fs)
#    y = (x-p[3][0])*p[5][0]
#    ax3.plot( x, y/6250, color ='m', label= "Gain = %d (e-/LSB)\n INL = %.2f%%"%(p[5][0], p[5][2]*100))
#    ax3.legend()
#
#    ax1.set_title("Waveforms Overlap of CH%d"%chnno)
#    ax2.set_title("Waveforms Overlap of CH%d"%chnno)
#    ax3.set_title("Linear Fit of CH%d"%chnno)
#
#    ax1.set_xlabel("Time / $\mu$s")
#    ax2.set_xlabel("Time / $\mu$s")
#    ax3.set_xlabel("ADC counts / bin")
#
#    ax1.set_ylabel("ADC counts / bin")
#    ax2.set_ylabel("ADC counts / bin")
#    ax3.set_ylabel("Charge / fC")
#    
#
#    ax1.set_xlim((0,10))
#    ax2.set_xlim((0,10))
#    ax3.set_xlim((0,fs))
#   
#    ax1.set_ylim((0,fs))
#    ax2.set_ylim((0,fs))
#    ax3.set_ylim((-100,100))
#
#    ax1.grid(True)
#    ax2.grid(True)
#    ax3.grid(True)
#    plt.tight_layout()
#    plt.savefig( fpic + adc_bits + "_ch%d.png"%chnno)
#    plt.close()
#
#mode16bit = False
#BL = "900mV"
#
#testnos = list(range(1,5)) #+ list(range(11, 19)) + list(range(21, 29)) + list(range(31, 39))
#for testno in testnos:
#    testno_str = "Test%02d"%testno
#    f_dir = "D:/ColdADC/ChipN_gain/"
#    fr_dir = f_dir + "results/"
#    if (os.path.exists(fr_dir)):
#        pass
#    else:
#        try:
#            os.makedirs(fr_dir)
#        except OSError:
#            print ("Error to create folder ")
#            exit()
#    
#    period = 200
#    avg_n = 50
#    fs = file_list(runpath=f_dir)
#    data_fs = []
#    for f in fs:
#        if (f.find(testno_str)>=0) and (f.find(".bin")>0) and (f.find(BL)>0):
#            tp = f[f.find("us")-2 : f.find("us")+2]
#            sg = f[f.find("mVfC")-2 : f.find("mVfC")+4]
#            data_fs.append(f)
#    
#    asic_cali = Asic_Cali(data_fs, mode16bit = mode16bit )
#
#    fpic = fr_dir + data_fs[0][:f.find("asicdac")]
#    chn_gains = []
#    chn_inls = []
#    for i in range(16):
##        Chn_Plot(asic_cali, chnno = i, mode16bit = mode16bit , fpic= fpic )
#        p = Chn_Ana(asic_cali, chnno = i, sg=sg)
#        chn_gains.append((p[5][0]))
#        chn_inls.append(p[5][2])
#
#    if (mode16bit):
#        adc_bits = "ADC16bit"
#    else:
#        adc_bits = "ADC12bit"
#    csv_fn = fr_dir + testno_str + tp + sg + adc_bits + "BL%s"%BL + ".csv"
#
#    with open(csv_fn, "w") as cfp:
#        cfp.write(",".join(str(i) for i in chn_gains) +  "," + "\n")
#        cfp.write(",".join(str(i) for i in chn_inls) +  "," + "\n")
#    
#    print (chn_gains)
#
#
