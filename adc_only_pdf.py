# -*- coding: utf-8 -*-
"""
Created on Tue Sep 17 11:17:18 2019

@author: Edoardo Lopriore
"""
#This file collects every output of the QA/QC procedure into a PDF file, using the pyFPDF library. File structure:
#(1) Summary: date&time, temperature, chip ID, board ID, power consumption and characterization tables (BJT only, can be changed to CMOS).
#(2) Initialization checkout: power consumptions for BJT and CMOS references, sweep plots of reference voltages and currents. 
#(3) Calibration weights: recorded weights (to be changed to hex format).
#(4) Noise study: RMS noise for each channels and comparison.
#(5) Channels characterization: noise, linearity and dynamic studies for every channel, both BJT and CMOS references.
#(6) ADC test input: internal ADC only characterization, both at 4 Ms/s and 16 Ms/s.


import adc_config as config
import numpy as np
import os
import sys
import os.path
import csv
import datetime
now = datetime.datetime.now()

from fpdf import FPDF
from cmd_library import CMD_ACQ
cq = CMD_ACQ()  #command library

env = config.temperature
rawdir = config.subdir
board = config.board_ID
chip = config.chip_ID
samp_freq = config.sampling_frequency

adc_sdc_en = (sys.argv[1] == "SDC")

status_file = open("Status.txt","r")
status = status_file.read()
status_file.close()

err_file = open("Error_Log.txt","r")
err_log = err_file.read()
err_file.close()

pass_file = open("Pass_Log.txt","r")
pass_log = pass_file.read()
pass_file.close()

if (os.path.exists(rawdir)):
    pass
else:
    try:
        os.makedirs(rawdir)
    except OSError:
        print ("Error to create folder ")
        sys.exit()



pdf = FPDF(orientation = 'P', unit = 'mm', format='Letter')
pdf.alias_nb_pages()

##### ADC Test Summary page #####
pdf.add_page()
pdf.set_font('Times', '', 20)
pdf.cell(85)
pdf.cell(30, 5, 'ADC Test Summary', 0, 1, 'C')
pdf.set_font('Times', '', 12)
pdf.ln(10)

pdf.cell(30, 5, 'Date&Time: %s'%now.strftime("%Y-%m-%d %H:%M:%S"), 0, 0)
pdf.cell(100)
pdf.cell(30, 5, 'Temperature: %s'%env, 0, 1)
pdf.cell(30, 5, 'Chip ID: %s'%chip, 0, 0)
pdf.cell(100)
pdf.cell(30, 5, 'Frequency: %s'%samp_freq, 0, 1)
pdf.cell(30, 5, 'Board ID: %s'%board, 0, 0)
pdf.cell(100)
pdf.cell(30, 5, 'Status: %s'%status, 0, 1)
pdf.ln(5)

# Generate Power Check table
pdf.cell(30, 5, 'Power Consumption (CMOS Reference):', 0, 1)
# Colon width is 1/4 of effective page width
epw = pdf.w - 2*pdf.l_margin
col_width = epw/4
pdf.set_font('Times', '', 10) 
with open(rawdir + 'Power_Check/Power_Check_CMOS.csv', "r") as csvfile:
    data = list(csv.reader(csvfile))
print(data)
pdf.ln(5)

# Text height is the same as current font size
th = pdf.font_size 
pdf.ln(0.5*th)
for row in data:
    for datum in row:
        # pyFPDF expects a string, not a number
        pdf.cell(col_width, 2*th, str(datum), border=1)
    pdf.ln(2*th)

pdf.ln(5)

if(status == "PASS"):
    pdf.set_font('Times', '', 12)
    pdf.cell(30, 5, 'Functionality and Characterization Summary:', 0, 1)
    pdf.ln(0.5*th)
    pdf.set_font('Times', '', 10)
    pdf.multi_cell(epw, 5, '%s'%pass_log)
    pdf.ln(2*th)

    col_width = epw/9
    pdf.cell(epw, 10, 'ADC0 (CMOS Reference)', 0, 1, align = 'C')
    pdf.ln(0.5*th)
    with open(rawdir + 'Channel_Characterization_CMOS_ADC0.csv', "r") as csvfile:
        data = list(csv.reader(csvfile))
    print(data)

    for row in data:
        for datum in row:
            pdf.cell(col_width, 2*th, str(datum), border=1)
        pdf.ln(2*th)
    pdf.ln(2*th)

    pdf.cell(epw, 10, 'ADC1 (CMOS Reference)', 0, 1, align = 'C')
    pdf.ln(0.5*th)
    with open(rawdir + 'Channel_Characterization_CMOS_ADC1.csv', "r") as csvfile:
        data = list(csv.reader(csvfile))
    print(data)

    for row in data:
        for datum in row:
            pdf.cell(col_width, 2*th, str(datum), border=1)
        pdf.ln(2*th)


