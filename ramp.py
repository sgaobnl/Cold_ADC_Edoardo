# -*- coding: utf-8 -*-
"""
Created on Tue Feb 12 16:52:57 2019

@author: JunbinZhang
"""
import matplotlib.pyplot as plt
#import os.path
import xlrd #read
import xlwt
import numpy as np
import time

from brd_config import Brd_Config
from frame import Frames

#loc = ("D:\python_workspace\DUNE_COLDADC\data\uncali.xlsx")
#To open workbook(loc)
workbook = xlwt.Workbook()
sheet = workbook.add_sheet("cali")

#from Plotfun import Plotfun
brd_config = Brd_Config()

brd_config.adc_output_select("cali_ADCdata")

#plot = Plotfun()
#brd_config.adc_test_input("Normal")
#brd_config.adc_sync_mode("Normal")
#brd_config.adc_sdc_select("off")
#brd_config.adc_db_select("Bypass")
#brd_config.adc_sha_input(1)

#brd_config.word_order_slider(0) #2 ligned up


#result=brd_config.fe_config('ADAC')
#brd_config.fe_pulse_config('ADAC')
#brd_config.fe_spi_config(result)    
#brd_config.fe_pulse_param(9,77,500,0xa00)


#brd_config.adc_test_input("test")
#brd_config.adc_test_input("Normal")





#brd_config.adc_framemarker_shift(0)
#brd_config.adc_hard_reset()
#brd_config.adc_i2c_uart("I2C")
##config BJT
#brd_config.adc_ref_vol_src("BJT")
#brd_config.adc_bias_curr_src("BJT")
#brd_config.adc_ref_monitor(0,0)
#brd_config.adc_ref_powerdown(0,0)
#brd_config.adc_set_ioffset(0,0,0,0)
#brd_config.adc_set_vrefs(0xff,0x40,0x9F,0x7B)
#
##load_ADC pattern
#brd_config.adc_load_pattern_0(0x8a,0x8a)
#brd_config.adc_load_pattern_1(0xA0,0xA0)
#brd_config.adc_test_data_mode("test")
#
#brd_config.adc_test_data_mode("Normal")
#
#brd_config.adc_outputformat("offset")
##brd_config.adc_framemarker_shift(2)
#brd_config.adc_sync_mode("sync")
#brd_config.Acq_start_stop(0)
#brd_config.Acq_start_stop(0)
time.sleep(1)
brd_config.Acq_start_stop(1)
################################################
pktnum = 1000
adcdata = brd_config.get_data(pktnum,0,'Jumbo')
brd_config.Acq_start_stop(0)
frames_inst = Frames(pktnum,adcdata)
frames = frames_inst.packets()
###############################################

def complement(num,complete):
    if complete == "2s":
        if (num <= 32767):
            result = num
        else:
            result = (num%32768 - 32768)
    else:
        result = num
    return result
#print(hex(brd_config.udp.read_reg(0x101)))
#frames[0].info()
#frames[1].info()
#frames[2].info()
#frames[3].info()
#plot.PlotADC('COLDADC',frames[0].ADCdata)
chns=[[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
for i in range(len(frames)):
    for j in range(16): #16 channels
        chns[j].append(complement(frames[i].ADCdata[j],"none"))

#Save data in column
#np.savetxt('uncali.txt',zip(chns[0],chns[1],chns[2],chns[3],chns[4],chns[5],chns[6],chns[7],chns[8],chns[9],chns[10],chns[11],chns[12],chns[13],chns[14],chns[15]),fmt = "%i %i %i %i %i %i %i %i %i %i %i %i %i %i %i %i" )
#np.savetxt('uncali.txt',chns,delimiter=',')   
for i in range(16):
    sheet.write(0,i,'chn'+str(i))
    for j in range(len(frames)):
        sheet.write(j+1,i,chns[i][j])

workbook.save("cali_1.xls")    
    
fig = plt.figure()
ax1 = fig.add_subplot(211)
plt.xlabel('times')
plt.ylabel('ADC counts')
plt.title('ADC0 chn1')
plt.plot(chns[1],'b*-')
#plt.plot(chns[1],'g*')
#plt.plot(chns[2],'rh')
#plt.plot(chns[3],'c+')
#plt.plot(chns[4],'mx')
#plt.plot(chns[5],'yd')
#plt.plot(chns[6],'kD')
#plt.plot(chns[7],'k,')
#plt.legend(('chn0','chn1','chn2','chn3','chn4','chn5','chn6','chn7'))
#plt.text(0,2000, 'chn0=%d,chn1=%d,chn2=%d,chn3=%d,chn4=%d,chn5=%d,chn6=%d,chn7=%d'%(chns[0][0],chns[1][0],chns[2][0],chns[3][0],chns[4][0],chns[5][0],chns[6][0],chns[7][0]),color='k')
ax2 = fig.add_subplot(212)
plt.xlabel('times')
plt.ylabel('ADC counts')
plt.title('ADC1 chn1')
plt.plot(chns[9],'b*-')
plt.show()