if(status == "FAIL"):
    pdf.set_font('Times', '', 12)
    pdf.cell(30, 5, 'Error Log:', 0, 1)
    pdf.ln(0.5*th)
    pdf.set_font('Times', '', 10)
    pdf.multi_cell(epw, 5, '%s'%err_log)
    


##### ADC Initialization Checkout pages #####
pdf.add_page()
pdf.set_font('Times', '', 20)
pdf.cell(85)
pdf.cell(30, 5, 'Initialization Checkout', 0, 1, 'C')
pdf.set_font('Times', '', 12)

# Generate Power Check table
pdf.cell(30, 5, 'Power Check - BJT:', 0, 1)
# Colon width is 1/4 of effective page width
epw = pdf.w - 2*pdf.l_margin
col_width = epw/4
 
with open(rawdir + 'Power_Check/Power_Check_BJT.csv', "r") as csvfile:
    data = list(csv.reader(csvfile))
print(data)

# Text height is the same as current font size
th = pdf.font_size 
pdf.ln(0.5*th)
for row in data:
    for datum in row:
        # pyFPDF expects a string, not a number
        pdf.cell(col_width, 2*th, str(datum), border=1)
    pdf.ln(2*th)

# Linebreak of 2 lines
pdf.ln(2*th)

pdf.cell(30, 5, 'Power Check - CMOS:', 0, 1)
pdf.ln(0.5*th)
with open(rawdir + 'Power_Check/Power_Check_CMOS.csv', "r") as csvfile:
    data = list(csv.reader(csvfile))
print(data)

for row in data:
    for datum in row:
        pdf.cell(col_width, 2*th, str(datum), border=1)
    pdf.ln(2*th)

pdf.ln(3*th)
pdf.cell(30, 5, 'Reference Check - BJT:', 0, 1)
pdf.image(rawdir + 'Reference_Check/Reference_BJT.png', 18, 126, 176)

pdf.cell(0,89,'',0,1)
pdf.cell(30, 5, 'Reference Check - CMOS:', 0, 1)
pdf.image(rawdir + 'Reference_Check/Reference_CMOS.png', 11, 222, 186)


# Generate Calibration Weights table
pdf.add_page()
pdf.set_font('Times', '', 20)
pdf.cell(85)
pdf.cell(30, 5, 'Calibration Weights (4 Ms/s)', 0, 1, 'C')

table_w = pdf.w/2 - (4/3)*pdf.l_margin
pdf.set_font('Times', '', 12)
pdf.set_y(25)
pdf.cell(table_w, 10, 'BJT:', 0, 1, align = 'C')
col_width = table_w/4
with open(rawdir + 'Weights_Records/Weights_Record_BJT_4M.csv', "r") as csvfile:
    data = list(csv.reader(csvfile))
print(data)

pdf.set_font('Times', '', 10)
th = pdf.font_size 
for row in data:
    for datum in row:
        pdf.cell(col_width, 2*th, str(datum), border=1)
    pdf.ln(2*th)


pdf.set_font('Times', '', 12)
pdf.set_y(25)
pdf.cell(table_w + (2/3)*pdf.l_margin)
pdf.cell(table_w, 10, 'CMOS:', 0, 1, align = 'C')
table_w = pdf.w/2 - (4/3)*pdf.l_margin
col_width = table_w/4
with open(rawdir + 'Weights_Records/Weights_Record_CMOS_4M.csv', "r") as csvfile:
    data = list(csv.reader(csvfile))
print(data)

pdf.set_font('Times', '', 10)
th = pdf.font_size 
for row in data:
    pdf.cell(table_w + (2/3)*pdf.l_margin)
    for datum in row:
        pdf.cell(col_width, 2*th, str(datum), border=1)
    pdf.ln(2*th)    

# Generate Calibration Weights table
pdf.add_page()
pdf.set_font('Times', '', 20)
pdf.cell(85)
pdf.cell(30, 5, 'Calibration Weights (16 Ms/s)', 0, 1, 'C')

table_w = pdf.w/2 - (4/3)*pdf.l_margin
pdf.set_font('Times', '', 12)
pdf.set_y(25)
pdf.cell(table_w, 10, 'BJT:', 0, 1, align = 'C')
col_width = table_w/4
with open(rawdir + 'Weights_Records/Weights_Record_BJT_16M.csv', "r") as csvfile:
    data = list(csv.reader(csvfile))
print(data)

pdf.set_font('Times', '', 10)
th = pdf.font_size 
for row in data:
    for datum in row:
        pdf.cell(col_width, 2*th, str(datum), border=1)
    pdf.ln(2*th)


pdf.set_font('Times', '', 12)
pdf.set_y(25)
pdf.cell(table_w + (2/3)*pdf.l_margin)
pdf.cell(table_w, 10, 'CMOS:', 0, 1, align = 'C')
table_w = pdf.w/2 - (4/3)*pdf.l_margin
col_width = table_w/4
with open(rawdir + 'Weights_Records/Weights_Record_CMOS_16M.csv', "r") as csvfile:
    data = list(csv.reader(csvfile))
print(data)

pdf.set_font('Times', '', 10)
th = pdf.font_size 
for row in data:
    pdf.cell(table_w + (2/3)*pdf.l_margin)
    for datum in row:
        pdf.cell(col_width, 2*th, str(datum), border=1)
    pdf.ln(2*th)    

#Generate Noise Study pages
pdf.add_page()
pdf.set_font('Times', '', 20)
pdf.cell(85)
pdf.cell(30, 5, 'Noise Study', 0, 1, 'C')

pdf.set_font('Times', '', 12)
pdf.cell(30, 20, 'Baseline 200 mV, BJT Reference:', 0, 1)
pdf.image(rawdir + 'DC_Noise/' + 'Hist_NoiseTest_%s_BJT_200.png'%env, 14, 30, 180)
pdf.image(rawdir + 'DC_Noise/' + 'RMS_NoiseTest_%s_BJT_200.png'%env, 30, 180, 160)


pdf.add_page()
pdf.set_font('Times', '', 20)
pdf.cell(85)
pdf.cell(30, 5, 'Noise Study', 0, 1, 'C')

pdf.set_font('Times', '', 12)
pdf.cell(30, 20, 'Baseline 900 mV, BJT Reference:', 0, 1)
pdf.image(rawdir + 'DC_Noise/' + 'Hist_NoiseTest_%s_BJT_900.png'%env, 14, 30, 180)
pdf.image(rawdir + 'DC_Noise/' + 'RMS_NoiseTest_%s_BJT_900.png'%env, 30, 180, 160)


pdf.add_page()
pdf.set_font('Times', '', 20)
pdf.cell(85)
pdf.cell(30, 5, 'Noise Study', 0, 1, 'C')

pdf.set_font('Times', '', 12)
pdf.cell(30, 20, 'Baseline 200 mV, CMOS Reference:', 0, 1)
pdf.image(rawdir + 'DC_Noise/' + 'Hist_NoiseTest_%s_CMOS_200.png'%env, 14, 30, 180)
pdf.image(rawdir + 'DC_Noise/' + 'RMS_NoiseTest_%s_CMOS_200.png'%env, 30, 180, 160)


pdf.add_page()
pdf.set_font('Times', '', 20)
pdf.cell(85)
pdf.cell(30, 5, 'Noise Study', 0, 1, 'C')

pdf.set_font('Times', '', 12)
pdf.cell(30, 20, 'Baseline 900 mV, CMOS Reference:', 0, 1)
pdf.image(rawdir + 'DC_Noise/' + 'Hist_NoiseTest_%s_CMOS_900.png'%env, 14, 30, 180)
pdf.image(rawdir + 'DC_Noise/' + 'RMS_NoiseTest_%s_CMOS_900.png'%env, 30, 180, 160)




#if(env == "RT"):
#    #amp = "1.40 V" 
#    amp = "1.35 V"
#else:
#    amp = "1.35 V"
amp = "1.30 V"

##### Single channel Carachterization (static and dynamic behavior) #####
for chnno in range(16):
    pdf.add_page()
    pdf.set_font('Times', '', 20)
    pdf.cell(85)
    if(adc_sdc_en):
        pdf.cell(30, 3, 'Channel %d (SE + SDC + SHA + ADC)'%chnno, 0, 1, 'C')
    else:
        pdf.cell(30, 3, 'Channel %d (SE + SHA + ADC)'%chnno, 0, 1, 'C')
    
    pdf.set_font('Times', '', 12)
    pdf.cell(30, 5, 'Static Behavior - Noise:', 0, 1)
    pdf.image(rawdir + 'DC_Noise/Single_Channel/' + 'Hist_NoiseTest_%s_BJT_200_ch%d.png'%(env,chnno), 9, 20, 100)
    pdf.image(rawdir + 'DC_Noise/Single_Channel/' + 'Hist_NoiseTest_%s_BJT_900_ch%d.png'%(env,chnno), 9, 65, 100)
    pdf.image(rawdir + 'DC_Noise/Single_Channel/' + 'Hist_NoiseTest_%s_CMOS_200_ch%d.png'%(env,chnno), 107, 20, 100)
    pdf.image(rawdir + 'DC_Noise/Single_Channel/' + 'Hist_NoiseTest_%s_CMOS_900_ch%d.png'%(env,chnno), 107, 65, 100)

    pdf.cell(0,95,'',0,1)

    pdf.cell(30, 5, 'Static Behavior - Linearity (Freq = 14.4043 kHz, Amp = %s, Offs = 0.9 V):'%amp, 0, 1)
    pdf.image(rawdir + 'Linearity/' + 'DNL_INL_%s_BJT_ch%d.png'%(env,chnno), 8, 120, 95)
    pdf.image(rawdir + 'Linearity/' + 'DNL_INL_%s_CMOS_ch%d.png'%(env,chnno), 108,120,95)

    pdf.cell(0,78,'',0,1)
    pdf.cell(30, 5, 'Dynamic Behavior (Freq = 14.4043 kHz, Amp = %s, Offs = 0.9 V):'%amp, 0, 1)
    pdf.image(rawdir + 'Dynamic_Behavior/' + 'ENOB_%s_BJT_ch%d.png'%(env,chnno), 8, 203, 94)
    pdf.image(rawdir + 'Dynamic_Behavior/' + 'ENOB_%s_CMOS_ch%d.png'%(env,chnno), 108,203,94)



##### ADC Test Input Carachterization (16 MHz, nominal operating frequency) #####
pdf.add_page()
pdf.set_font('Times', '', 20)
pdf.cell(85)
pdf.cell(30, 5, 'ADC Test Input (16 Ms/s)', 0, 1, 'C')

pdf.cell(0,5,'',0,1)
pdf.set_font('Times', '', 12)
pdf.cell(30, 5, 'Static Behavior - Noise:', 0, 1)
pdf.image(rawdir + 'ADC_TST_IN/16Mss/' + 'Hist_NoiseTest_%s_BJT_900.png'%(env), 9, 25, 100)
pdf.image(rawdir + 'ADC_TST_IN/16Mss/' + 'Hist_NoiseTest_%s_CMOS_900.png'%(env), 107, 25, 100)

pdf.cell(0,73,'',0,1)
pdf.cell(30, 5, 'Static Behavior - Linearity (Freq = 85.9375 kHz, Amp = %s, Offs = 0.9 V):'%amp, 0, 1)
pdf.image(rawdir + 'ADC_TST_IN/16Mss/' + 'DNL_INL_%s_BJT.png'%(env), 8, 108, 95)
pdf.image(rawdir + 'ADC_TST_IN/16Mss/' + 'DNL_INL_%s_CMOS.png'%(env), 108,108,95)

pdf.cell(0,85,'',0,1)
pdf.cell(30, 5, 'Dynamic Behavior (Freq = 85.9375 kHz, Amp = %s, Offs = 0.9 V):'%amp, 0, 1)
pdf.image(rawdir + 'ADC_TST_IN/16Mss/' + 'ENOB_%s_BJT.png'%(env), 8, 198, 94)
pdf.image(rawdir + 'ADC_TST_IN/16Mss/' + 'ENOB_%s_CMOS.png'%(env), 108,198,94)


##### ADC Test Input Carachterization (4 MHz, nominal operating frequency) #####
pdf.add_page()
pdf.set_font('Times', '', 20)
pdf.cell(85)
pdf.cell(30, 5, 'ADC Test Input (4 Ms/s)', 0, 1, 'C')

pdf.cell(0,5,'',0,1)
pdf.set_font('Times', '', 12)
pdf.cell(30, 5, 'Static Behavior - Noise:', 0, 1)
pdf.image(rawdir + 'ADC_TST_IN/4Mss/' + 'Hist_NoiseTest_%s_BJT_900.png'%(env), 9, 25, 100)
pdf.image(rawdir + 'ADC_TST_IN/4Mss/' + 'Hist_NoiseTest_%s_CMOS_900.png'%(env), 107, 25, 100)

pdf.cell(0,73,'',0,1)
pdf.cell(30, 5, 'Static Behavior - Linearity (Freq = 13671.9 kHz, Amp = %s, Offs = 0.9 V):'%amp, 0, 1)
pdf.image(rawdir + 'ADC_TST_IN/4Mss/' + 'DNL_INL_%s_BJT.png'%(env), 8, 108, 95)
pdf.image(rawdir + 'ADC_TST_IN/4Mss/' + 'DNL_INL_%s_CMOS.png'%(env), 108,108,95)

pdf.cell(0,85,'',0,1)
pdf.cell(30, 5, 'Dynamic Behavior (Freq = 13671.9 kHz, Amp = %s, Offs = 0.9 V):'%amp, 0, 1)
pdf.image(rawdir + 'ADC_TST_IN/4Mss/' + 'ENOB_%s_BJT.png'%(env), 8, 198, 94)
pdf.image(rawdir + 'ADC_TST_IN/4Mss/' + 'ENOB_%s_CMOS.png'%(env), 108,198,94)


filename = rawdir + "Board" + board + "_Chip" + chip + "_"  + env + ".pdf"
pdf.output(filename, 'F')
pdf.close()
