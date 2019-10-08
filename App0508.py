# -*- coding: utf-8 -*-
"""
Created on Wed Feb 27 10:01:00 2019

@author: JunbinZhang
"""
#from PySide2 import QtCore
#import sys
#import pyaudio
from PyQt5.QtCore import (pyqtSlot, pyqtSignal, QThread,QObject, QTimer, QMutex, Qt)
from PyQt5.QtGui import (QFont,QRegExpValidator,QStandardItemModel,QStandardItem)
from PyQt5.QtWidgets import(QApplication, QCheckBox, QComboBox, QDateTimeEdit, QDialogButtonBox, QDial, QErrorMessage, QFileDialog,
                              QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit, QListView, QMainWindow,QMenu, QMessageBox,
                              QProgressBar, QPushButton, QRadioButton, QScrollBar, QSlider,
                              QSpinBox, QStyleFactory, QTableWidget,QTabWidget, QTextEdit, QVBoxLayout, QWidget)

import pyqtgraph as pg  #Note: Do not import pyqtgraph in front of PySide2
from brd_config import Brd_Config
from frame import Frames
from copy import copy
from adc_test_method import ADC_method
import time
import ast
import numpy as np
#-----------------Waveform Example----------------#
class DataFrameThread(QThread):
    interact = pyqtSignal(object)
    sgnFinished = pyqtSignal()
    def __init__(self,total_data,CHUNK=128):
        QThread.__init__(self,parent=None)
        self.CHUNK = CHUNK
        self.MAX_PLOT_SIZE = self.CHUNK*5
        self.brd_config = Brd_Config()
        self.result = [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
        self.mutex = QMutex()        
        self.total_data=total_data        
        self.Acq = True
    @pyqtSlot()
    def stop(self):
        print('switching while loop condition to false')
        self.mutex.lock()
        self.Acq=False
        self.mutex.unlock()         
    def running(self):
        try:
            self.mutex.lock()
            return self.Acq
        finally:
            self.mutex.unlock()        
    def __del__(self):
        self.wait()
    def get_rawdata(self):
        rawdata = self.brd_config.get_data(self.CHUNK,0,'Jumbo') #no packet check
        frames_inst = Frames(self.CHUNK,rawdata)     
        frames = frames_inst.packets()
        #Change it to emit all 16 channels data 
        chns=[[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]] #16-bit
        for i in range(self.CHUNK):
            for j in range(16): #16 channels
                chns[j].append(frames[i].ADCdata[j]) 
        #Calculate FFT
        return chns
       
    def stream(self):
        while self.running():
            self.mutex.lock()
            self.result = self.get_rawdata()
            self.mutex.unlock()
            self.interact.emit(self.result)
            QThread.msleep(2)
        self.sgnFinished.emit()
#--------------code density--------------#
class CodeScanThread(QThread):
    interact = pyqtSignal(object)
    sgnFinished = pyqtSignal()
    def __init__(self,CHUNK=128):
        QThread.__init__(self,parent=None)
        self.CHUNK = CHUNK
        self.MAX_PLOT_SIZE = self.CHUNK*5
        self.brd_config = Brd_Config()
        #self.brd_config.sockets_init()
        self.adc_method = ADC_method()
        self.hist_chns = [[0]*4096,[0]*4096,[0]*4096,[0]*4096,[0]*4096,[0]*4096,[0]*4096,[0]*4096,[0]*4096,[0]*4096,[0]*4096,[0]*4096,[0]*4096,[0]*4096,[0]*4096,[0]*4096]
        #self.hist_chns_raw = [[0]*65536,[0]*65536,[0]*65536,[0]*65536,[0]*65536,[0]*65536,[0]*65536,[0]*65536,[0]*65536,[0]*65536,[0]*65536,[0]*65536,[0]*65536,[0]*65536,[0]*65536,[0]*65536]
        self.mutex = QMutex()           
        self.Acq = True
        self.result = []

    @pyqtSlot()
    def stop(self):
        print('switching while loop condition to false')
        self.mutex.lock()
        self.Acq=False
        self.mutex.unlock()   
        
    def running(self):
        try:
            self.mutex.lock()
            return self.Acq
        finally:
            self.mutex.unlock()    
            
    def __del__(self):
        self.wait()
       # y,x = np.histogram(vals,bins=list(range(0,4096)))
    def get_rawdata(self):
        rawdata = self.brd_config.get_data(self.CHUNK,0,'Jumbo') #no packet check
        frames_inst = Frames(self.CHUNK,rawdata)     
        frames = frames_inst.packets()
        #Change it to emit all 16 channels data 
        chns_truncate = [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]] #truncate it to 12-bit
        for i in range(self.CHUNK):
            for j in range(16): #16 channels
                chns_truncate[j].append(frames[i].ADCdata[j] >> 4) 
        return chns_truncate
    #create an array for histogram 
    def code_indensity(self,chns_truncate):
        for i in range(len(chns_truncate)):
            for j in range(4096):
                self.hist_chns[i][j] = self.hist_chns[i][j] + chns_truncate[i].count(j)
        return self.hist_chns
    def stream(self):
        while self.running():
            self.mutex.lock()
            chns_truncate = self.get_rawdata()
            self.hist_chns = self.code_indensity(chns_truncate)
            #code range, no range
            #self.result= self.adc_method.ramp_dnl_inl(self.hist_chns,0)
            self.result = self.adc_method.data_window_cali(self.hist_chns)
            #self.result= self.adc_method.ramp_dnl_inl_cali(self.hist_chns) #change here
            
            self.mutex.unlock()
            self.interact.emit(self.result)
            QThread.msleep(1)
        self.sgnFinished.emit()        
#--------COTS ADC dac scan-------#        
class DacScanThread(QThread):
    interact = pyqtSignal(object)
    sgnFinished = pyqtSignal()
    def __init__(self,reg,averageN,step):
        QThread.__init__(self,parent=None)
        self.reg = reg
        self.averageN = averageN
        self.step = step
        self.brd_config = Brd_Config()
        self.mutex = QMutex()           
        self.result = [[],[]]      
    def run(self):
        for code in range(0,255,self.step):
            self.mutex.lock()
            self.brd_config.adc_write_reg(self.reg,code)
            QThread.msleep(200)
            amp = self.brd_config.cots_adc_data(self.averageN)
            self.result[0].append(code)
            self.result[1].append(amp)
            self.mutex.unlock()
            self.interact.emit(self.result)
            QThread.msleep(1)     
        self.sgnFinished.emit()       

#------------Noise scan-------------#            
class NoiseScanThread(QThread):
    interact = pyqtSignal(object)
    sgnFinished = pyqtSignal()
    def __init__(self,CHUNK=128):
        QThread.__init__(self,parent=None)
        self.CHUNK = CHUNK
        self.MAX_PLOT_SIZE = self.CHUNK*5
        self.brd_config = Brd_Config()
        #self.brd_config.sockets_init()
        self.adc_method = ADC_method()
        #self.hist_chns = [[0]*4096,[0]*4096,[0]*4096,[0]*4096,[0]*4096,[0]*4096,[0]*4096,[0]*4096,[0]*4096,[0]*4096,[0]*4096,[0]*4096,[0]*4096,[0]*4096,[0]*4096,[0]*4096]
        #self.hist_chns = [[0]*65536,[0]*65536,[0]*65536,[0]*65536,[0]*65536,[0]*65536,[0]*65536,[0]*65536,[0]*65536,[0]*65536,[0]*65536,[0]*65536,[0]*65536,[0]*65536,[0]*65536,[0]*65536]
        self.hist_chns = [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]] #16 channels
        self.mutex = QMutex()           
        self.Acq = True
        self.result = []

    @pyqtSlot()
    def stop(self):
        print('switching while loop condition to false')
        self.mutex.lock()
        self.Acq=False
        self.mutex.unlock()   
        
    def running(self):
        try:
            self.mutex.lock()
            return self.Acq
        finally:
            self.mutex.unlock()    
            
    def __del__(self):
        self.wait()
       # y,x = np.histogram(vals,bins=list(range(0,4096)))
    def get_rawdata(self):
        rawdata = self.brd_config.get_data(self.CHUNK,0,'Jumbo') #no packet check
        frames_inst = Frames(self.CHUNK,rawdata)     
        frames = frames_inst.packets()
        #Change it to emit all 16 channels data 
        chns_truncate = [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]] #truncate it to 12-bit
        for i in range(self.CHUNK):
            for j in range(16): #16 channels
                chns_truncate[j].append(frames[i].ADCdata[j]) 
        return chns_truncate
    #create an array for histogram 
    def peak_to_peak(self, chns_truncate):
        
        for chn in range(len(chns_truncate)):
            vpp = max(chns_truncate[chn])-min(chns_truncate[chn])
            self.hist_chns[chn].append(vpp)
        return self.hist_chns
            
            
#    def code_indensity(self,chns_truncate):
#        for i in range(len(chns_truncate)):
#            for j in range(65536):
#                self.hist_chns[i][j] = self.hist_chns[i][j] + chns_truncate[i].count(j)
#        return self.hist_chns
    
    def stream(self):
        while self.running():
            self.mutex.lock()
            chns_truncate = self.get_rawdata()
            self.result = self.peak_to_peak(chns_truncate)
            #code range, no range
            #self.result = self.adc_method.noise_window(self.hist_chns)           
            self.mutex.unlock()
            self.interact.emit(self.result)
            QThread.msleep(1)
        self.sgnFinished.emit()        
#---------------MainWindow---------------#    
class MainWindow(QWidget):
        
    def ChannelGroupBox(self):
        self.MMradioButton = QRadioButton("Multi-mode")
        self.SMradioButton = QRadioButton("Single-mode")
        self.SMradioButton.setChecked(True)
        
        self.ChngroupBox = QGroupBox("Channel Selection")
        self.ChngroupBox.setCheckable(True)
        self.ChngroupBox.setChecked(True)
        self.Chnlist = QListView()
        self.listmodel = QStandardItemModel(self.Chnlist)
        #self.listmodel.setColumnCount(8)
        chns = ['all','ch0','ch1','ch2','ch3','ch4','ch5','ch6','ch7','ch8','ch9','ch10','ch11','ch12','ch13','ch14','ch15']
        for chn in chns:
            item = QStandardItem(chn)
            #add a checkbox to it
            item.setCheckable(True)
            #item.setFlags(ItemIsUserCheckable | Qt.ItemIsEnabled)
            #item.setData(QVariant(Qt.Checked), Qt.CheckStateRole)
            #Add the item to the model
            self.listmodel.appendRow(item)
        self.Chnlist.setModel(self.listmodel)
        #--------------Slider--------------#
        self.ChnSlider = QSlider(Qt.Vertical)
        self.ChnSlider.setMaximum(0)
        self.ChnSlider.setMaximum(15)
        self.ChnSlider.setTickPosition(QSlider.TicksRight)
        self.ChnSlider.setTickInterval(1)
        self.ChnSlider.setValue(0)
        self.ChnSlider.valueChanged.connect(self.ChannelSelect)
        #-----------------------------------------------------#
        layout = QGridLayout()
        layout.addWidget(self.Chnlist,0,0,16,1)
        layout.addWidget(self.ChnSlider,0,1,16,1)
        for i in range(16):
            layout.addWidget(QLabel("chn"+str(15-i)),i,2,1,1)
        self.ChngroupBox.setLayout(layout)   
        
    def MessageGroupBox(self):
        self.MsggroupBox = QGroupBox("Message")
        self.msg = QTextEdit()
        self.msgClearbtn = QPushButton("Clear")
        self.msgSavelogbtn = QPushButton("Save")
        layout1 = QHBoxLayout()
        layout1.addWidget(self.msgClearbtn)
        layout1.addWidget(self.msgSavelogbtn)
        layout = QGridLayout()
        layout.addWidget(self.msg,0,0,8,1)
        layout.addLayout(layout1,9,0,1,1)
        self.MsggroupBox.setLayout(layout)        
        
    def FPGActrlGroupBox(self):
        self.FPGAgroupBox = QGroupBox("FPGA REG control")
        label1 = QLabel("Reg")
        label2 = QLabel("Val")
        self.FPGARegAddrlineEdit = QLineEdit("hex only")
#        rx1 = QRegExp("^[0-9A-F]{3}$")
#        validator1 = QRegExpValidator(rx1)
#        self.FPGARegAddrlineEdit.setValidator(validator1)
        self.FPGARegVallineEdit = QLineEdit("hex only")
        #rx2 = QRegExp("^[0-9A-F]{3}$")
        #validator2 = QRegExpValidator(rx2)
        #self.FPGARegAddrlineEdit.setValidator(validator1)       
        self.FPGAwriteRegButton = QPushButton("&write")
        #bind to the Action
        self.FPGAwriteRegButton.clicked.connect(self.FPGAwritebtn_clicked)
        
        self.FPGAreadRegButton = QPushButton("&read")
        #bind to the Action
        self.FPGAreadRegButton.clicked.connect(self.FPGAreadbtn_clicked)
        #Create a toggle pushbutton
        self.ModeComboBox = QComboBox()
        self.ModeComboBox.addItem("Normal")
        self.ModeComboBox.addItem("F_Suffix")
        self.ModeComboBox.addItem("F_ChnID")
        self.ModeComboBox.activated[str].connect(self.Change_mode)
        
        label3 = QLabel("Suffix")
        self.SuffixlineEdit = QLineEdit("0xA0F0")
        
        
        self.AcqStartButton = QPushButton("AcqStart")
        self.AcqStartButton.clicked.connect(self.AcqStartbtn_clicked)
        self.AcqStopButton = QPushButton("AcqStop")
        self.AcqStopButton.setDisabled(True)
        self.AcqStopButton.clicked.connect(self.AcqStopbtn_clicked)
        
        
     
        #self.AcqStartButton.setCheckable(True)
        
        #Layout
        layout1 = QHBoxLayout()
        layout1.addWidget(label1)
        layout1.addWidget(self.FPGARegAddrlineEdit)
        layout1.addWidget(label2)
        layout1.addWidget(self.FPGARegVallineEdit)
        
        layout2 = QHBoxLayout()
        layout2.addWidget(self.FPGAwriteRegButton)
        layout2.addWidget(self.FPGAreadRegButton)
        
        layout3 = QHBoxLayout()
        layout3.addWidget(self.ModeComboBox)
        layout3.addWidget(label3)
        layout3.addWidget(self.SuffixlineEdit)
        
        layout4 = QHBoxLayout()
        layout4.addWidget(self.AcqStartButton)
        layout4.addWidget(self.AcqStopButton) 
        
#        layout5 = QHBoxLayout()
#        layout5.addWidget(self.btn_CodeScanStart)
#        layout5.addWidget(self.btn_CodeScanStop)            
        #layout3.addWidget(self.AcqStartButton)     
        layout = QVBoxLayout()
        layout.addLayout(layout1)
        layout.addLayout(layout2)
        layout.addLayout(layout3)
        layout.addLayout(layout4)
        #layout.addLayout(layout5)
        #Set Layout
        self.FPGAgroupBox.setLayout(layout)   
        
    def ViewControl(self):
        self.ViewControlgroupBox = QGroupBox("Functional test") 
        lbl_word_order = QLabel("Word order")
        self.sp_word_order = QSpinBox()
        self.sp_word_order.setRange(0,7)
        self.sp_word_order.setValue(0)
        self.sp_word_order.setSingleStep(1)
        self.sp_word_order.valueChanged.connect(self.fun_wordorder)
        
        lbl_dnl_inl = QLabel("DNL/INL")
        self.btn_CodeScanStart = QPushButton("CodeScanStart")
        self.btn_CodeScanStart.clicked.connect(self.btn_CodeScanStart_clicked)
        self.btn_CodeScanStop = QPushButton("CodeScanStop")
        self.btn_CodeScanStop.setDisabled(True)
        self.btn_CodeScanStop.clicked.connect(self.btn_CodeScanStop_clicked)          
        
        lbl_noise_statistics = QLabel("Noise/run")
        self.btn_NoiseRunStart = QPushButton("Run")
        self.btn_NoiseRunStart.clicked.connect(self.btn_NoiseRunStart_clicked)
        
        self.btn_NoiseRunStop  = QPushButton("Stop")
        self.btn_NoiseRunStop.clicked.connect(self.btn_NoiseRunStop_clicked)
                 
        
        layout = QGridLayout()
        layout.addWidget(lbl_word_order,0,0)
        layout.addWidget(self.sp_word_order,0,1) 
        
        layout.addWidget(lbl_dnl_inl,1,0)
        layout.addWidget(self.btn_CodeScanStart,1,1)
        layout.addWidget(self.btn_CodeScanStop,1,2)
        
        layout.addWidget(lbl_noise_statistics,2,0)
        layout.addWidget(self.btn_NoiseRunStart,2,1)
        layout.addWidget(self.btn_NoiseRunStop,2,2)
        
        self.ViewControlgroupBox.setLayout(layout)   
        
    def COTS_ADC(self):
        self.gbox_cots_adc = QGroupBox("COTS ADC")
        lbl_BJT_Mon = QLabel("BJT_mon")
        self.cbox_BJT_mon = QComboBox()
        self.cbox_BJT_mon.addItem("None")
        self.cbox_BJT_mon.addItem("VREF_ext") #reg20 Bit0
        self.cbox_BJT_mon.addItem("VREFN")    #reg20 Bit1
        self.cbox_BJT_mon.addItem("VREFP")    #reg20 Bit2
        self.cbox_BJT_mon.addItem("VCMI")     #reg20 Bit3
        self.cbox_BJT_mon.addItem("VCMO")     #reg20 Bit4
        self.cbox_BJT_mon.addItem("VBGR_1.2V")#reg21 Bit7
        self.cbox_BJT_mon.addItem("Vdac0_5k") #reg20 Bit5
        self.cbox_BJT_mon.addItem("Vdac1_5k") #reg20 Bit6
        self.cbox_BJT_mon.addItem("ibuff0_5k")#reg20 Bit7
        self.cbox_BJT_mon.addItem("ibuff1_5k")    #reg21 Bit0
        self.cbox_BJT_mon.addItem("Isink_adc1_5k")#reg21 Bit1
        self.cbox_BJT_mon.addItem("Isink_adc0_5k")#reg21 Bit2
        self.cbox_BJT_mon.addItem("Isink_sha1_5k")#reg21 Bit3
        self.cbox_BJT_mon.addItem("Isink_sha0_5k")#reg21 Bit4
        self.cbox_BJT_mon.addItem("Isink_refbuf0_5k")#reg21 Bit5
        self.cbox_BJT_mon.addItem("Isink_refbuf1_5k")#reg21 Bit6
        self.cbox_BJT_mon.activated[str].connect(self.fun_BJT_mon) #
        
        lbl_mux_mon = QLabel("MUX")
        self.cbox_mux_mon = QComboBox()
        self.cbox_mux_mon.addItem("AUX_ISINK")  #000
        self.cbox_mux_mon.addItem("AUX_VOLTAGE")#001
        self.cbox_mux_mon.addItem("AUX_ISOURCE")#010
        self.cbox_mux_mon.addItem("VOLTAGE_MON")#011
        self.cbox_mux_mon.addItem("CURRENT_MON")#100
        self.cbox_mux_mon.activated[str].connect(self.fun_MUX_mon)  #
        
        lbl_average = QLabel("Avr points")
        self.ledit_cots_avr_points = QLineEdit("1") 
        lbl_value = QLabel("Val(V)")
        self.ledit_cotsadc_result = QLineEdit("") 
        self.btn_read_cots_adc = QPushButton("Read")
        self.btn_read_cots_adc.clicked.connect(self.btn_read_cots_adc_clicked)   
        
        lbl_steps = QLabel("Steps")# change code here
        self.sp_dac_steps = QSpinBox()
        self.sp_dac_steps.setRange(1,128)
        self.sp_dac_steps.setValue(0)
        self.sp_dac_steps.setSingleStep(5)
        self.sp_dac_steps.setSuffix(" points")
        self.sp_dac_steps.valueChanged.connect(self.fun_dac_steps)
        
        
        self.btn_dacscan_start = QPushButton("DAC scan")
        self.btn_dacscan_start.clicked.connect(self.btn_dacscan_start_clicked)
        
        self.btn_dacscan_stop = QPushButton("stop")
        self.btn_dacscan_stop.clicked.connect(self.btn_dacscan_stop_clicked)
        
        layout = QGridLayout() 
        layout.addWidget(lbl_BJT_Mon,0,0)
        layout.addWidget(self.cbox_BJT_mon,0,1)
        layout.addWidget(lbl_mux_mon,0,2)
        layout.addWidget(self.cbox_mux_mon,0,3)
        
        
        layout.addWidget(lbl_average,1,0)
        layout.addWidget(self.ledit_cots_avr_points,1,1)
        
        layout.addWidget(lbl_value,1,2)
        layout.addWidget(self.ledit_cotsadc_result,1,3)
        layout.addWidget(self.btn_read_cots_adc,1,4)
        
        layout.addWidget(lbl_steps,2,0)
        layout.addWidget(self.sp_dac_steps,2,1)
        layout.addWidget(self.btn_dacscan_start,2,2)
        layout.addWidget(self.btn_dacscan_stop,2,3)
        self.gbox_cots_adc.setLayout(layout)
    #---------------------------a part of show----------------------------#    
    def ControlTabWidget(self):
        self.ControlTab = QTabWidget()
        #-------------------------tab1----------------------------#
        tab1 = QWidget()
        #---------------first line label-----------#
        gbox_SpiCtrl = QGroupBox("spi control")
        lbl_fe_chn      = QLabel("CHN")
        lbl_fe_input= QLabel("Input")
        lbl_fe_baseline = QLabel("Baseline")
        lbl_fe_gain = QLabel("Gain")
        lbl_fe_peaktime = QLabel("Peaktime")
        lbl_fe_mon = QLabel("Mon")
        lbl_fe_buffer = QLabel("Buffer")
        
        #--------------channels-------------------#
        lbl_fe_chns = [QLabel("chn0"),QLabel("chn1"),QLabel("chn2"),QLabel("chn3"),QLabel("chn4"),QLabel("chn5"),QLabel("chn6"),QLabel("chn7"),
                       QLabel("chn8"),QLabel("chn9"),QLabel("chn10"),QLabel("chn11"),QLabel("chn12"),QLabel("chn13"),QLabel("chn14"),QLabel("chn15")]
        self.cbox_fe_inputs=[QComboBox(),QComboBox(),QComboBox(),QComboBox(),QComboBox(),QComboBox(),QComboBox(),QComboBox(),
                             QComboBox(),QComboBox(),QComboBox(),QComboBox(),QComboBox(),QComboBox(),QComboBox(),QComboBox()]
        for fe_inputs in self.cbox_fe_inputs:
            fe_inputs.addItem("Direct_Input")
            fe_inputs.addItem("Test_Input")
            
        self.cbox_fe_baselines =[QComboBox(),QComboBox(),QComboBox(),QComboBox(),QComboBox(),QComboBox(),QComboBox(),QComboBox(),
                                 QComboBox(),QComboBox(),QComboBox(),QComboBox(),QComboBox(),QComboBox(),QComboBox(),QComboBox()]    
        for fe_baseline in self.cbox_fe_baselines:
            fe_baseline.addItem("900mV")
            fe_baseline.addItem("200mV") 
        
        self.cbox_fe_gains = [QComboBox(),QComboBox(),QComboBox(),QComboBox(),QComboBox(),QComboBox(),QComboBox(),QComboBox(),
                              QComboBox(),QComboBox(),QComboBox(),QComboBox(),QComboBox(),QComboBox(),QComboBox(),QComboBox()]
        for fe_gain in self.cbox_fe_gains:
            fe_gain.addItem("14mV/fC")
            fe_gain.addItem("4.7mV/fC")
            fe_gain.addItem("7.8mV/fC")
            fe_gain.addItem("25mV/fC")
            
        self.cbox_fe_peaktimes = [QComboBox(),QComboBox(),QComboBox(),QComboBox(),QComboBox(),QComboBox(),QComboBox(),QComboBox(),
                                  QComboBox(),QComboBox(),QComboBox(),QComboBox(),QComboBox(),QComboBox(),QComboBox(),QComboBox()] 
        for fe_peaktime in self.cbox_fe_peaktimes:
            fe_peaktime.addItem("2us")
            fe_peaktime.addItem("0.5us")
            fe_peaktime.addItem("1us")
            fe_peaktime.addItem("3us")   
            
        self.cbox_fe_mons = [QComboBox(),QComboBox(),QComboBox(),QComboBox(),QComboBox(),QComboBox(),QComboBox(),QComboBox(),
                             QComboBox(),QComboBox(),QComboBox(),QComboBox(),QComboBox(),QComboBox(),QComboBox(),QComboBox()]
        for fe_mon in self.cbox_fe_mons:
            fe_mon.addItem("off")
            fe_mon.addItem("on")
            
        self.cbox_fe_buffers = [QComboBox(),QComboBox(),QComboBox(),QComboBox(),QComboBox(),QComboBox(),QComboBox(),QComboBox(),
                                QComboBox(),QComboBox(),QComboBox(),QComboBox(),QComboBox(),QComboBox(),QComboBox(),QComboBox()] 
        for fe_buffer in self.cbox_fe_buffers:
            fe_buffer.addItem("off")
            fe_buffer.addItem("on")  

        lbl_fe_chn_all = QLabel("All chn")
        self.cbox_fe_input_all = QComboBox()
        self.cbox_fe_input_all.addItem("Direct_Input")
        self.cbox_fe_input_all.addItem("Test_Input")
        self.cbox_fe_input_all.setStyleSheet("QComboBox {background-color:green;}")
        self.cbox_fe_input_all.activated[str].connect(self.fun_fe_input_all)  
        
        self.cbox_fe_baseline_all = QComboBox()
        self.cbox_fe_baseline_all.addItem("900mV")
        self.cbox_fe_baseline_all.addItem("200mV")
        self.cbox_fe_baseline_all.setStyleSheet("QComboBox {background-color:green;}")
        self.cbox_fe_baseline_all.activated[str].connect(self.fun_fe_baseline_all)  
        
        self.cbox_fe_gain_all = QComboBox()
        self.cbox_fe_gain_all.addItem("14mV/fC")
        self.cbox_fe_gain_all.addItem("4.7mV/fC")
        self.cbox_fe_gain_all.addItem("7.8mV/fC")
        self.cbox_fe_gain_all.addItem("25mV/fC")
        self.cbox_fe_gain_all.setStyleSheet("QComboBox {background-color:green;}")
        self.cbox_fe_gain_all.activated[str].connect(self.fun_fe_gain_all)  
        
        self.cbox_fe_peaktime_all = QComboBox()
        self.cbox_fe_peaktime_all.addItem("2us")
        self.cbox_fe_peaktime_all.addItem("0.5us")
        self.cbox_fe_peaktime_all.addItem("1us")
        self.cbox_fe_peaktime_all.addItem("3us")   
        self.cbox_fe_peaktime_all.setStyleSheet("QComboBox {background-color:green;}")
        self.cbox_fe_peaktime_all.activated[str].connect(self.fun_fe_peaktime_all)  
             
        self.cbox_fe_mon_all = QComboBox()
        self.cbox_fe_mon_all.addItem("off")
        self.cbox_fe_mon_all.addItem("on")
        self.cbox_fe_mon_all.setStyleSheet("QComboBox {background-color:green;}")
        self.cbox_fe_mon_all.activated[str].connect(self.fun_fe_mon_all)             
        
        self.cbox_fe_buffer_all = QComboBox()
        self.cbox_fe_buffer_all.addItem("off")
        self.cbox_fe_buffer_all.addItem("on") 
        self.cbox_fe_buffer_all.setStyleSheet("QComboBox {background-color:green;}")
        self.cbox_fe_buffer_all.activated[str].connect(self.fun_fe_buffer_all) 
        
        lbl_fe_glbl      = QLabel("GLBL")
        lbl_fe_pulse_src = QLabel("Pulse")
        self.cbox_fe_pulse_src = QComboBox()
        self.cbox_fe_pulse_src.addItem("Disable")
        self.cbox_fe_pulse_src.addItem("External")
        self.cbox_fe_pulse_src.addItem("Internal")
        self.cbox_fe_pulse_src.addItem("ExtM")
        self.cbox_fe_pulse_src.activated[str].connect(self.fun_fe_pulse_src)        
        
        lbl_fe_coupling = QLabel("Coupling")
        self.cbox_fe_coupling = QComboBox()
        self.cbox_fe_coupling.addItem("DC")
        self.cbox_fe_coupling.addItem("AC")
        self.cbox_fe_coupling.activated[str].connect(self.fun_fe_coupling)        

        lbl_fe_leakage = QLabel("Leakage")
        self.cbox_fe_leakage = QComboBox()
        self.cbox_fe_leakage.addItem("500pA")
        self.cbox_fe_leakage.addItem("100pA")
        self.cbox_fe_leakage.addItem("5nA")
        self.cbox_fe_leakage.addItem("1nA")
        self.cbox_fe_leakage.activated[str].connect(self.fun_fe_leakage)  
        
        lbl_fe_mon_type = QLabel("Montype")
        self.cbox_fe_mon_type = QComboBox()
        self.cbox_fe_mon_type.addItem("Analog")
        self.cbox_fe_mon_type.addItem("Temp")
        self.cbox_fe_mon_type.addItem("Bandgap")
        self.cbox_fe_mon_type.activated[str].connect(self.fun_fe_mon_type)
        
        lbl_asic_dac = QLabel("ADAC")
        self.sp_asic_dac = QSpinBox()
        self.sp_asic_dac.setRange(0,31)
        self.sp_asic_dac.setValue(5)
        self.sp_asic_dac.setPrefix("0x")
        self.sp_asic_dac.setSingleStep(1)
        self.sp_asic_dac.setDisplayIntegerBase(16)
        self.sp_asic_dac.valueChanged.connect(self.fun_fe_asicdac)                 
        
        #----------------------channel 0--------------------------#
#        lbl_fe_chn_0 = QLabel("chn 0")
#        self.cbox_fe_input_0    = QComboBox()
#        self.cbox_fe_input_0.addItem("Direct_Input")
#        self.cbox_fe_input_0.addItem("Test_Input")
#        self.cbox_fe_input_0.activated[str].connect(self.fun_fe_input_0)       
#        self.cbox_fe_baseline_0 = QComboBox()
#        self.cbox_fe_baseline_0.addItem("900mV")
#        self.cbox_fe_baseline_0.addItem("200mV")
#        self.cbox_fe_baseline_0.activated[str].connect(self.fun_fe_baseline_0)        
#        self.cbox_fe_gain_0     = QComboBox()
#        self.cbox_fe_gain_0.addItem("14mV/fC")
#        self.cbox_fe_gain_0.addItem("4.7mV/fC")
#        self.cbox_fe_gain_0.addItem("7.8mV/fC")
#        self.cbox_fe_gain_0.addItem("25mV/fC")
#        self.cbox_fe_gain_0.activated[str].connect(self.fun_fe_gain_0)        
#        self.cbox_fe_peaktime_0 = QComboBox()
#        self.cbox_fe_peaktime_0.addItem("2us")
#        self.cbox_fe_peaktime_0.addItem("0.5us")
#        self.cbox_fe_peaktime_0.addItem("1us")
#        self.cbox_fe_peaktime_0.addItem("3us")
#        self.cbox_fe_peaktime_0.activated[str].connect(self.fun_fe_peaktime_0)        
#        self.cbox_fe_mon_0      = QComboBox()
#        self.cbox_fe_mon_0.addItem("off")
#        self.cbox_fe_mon_0.addItem("on")
#        self.cbox_fe_mon_0.activated[str].connect(self.fun_fe_mon_0)       
#        self.cbox_fe_buffer_0   = QComboBox()
#        self.cbox_fe_buffer_0.addItem("off")
#        self.cbox_fe_buffer_0.addItem("on")        
#        self.cbox_fe_buffer_0.activated[str].connect(self.fun_fe_buffer_0)
        #--------------------channel 2---------------------------#  
#        lbl_fedacmode = QLabel("DAC_MODE")
#        self.cbox_fedacmode = QComboBox()
#        self.cbox_fedacmode.addItem("RMS")
#        self.cbox_fedacmode.addItem("FDAC")
#        self.cbox_fedacmode.addItem("ADAC")
#        self.cbox_fedacmode.activated[str].connect(self.fun_SetFedacMode)
        
        #lbl_fe_baseline = QLabel("Baseline")
#        self.cbox_fe_baseline = QComboBox()
#        self.cbox_fe_baseline.addItem("900mV")
#        self.cbox_fe_baseline.addItem("200mV")
#        self.cbox_fe_baseline.activated[str].connect(self.fun_fe_baseline)
#        
#        #lbl_fe_gain = QLabel("Gain")
#        self.cbox_fe_gain = QComboBox()
#        self.cbox_fe_gain.addItem("14mV/fC")
#        self.cbox_fe_gain.addItem("4.7mV/fC")
#        self.cbox_fe_gain.addItem("7.8mV/fC")
#        self.cbox_fe_gain.addItem("25mV/fC")
#        self.cbox_fe_gain.activated[str].connect(self.fun_fe_gain)
#        
#        #lbl_fe_peaktime = QLabel("Peaktime")
#        self.cbox_fe_peaktime = QComboBox()
#        self.cbox_fe_peaktime.addItem("2us")
#        self.cbox_fe_peaktime.addItem("0.5us")
#        self.cbox_fe_peaktime.addItem("1us")
#        self.cbox_fe_peaktime.addItem("3us")
#        self.cbox_fe_peaktime.activated[str].connect(self.fun_fe_peaktime)
#        
#        #lbl_fe_mon = QLabel("Mon")
#        self.cbox_fe_mon = QComboBox()
#        self.cbox_fe_mon.addItem("off")
#        self.cbox_fe_mon.addItem("on")
#        self.cbox_fe_mon.activated[str].connect(self.fun_fe_mon)
#        
#        #lbl_fe_buffer = QLabel("Buffer")
#        self.cbox_fe_buffer = QComboBox()
#        self.cbox_fe_buffer.addItem("off")
#        self.cbox_fe_buffer.addItem("on")
#        self.cbox_fe_buffer.activated[str].connect(self.fun_fe_buffer)
        
#        lbl_fe_coupling = QLabel("Coupling")
#        self.cbox_fe_coupling = QComboBox()
#        self.cbox_fe_coupling.addItem("DC")
#        self.cbox_fe_coupling.addItem("AC")
#        self.cbox_fe_coupling.activated[str].connect(self.fun_fe_coupling)        
#
#        lbl_fe_leakage = QLabel("Leakage")
#        self.cbox_fe_leakage = QComboBox()
#        self.cbox_fe_leakage.addItem("500pA")
#        self.cbox_fe_leakage.addItem("100pA")
#        self.cbox_fe_leakage.addItem("5nA")
#        self.cbox_fe_leakage.addItem("1nA")
#        self.cbox_fe_leakage.activated[str].connect(self.fun_fe_leakage)  
#        
#        lbl_fe_mon_type = QLabel("Montype")
#        self.cbox_fe_mon_type = QComboBox()
#        self.cbox_fe_mon_type.addItem("Analog")
#        self.cbox_fe_mon_type.addItem("Temp")
#        self.cbox_fe_mon_type.addItem("Bandgap")
#        self.cbox_fe_mon_type.activated[str].connect(self.fun_fe_mon_type)
#        
#        lbl_asic_dac = QLabel("ADAC")
#        self.sp_asic_dac = QSpinBox()
#        self.sp_asic_dac.setRange(0,31)
#        self.sp_asic_dac.setValue(5)
#        self.sp_asic_dac.setPrefix("0x")
#        self.sp_asic_dac.setSingleStep(1)
#        self.sp_asic_dac.setDisplayIntegerBase(16)
#        self.sp_asic_dac.valueChanged.connect(self.fun_fe_asicdac)

        self.btn_fe_spi_config = QPushButton("spi write")
        self.btn_fe_spi_config.clicked.connect(self.fun_FeSpiConfig_clicked) 
        
        SpiCtrl_layout = QGridLayout()
        SpiCtrl_layout.addWidget(lbl_fe_chn,0,0)
        SpiCtrl_layout.addWidget(lbl_fe_input,0,1)
        SpiCtrl_layout.addWidget(lbl_fe_baseline,0,2)
        SpiCtrl_layout.addWidget(lbl_fe_gain,0,3)
        SpiCtrl_layout.addWidget(lbl_fe_peaktime,0,4)
        SpiCtrl_layout.addWidget(lbl_fe_mon,0,5)
        SpiCtrl_layout.addWidget(lbl_fe_buffer,0,6)
        
        for chn in range(16):
            SpiCtrl_layout.addWidget(lbl_fe_chns[chn],chn+1,0)
            SpiCtrl_layout.addWidget(self.cbox_fe_inputs[chn],chn+1,1)
            SpiCtrl_layout.addWidget(self.cbox_fe_baselines[chn],chn+1,2)
            SpiCtrl_layout.addWidget(self.cbox_fe_gains[chn],chn+1,3)
            SpiCtrl_layout.addWidget(self.cbox_fe_peaktimes[chn],chn+1,4)
            SpiCtrl_layout.addWidget(self.cbox_fe_mons[chn],chn+1,5)
            SpiCtrl_layout.addWidget(self.cbox_fe_buffers[chn],chn+1,6)
        
        
        SpiCtrl_layout.addWidget(lbl_fe_chn_all,17,0)
        SpiCtrl_layout.addWidget(self.cbox_fe_input_all,17,1)
        SpiCtrl_layout.addWidget(self.cbox_fe_baseline_all,17,2)
        SpiCtrl_layout.addWidget(self.cbox_fe_gain_all,17,3)
        SpiCtrl_layout.addWidget(self.cbox_fe_peaktime_all,17,4)
        SpiCtrl_layout.addWidget(self.cbox_fe_mon_all,17,5)
        SpiCtrl_layout.addWidget(self.cbox_fe_buffer_all,17,6)
        
        SpiCtrl_layout.addWidget(lbl_fe_glbl,18,0)
        SpiCtrl_layout.addWidget(lbl_fe_pulse_src,18,1)
        SpiCtrl_layout.addWidget(lbl_fe_coupling,18,2)
        SpiCtrl_layout.addWidget(lbl_fe_leakage,18,3)
        SpiCtrl_layout.addWidget(lbl_fe_mon_type,18,4)
        SpiCtrl_layout.addWidget(lbl_asic_dac,18,5)
        
        SpiCtrl_layout.addWidget(self.btn_fe_spi_config,19,0)
        SpiCtrl_layout.addWidget(self.cbox_fe_pulse_src,19,1) 
        SpiCtrl_layout.addWidget(self.cbox_fe_coupling,19,2)
        SpiCtrl_layout.addWidget(self.cbox_fe_leakage,19,3)
        SpiCtrl_layout.addWidget(self.cbox_fe_mon_type,19,4) 
        SpiCtrl_layout.addWidget(self.sp_asic_dac,19,5) 
        
        
        gbox_SpiCtrl.setLayout(SpiCtrl_layout)
        
        #-------------------------------------------------------------------#
        gbox_pulse_param = QGroupBox("pulse param")
        
        lbl_amp = QLabel("FDAC")
        
        self.sp_fpga_dac = QSpinBox()
        self.sp_fpga_dac.setRange(0,31)
        self.sp_fpga_dac.setPrefix("0x")
        self.sp_fpga_dac.setValue(5)
        self.sp_fpga_dac.setSingleStep(1)
        self.sp_fpga_dac.setDisplayIntegerBase(16)
        self.sp_fpga_dac.valueChanged.connect(self.fun_fe_fpgadac)
        
        
        lbl_delay = QLabel("Delay")
        self.ledit_dly = QLineEdit("77") 
        
        lbl_period = QLabel("Period")
        self.ledit_period = QLineEdit("500")  
        
        lbl_width = QLabel("Width")
        self.ledit_width = QLineEdit("0xa00") 
        
        self.btn_set_pulse_param = QPushButton("set param")
        self.btn_set_pulse_param.clicked.connect(self.fun_SetPulseParam_clicked)   
        
        pulse_param_layout = QGridLayout()
        
        pulse_param_layout.addWidget(lbl_amp,0,0)
        pulse_param_layout.addWidget(self.sp_fpga_dac,0,1)
        
        pulse_param_layout.addWidget(lbl_delay,1,0)
        pulse_param_layout.addWidget(self.ledit_dly,1,1)
        
        pulse_param_layout.addWidget(lbl_period,2,0)
        pulse_param_layout.addWidget(self.ledit_period,2,1)
        
        pulse_param_layout.addWidget(lbl_width,3,0)
        pulse_param_layout.addWidget(self.ledit_width,3,1) 
        pulse_param_layout.addWidget(self.btn_set_pulse_param,4,0) 
        gbox_pulse_param.setLayout(pulse_param_layout)
           
        tab1_layout = QGridLayout()
        tab1_layout.addWidget(gbox_SpiCtrl,0,0)
        tab1_layout.addWidget(gbox_pulse_param,1,0)        
        tab1.setLayout(tab1_layout)
        
        #-----------------------------------tab2------------------------------#
        tab2 = QWidget()
        
        gbox_config = QGroupBox("W/R register")
        self.rbtn_I2C = QRadioButton("I2C")
        self.rbtn_I2C.setChecked(True)
        self.rbtn_UART = QRadioButton("UART")
        self.rbtn_I2C.toggled.connect(lambda:self.I2C_UART_switch(self.rbtn_I2C))
        self.rbtn_UART.toggled.connect(lambda:self.I2C_UART_switch(self.rbtn_UART))
        
        lbl_page = QLabel("Page")
        self.cbox_page = QComboBox()
        self.cbox_page.addItem("1")
        self.cbox_page.addItem("2")
        self.cbox_page.addItem("0")
        #self.cbox_page.activated[str].connect(self.Change_I2C_page)
        lbl_AdcRegAddr = QLabel("Reg")
        lbl_AdcRegVal = QLabel("Val")
        self.ledit_AdcRegAddr = QLineEdit("int")
        self.ledit_AdcRegVal = QLineEdit("hex")        
        
        self.btn_AdcRegWrite = QPushButton("&write")
        self.btn_AdcRegWrite.clicked.connect(self.ADCwritebtn_clicked)
       
        self.btn_AdcRegRead = QPushButton("&read")
        self.btn_AdcRegRead.clicked.connect(self.ADCreadbtn_clicked)
        
        self.btn_AdcHardreset = QPushButton("adc hard reset")    
        self.btn_AdcHardreset.clicked.connect(self.btn_AdcHardreset_clicked)
        
        self.btn_AdcSoftreset = QPushButton("adc soft reset")
        self.btn_AdcSoftreset.clicked.connect(self.btn_AdcSoftreset_clicked)

        self.btn_readout_reg = QPushButton("read regs")
        self.btn_readout_reg.clicked.connect(self.btn_readout_reg_clicked)
        self.lbl_readoutreg = QLabel("wait...")
        
        config_layout = QGridLayout()
        config_layout.addWidget(self.rbtn_I2C,0,0)
        config_layout.addWidget(self.rbtn_UART,0,1)
        config_layout.addWidget(lbl_page,0,2)
        config_layout.addWidget(self.cbox_page,0,3)
        config_layout.addWidget(lbl_AdcRegAddr,1,0)
        config_layout.addWidget(self.ledit_AdcRegAddr,1,1)
        config_layout.addWidget(lbl_AdcRegVal,1,2)
        config_layout.addWidget(self.ledit_AdcRegVal,1,3)
        config_layout.addWidget(self.btn_AdcRegWrite,2,0)
        config_layout.addWidget(self.btn_AdcRegRead,2,1)
        
        config_layout.addWidget(self.btn_AdcHardreset,3,0)
        config_layout.addWidget(self.btn_AdcSoftreset,3,1)
        config_layout.addWidget(self.btn_readout_reg,3,2)
        config_layout.addWidget(self.lbl_readoutreg,3,3)
        gbox_config.setLayout(config_layout)
        
        #--------------------------------------------------------------#
        gbox_ref = QGroupBox("Reference") #add a tab widget here
        
        lbl_refVol = QLabel("Ref Voltage:")
        self.cbox_refvol = QComboBox()
        self.cbox_refvol.addItem("BJT")
        self.cbox_refvol.addItem("BJT_EXT")
        self.cbox_refvol.addItem("CMOS")
        self.cbox_refvol.addItem("EXTERNAL")
        self.cbox_refvol.activated[str].connect(self.fun_refVolMode)
        
        lbl_biasCur = QLabel("Bias Current:")
        self.cbox_biascur = QComboBox() 
        self.cbox_biascur.addItem("BJT")
        self.cbox_biascur.addItem("CMOS_INTR")
        self.cbox_biascur.addItem("CMOS_EXTR")
        self.cbox_biascur.addItem("PlanB")
        self.cbox_biascur.activated[str].connect(self.fun_biasCurMode)
        
        ReferenceTab = QTabWidget()
        
        BJT_tab = QWidget()
        lbl_VREFP = QLabel("VREFP")
        lbl_VREFN = QLabel("VREFN")
        lbl_VCMI = QLabel("VCMI")
        lbl_VCMO = QLabel("VCMO")
        
        self.ledit_VREFP = QLineEdit("0xff")
        self.ledit_VREFN = QLineEdit("0x40")
        self.ledit_VCMI  = QLineEdit("0x7B")
        self.ledit_VCMO  = QLineEdit("0x9F")
        
        lbl_ioffset_vrefp = QLabel("ioffset")
        self.cbox_ioffset_vrefp = QComboBox()
        self.cbox_ioffset_vrefp.addItem("9.5pA")
        self.cbox_ioffset_vrefp.addItem("6.3uA")
        self.cbox_ioffset_vrefp.addItem("9.5uA")
        self.cbox_ioffset_vrefp.addItem("12.6uA")
        self.cbox_ioffset_vrefp.activated[str].connect(self.fun_ioffset_vrefp)
        
        lbl_ioffset_vrefn = QLabel("ioffset")
        self.cbox_ioffset_vrefn = QComboBox()
        self.cbox_ioffset_vrefn.addItem("9.5pA")
        self.cbox_ioffset_vrefn.addItem("6.3uA")
        self.cbox_ioffset_vrefn.addItem("9.5uA")
        self.cbox_ioffset_vrefn.addItem("12.6uA")
        self.cbox_ioffset_vrefn.activated[str].connect(self.fun_ioffset_vrefn)
        
        lbl_ioffset_vcmi = QLabel("ioffset")
        self.cbox_ioffset_vcmi = QComboBox()
        self.cbox_ioffset_vcmi.addItem("9.5pA")
        self.cbox_ioffset_vcmi.addItem("6.3uA")
        self.cbox_ioffset_vcmi.addItem("9.5uA")
        self.cbox_ioffset_vcmi.addItem("12.6uA")
        self.cbox_ioffset_vcmi.activated[str].connect(self.fun_ioffset_vcmi)
        
        lbl_ioffset_vcmo = QLabel("ioffset")
        self.cbox_ioffset_vcmo = QComboBox()
        self.cbox_ioffset_vcmo.addItem("9.5pA")
        self.cbox_ioffset_vcmo.addItem("6.3uA")
        self.cbox_ioffset_vcmo.addItem("9.5uA")
        self.cbox_ioffset_vcmo.addItem("12.6uA")    
        self.cbox_ioffset_vcmo.activated[str].connect(self.fun_ioffset_vcmo)
        
        lbl_ibuff0 = QLabel("ibuff0_15")
        lbl_ibuff1 = QLabel("ibuff1_16")
        lbl_idac0 = QLabel("idac0_17")
        lbl_idac1 = QLabel("idac1_18")
        
        self.ledit_ibuff0 = QLineEdit("0xff")
        self.ledit_ibuff1 = QLineEdit("0xff")
        self.ledit_idac0  = QLineEdit("0xff")
        self.ledit_idac1  = QLineEdit("0xff")        
        
        lbl_ref_monitor = QLabel("monitor")
        self.ledit_refmon_H = QLineEdit("0x00")
        self.ledit_refmon_L = QLineEdit("0x00")
        
        lbl_ref_powerdone = QLabel("powerdone")
        self.ledit_refpwd_H = QLineEdit("0x00")
        self.ledit_refpwd_L = QLineEdit("0x00")        
        
        self.btn_SetRefVol = QPushButton("SetRefVol")
        self.btn_SetRefVol.clicked.connect(self.btn_SetRefVol_clicked)
        
        self.btn_Setoffset = QPushButton("Set ioffset")
        self.btn_Setoffset.clicked.connect(self.btn_Setoffset_clicked)
  
        self.btn_Setibuff = QPushButton("Set ibuff")
        self.btn_Setibuff.clicked.connect(self.btn_Setibuff_clicked)
        
        self.btn_Setidac = QPushButton("Set idac")
        self.btn_Setidac.clicked.connect(self.btn_Setidac_clicked)
        
        self.btn_SetrefMon = QPushButton("Set refmon")
        self.btn_SetrefMon.clicked.connect(self.btn_SetrefMon_clicked)        
  
        self.btn_Setpwrdown = QPushButton("Set pwrdown")
        self.btn_Setpwrdown.clicked.connect(self.btn_Setpwrdown_clicked)          
        
        BJT_layout = QGridLayout()
        
        BJT_layout.addWidget(lbl_VREFP,0,0)
        BJT_layout.addWidget(self.ledit_VREFP,0,1)
        BJT_layout.addWidget(lbl_ioffset_vrefp,0,2)
        BJT_layout.addWidget(self.cbox_ioffset_vrefp,0,3)        
        
        BJT_layout.addWidget(lbl_VREFN,1,0)
        BJT_layout.addWidget(self.ledit_VREFN,1,1)
        BJT_layout.addWidget(lbl_ioffset_vrefn,1,2)
        BJT_layout.addWidget(self.cbox_ioffset_vrefn,1,3) 

        BJT_layout.addWidget(lbl_VCMI,2,0)
        BJT_layout.addWidget(self.ledit_VCMI,2,1)
        BJT_layout.addWidget(lbl_ioffset_vcmi,2,2)
        BJT_layout.addWidget(self.cbox_ioffset_vcmi,2,3)               
        
        BJT_layout.addWidget(lbl_VCMO,3,0)
        BJT_layout.addWidget(self.ledit_VCMO,3,1)
        BJT_layout.addWidget(lbl_ioffset_vcmo,3,2)
        BJT_layout.addWidget(self.cbox_ioffset_vcmo,3,3)            
        
        BJT_layout.addWidget(self.btn_SetRefVol,4,1)
        BJT_layout.addWidget(self.btn_Setoffset,4,3)
        
        
        BJT_layout.addWidget(lbl_ibuff0,5,0)
        BJT_layout.addWidget(self.ledit_ibuff0,5,1)
        
        BJT_layout.addWidget(lbl_ibuff1,6,0)
        BJT_layout.addWidget(self.ledit_ibuff1,6,1)
        
        BJT_layout.addWidget(lbl_idac0,5,2)
        BJT_layout.addWidget(self.ledit_idac0,5,3)
        
        BJT_layout.addWidget(lbl_idac1,6,2)
        BJT_layout.addWidget(self.ledit_idac1,6,3)   
             
        BJT_layout.addWidget(self.btn_Setibuff,7,1)          
        BJT_layout.addWidget(self.btn_Setidac,7,3)
        
        BJT_layout.addWidget(lbl_ref_monitor,8,0) 
        BJT_layout.addWidget(self.ledit_refmon_H,8,1)
        BJT_layout.addWidget(self.ledit_refmon_L,8,2)

        BJT_layout.addWidget(lbl_ref_powerdone,9,0) 
        BJT_layout.addWidget(self.ledit_refpwd_H,9,1)
        BJT_layout.addWidget(self.ledit_refpwd_L,9,2)
        
        BJT_layout.addWidget(self.btn_SetrefMon,8,3)        
        BJT_layout.addWidget(self.btn_Setpwrdown,9,3)         
        BJT_tab.setLayout(BJT_layout)
        
        CMOS_tab = QWidget()
        #CMOS tab widget for CMOS reference generation
        lbl_CMOS_VREFP = QLabel("VREFP")
        lbl_CMOS_VREFN = QLabel("VREFN")
        lbl_CMOS_VCMI = QLabel("VCMI")
        lbl_CMOS_VCMO = QLabel("VCMO")
#
        self.ledit_CMOS_VREFP = QLineEdit("0xcc")
        self.ledit_CMOS_VREFN = QLineEdit("0x2b")
        self.ledit_CMOS_VCMI  = QLineEdit("0x5b")
        self.ledit_CMOS_VCMO  = QLineEdit("0x7b")
        
        lbl_CMOS_ibuff0 = QLabel("ibuff0")
        lbl_CMOS_ibuff1 = QLabel("ibuff1")  
        
        lbl_CMOS_ibuff_inst = QLabel("ibuff: 512uA-N*8uA")
        lbl_CMOS_ref_inst = QLabel("REF: N/255 * VDDA")
        
        self.ledit_CMOS_ibuff0  = QLineEdit("0x00")
        self.ledit_CMOS_ibuff1  = QLineEdit("0x00")

        self.btn_SetCMOSRefV = QPushButton("Set Ref")
        self.btn_SetCMOSRefV.clicked.connect(self.btn_SetCMOSRefV_clicked) 
           
        self.btn_SetCMOSibuff = QPushButton("Set ibuff")
        self.btn_SetCMOSibuff.clicked.connect(self.btn_SetCMOSibuff_clicked)
        
        lbl_vt_iref_trim = QLabel("iref_trim")
        self.sp_vt_iref_trim = QSpinBox()
        self.sp_vt_iref_trim.setSuffix("uA")
        self.sp_vt_iref_trim.setRange(35,70)
        self.sp_vt_iref_trim.setValue(50)
        self.sp_vt_iref_trim.setSingleStep(5)
        self.sp_vt_iref_trim.valueChanged.connect(self.fun_vt_iref_trim)        
        
        
        CMOS_layout = QGridLayout()
        CMOS_layout.addWidget(lbl_CMOS_VREFP,0,0)
        CMOS_layout.addWidget(self.ledit_CMOS_VREFP,0,1)
        CMOS_layout.addWidget(lbl_CMOS_ibuff0,0,2)
        CMOS_layout.addWidget(self.ledit_CMOS_ibuff0,0,3)
        
        CMOS_layout.addWidget(lbl_CMOS_VREFN,1,0)
        CMOS_layout.addWidget(self.ledit_CMOS_VREFN,1,1)
        CMOS_layout.addWidget(lbl_CMOS_ibuff1,1,2)
        CMOS_layout.addWidget(self.ledit_CMOS_ibuff1,1,3)
        
        CMOS_layout.addWidget(lbl_CMOS_VCMI,2,0)
        CMOS_layout.addWidget(self.ledit_CMOS_VCMI,2,1)
        CMOS_layout.addWidget(self.btn_SetCMOSibuff,2,3)
        
        CMOS_layout.addWidget(lbl_CMOS_VCMO,3,0)
        CMOS_layout.addWidget(self.ledit_CMOS_VCMO,3,1)
        
        CMOS_layout.addWidget(lbl_vt_iref_trim,3,2)
        CMOS_layout.addWidget(self.sp_vt_iref_trim,3,3)
        
        
        CMOS_layout.addWidget(self.btn_SetCMOSRefV,4,1)
        CMOS_layout.addWidget(lbl_CMOS_ref_inst,4,2)
        CMOS_layout.addWidget(lbl_CMOS_ibuff_inst,4,3)
        CMOS_tab.setLayout(CMOS_layout)
        
        ReferenceTab.addTab(BJT_tab,"BJT")
        ReferenceTab.addTab(CMOS_tab,"CMOS")
        
        ref_layout = QGridLayout()
        ref_layout.addWidget(lbl_refVol,0,0)
        ref_layout.addWidget(self.cbox_refvol,0,1)
        ref_layout.addWidget(lbl_biasCur,0,2)
        ref_layout.addWidget(self.cbox_biascur,0,3)
        ref_layout.addWidget(ReferenceTab,1,0,1,4)
        gbox_ref.setLayout(ref_layout)
        
        #-----------------------------------------------------#
        gbox_debug = QGroupBox("debug")    
        DebugCaliTab = QTabWidget()
        debug_tab = QWidget()
        
        lbl_adc0_pattern = QLabel("adc0 pattern")
        self.ledit_adc0_pattern_L = QLineEdit("0xcd")
        self.ledit_adc0_pattern_H = QLineEdit("0xab")
        self.btn_LoadADC0Pattern = QPushButton("load pattern")
        self.btn_LoadADC0Pattern.clicked.connect(self.btn_LoadADC0Pattern_clicked)
        
        lbl_adc1_pattern = QLabel("adc1 pattern")
        self.ledit_adc1_pattern_L = QLineEdit("0x34")
        self.ledit_adc1_pattern_H = QLineEdit("0x12") 
        self.btn_LoadADC1Pattern = QPushButton("load pattern")
        self.btn_LoadADC1Pattern.clicked.connect(self.btn_LoadADC1Pattern_clicked)   
        
        lbl_test_data_mode = QLabel("test_data_mode")
        self.cbox_testdatamode = QComboBox()
        self.cbox_testdatamode.addItem("Normal")
        self.cbox_testdatamode.addItem("Test Pattern")
        self.cbox_testdatamode.activated[str].connect(self.fun_testdatamode)
        
        lbl_frame_marker = QLabel("frame maker shifts")
        # change code here
        self.sp_framemarker_shift = QSpinBox()
        self.sp_framemarker_shift.setRange(0,31)
        self.sp_framemarker_shift.setValue(0)
        self.sp_framemarker_shift.setSingleStep(1)
        self.sp_framemarker_shift.valueChanged.connect(self.fun_framemakershift)
        
        #self.ledit_framemaker = QLineEdit("0")

        
        debug_layout = QGridLayout()
        debug_layout.addWidget(lbl_adc0_pattern,0,0)
        debug_layout.addWidget(self.ledit_adc0_pattern_H,0,1)
        debug_layout.addWidget(self.ledit_adc0_pattern_L,0,2)
        debug_layout.addWidget(self.btn_LoadADC0Pattern,0,3)        
        debug_layout.addWidget(lbl_adc1_pattern,1,0)
        debug_layout.addWidget(self.ledit_adc1_pattern_H,1,1)
        debug_layout.addWidget(self.ledit_adc1_pattern_L,1,2)
        debug_layout.addWidget(self.btn_LoadADC1Pattern,1,3)  
        debug_layout.addWidget(lbl_test_data_mode,2,0)
        debug_layout.addWidget(self.cbox_testdatamode,2,1)
        debug_layout.addWidget(lbl_frame_marker,3,0)
        debug_layout.addWidget(self.sp_framemarker_shift,3,1)
        debug_tab.setLayout(debug_layout)
        
        Cali_tab = QWidget()
        self.btn_autocali = QPushButton("AutoCali")
        self.btn_autocali.clicked.connect(self.btn_autocali_clicked)
        self.lbl_calistatus = QLabel("Process...")      
  
        self.btn_calionebyone = QPushButton("Calione")
        self.btn_calionebyone.clicked.connect(self.btn_calionebyone_clicked)


      
        lbl_samples = QLabel("samples average")
        self.ledit_samples_avr = QLineEdit("16000")
        
        lbl_run_times = QLabel("Run times")
        self.ledit_run_time = QLineEdit("1")
        
        self.btn_save_weights = QPushButton("Save Weights")
        self.btn_save_weights.clicked.connect(self.btn_save_weights_clicked)
        
        self.btn_load_weights = QPushButton("Load Weights")
        self.btn_load_weights.clicked.connect(self.btn_load_weights_clicked)
        
        self.lbl_load_status = QLabel("Wait...")  
        
        Cali_layout = QGridLayout()
        Cali_layout.addWidget(lbl_samples,0,0)
        Cali_layout.addWidget(self.ledit_samples_avr,0,1)
        Cali_layout.addWidget(lbl_run_times,0,2)
        Cali_layout.addWidget(self.ledit_run_time,0,3)
        
        Cali_layout.addWidget(self.btn_autocali,1,0)
        Cali_layout.addWidget(self.btn_calionebyone,1,1)
        Cali_layout.addWidget(self.lbl_calistatus,1,2)
        
        Cali_layout.addWidget(self.btn_save_weights,2,0)
        Cali_layout.addWidget(self.btn_load_weights,2,1)
        Cali_layout.addWidget(self.lbl_load_status,2,2)
        
        Cali_tab.setLayout(Cali_layout)
        
        DebugCaliTab.addTab(debug_tab,"Debug")
        DebugCaliTab.addTab(Cali_tab,"Calibration")
        
        
        debugcali_layout = QGridLayout()
        debugcali_layout.addWidget(DebugCaliTab)
        gbox_debug.setLayout(debugcali_layout)
    
        #--------------------------------------------#    
        gbox_converter = QGroupBox("Converter Config")
        lbl_adc_bias = QLabel("adc_bias")
        self.sp_adc_bias = QSpinBox()
        self.sp_adc_bias.setSuffix("uA")
        self.sp_adc_bias.setRange(10,80)
        self.sp_adc_bias.setValue(60)
        self.sp_adc_bias.setSingleStep(10)
        self.sp_adc_bias.valueChanged.connect(self.fun_adc_bias)           
        
        lbl_edgeselect = QLabel("edge select")
        self.cbox_edgeselect = QComboBox()
        self.cbox_edgeselect.addItem("Nominal")
        self.cbox_edgeselect.addItem("inverted")
        self.cbox_edgeselect.activated[str].connect(self.fun_edgeselect)
        
        lbl_outputformat = QLabel("out_format")
        self.cbox_outputformat = QComboBox()
        self.cbox_outputformat.addItem("two-complement")
        self.cbox_outputformat.addItem("offset binary")
        self.cbox_outputformat.activated[str].connect(self.fun_outputformat)
        
        lbl_syncmode = QLabel("sync_mode")
        self.cbox_syncmode = QComboBox()
        self.cbox_syncmode.addItem("Normal")
        self.cbox_syncmode.addItem("Analog pattern")
        self.cbox_syncmode.activated[str].connect(self.fun_syncmode)

        lbl_testinput = QLabel("test_input")
        self.cbox_testinput = QComboBox()
        self.cbox_testinput.addItem("Normal")
        self.cbox_testinput.addItem("ADC_TEST_IN")
        self.cbox_testinput.activated[str].connect(self.fun_testinput)
        
        lbl_outputselect = QLabel("output_s")
        self.cbox_outputselect = QComboBox()
        self.cbox_outputselect.addItem("cali_ADCdata")
        self.cbox_outputselect.addItem("uncali_ADCdata")
        self.cbox_outputselect.addItem("raw_ADC0")
        self.cbox_outputselect.addItem("raw_ADC1")
        self.cbox_outputselect.activated[str].connect(self.fun_outputselect)
        
        converter_layout = QGridLayout()
        converter_layout.addWidget(lbl_edgeselect,0,0)
        converter_layout.addWidget(self.cbox_edgeselect,0,1)
        
        converter_layout.addWidget(lbl_outputformat,1,0)
        converter_layout.addWidget(self.cbox_outputformat,1,1)
        
        converter_layout.addWidget(lbl_syncmode,2,0)
        converter_layout.addWidget(self.cbox_syncmode,2,1)

        converter_layout.addWidget(lbl_testinput,3,0)
        converter_layout.addWidget(self.cbox_testinput,3,1)
        
        converter_layout.addWidget(lbl_outputselect,4,0)
        converter_layout.addWidget(self.cbox_outputselect,4,1)   
        
        converter_layout.addWidget(lbl_adc_bias,5,0)
        converter_layout.addWidget(self.sp_adc_bias,5,1)
        gbox_converter.setLayout(converter_layout)
        
        gbox_inputbuffer = QGroupBox("Input buffer")
        lbl_sdc = QLabel("single-to-diff")
        self.cbox_sdc = QComboBox()
        self.cbox_sdc.addItem("On")
        self.cbox_sdc.addItem("Bypass")
        self.cbox_sdc.activated[str].connect(self.fun_sdc)

        lbl_db = QLabel("diff buffer")
        self.cbox_db = QComboBox()
        self.cbox_db.addItem("Bypass")
        self.cbox_db.addItem("On")
        self.cbox_db.activated[str].connect(self.fun_db)
        
        lbl_sha_se = QLabel("sha_se_input")
        self.cbox_sha_se = QComboBox()
        self.cbox_sha_se.addItem("Diff")
        self.cbox_sha_se.addItem("Single-ended")
        self.cbox_sha_se.activated[str].connect(self.fun_sha_se)        
        

        lbl_currsrc = QLabel("curr src")
        self.cbox_currsrc = QComboBox()
        self.cbox_currsrc.addItem("BJT-sd")
        self.cbox_currsrc.addItem("BJT-db")
        self.cbox_currsrc.addItem("CMOS-sd")
        self.cbox_currsrc.addItem("CMOS-db")        
        self.cbox_currsrc.activated[str].connect(self.fun_currsc)        
        
        inputbuffer_layout = QGridLayout()
        inputbuffer_layout.addWidget(lbl_sdc,0,0)
        inputbuffer_layout.addWidget(self.cbox_sdc,0,1)
        
        inputbuffer_layout.addWidget(lbl_db,1,0)
        inputbuffer_layout.addWidget(self.cbox_db,1,1)
        
        inputbuffer_layout.addWidget(lbl_sha_se,2,0)
        inputbuffer_layout.addWidget(self.cbox_sha_se,2,1)
        
        inputbuffer_layout.addWidget(lbl_currsrc,3,0)
        inputbuffer_layout.addWidget(self.cbox_currsrc,3,1)  
        
        gbox_inputbuffer.setLayout(inputbuffer_layout)
        
        #--------------SHA------------#
        gbox_shaper = QGroupBox("SHA")
        
        lbl_freeze_sha0 = QLabel("freeze_ADC0")
        self.cbox_freeze_sha0 = QComboBox()
        self.cbox_freeze_sha0.addItem("Normal")
        self.cbox_freeze_sha0.addItem("Freeze")
        self.cbox_freeze_sha0.activated[str].connect(self.fun_freeze_sha0)    

        lbl_freeze_sha1 = QLabel("freeze_ADC1")
        self.cbox_freeze_sha1 = QComboBox()
        self.cbox_freeze_sha1.addItem("Normal")
        self.cbox_freeze_sha1.addItem("Freeze")
        self.cbox_freeze_sha1.activated[str].connect(self.fun_freeze_sha1)          
        
        lbl_freeze_select0 = QLabel("freeze_select0")
        self.sp_freeze_select0 = QSpinBox()
        self.sp_freeze_select0.setPrefix("SHA")
        self.sp_freeze_select0.setRange(0,7)
        self.sp_freeze_select0.setValue(0)
        self.sp_freeze_select0.setSingleStep(10)
        self.sp_freeze_select0.valueChanged.connect(self.fun_freeze_select_0)
        
        lbl_freeze_select1 = QLabel("freeze_select1")
        self.sp_freeze_select1 = QSpinBox()
        self.sp_freeze_select1.setPrefix("SHA")
        self.sp_freeze_select1.setRange(0,7)
        self.sp_freeze_select1.setValue(0)
        self.sp_freeze_select1.setSingleStep(10)
        self.sp_freeze_select1.valueChanged.connect(self.fun_freeze_select_1)

        lbl_sha0_bias = QLabel("sha0_bias")
        self.sp_sha0_bias = QSpinBox()
        self.sp_sha0_bias.setSuffix("uA")
        self.sp_sha0_bias.setRange(10,80)
        self.sp_sha0_bias.setValue(50)
        self.sp_sha0_bias.setSingleStep(10)
        self.sp_sha0_bias.valueChanged.connect(self.fun_sha0_bias)
        
        lbl_sha1_bias = QLabel("sha1_bias")  
        self.sp_sha1_bias = QSpinBox()
        self.sp_sha1_bias.setSuffix("uA")
        self.sp_sha1_bias.setRange(10,80)
        self.sp_sha1_bias.setValue(50)
        self.sp_sha1_bias.setSingleStep(10)
        self.sp_sha1_bias.valueChanged.connect(self.fun_sha1_bias)        
        
        lbl_sha2_bias = QLabel("sha2_bias")
        self.sp_sha2_bias = QSpinBox()
        self.sp_sha2_bias.setSuffix("uA")
        self.sp_sha2_bias.setRange(10,80)
        self.sp_sha2_bias.setValue(50)
        self.sp_sha2_bias.setSingleStep(10)
        self.sp_sha2_bias.valueChanged.connect(self.fun_sha2_bias)              

        lbl_sha3_bias = QLabel("sha3_bias")
        self.sp_sha3_bias = QSpinBox()
        self.sp_sha3_bias.setSuffix("uA")
        self.sp_sha3_bias.setRange(10,80)
        self.sp_sha3_bias.setValue(50)
        self.sp_sha3_bias.setSingleStep(10)
        self.sp_sha3_bias.valueChanged.connect(self.fun_sha3_bias)  

        lbl_sha4_bias = QLabel("sha4_bias")
        self.sp_sha4_bias = QSpinBox()
        self.sp_sha4_bias.setSuffix("uA")
        self.sp_sha4_bias.setRange(10,80)
        self.sp_sha4_bias.setValue(50)
        self.sp_sha4_bias.setSingleStep(10)
        self.sp_sha4_bias.valueChanged.connect(self.fun_sha4_bias)
        
        lbl_sha5_bias = QLabel("sha5_bias") 
        self.sp_sha5_bias = QSpinBox()
        self.sp_sha5_bias.setSuffix("uA")
        self.sp_sha5_bias.setRange(10,80)
        self.sp_sha5_bias.setValue(50)
        self.sp_sha5_bias.setSingleStep(10)
        self.sp_sha5_bias.valueChanged.connect(self.fun_sha5_bias) 
        
        lbl_sha6_bias = QLabel("sha6_bias")
        self.sp_sha6_bias = QSpinBox()
        self.sp_sha6_bias.setSuffix("uA")
        self.sp_sha6_bias.setRange(10,80)
        self.sp_sha6_bias.setValue(50)
        self.sp_sha6_bias.setSingleStep(10)
        self.sp_sha6_bias.valueChanged.connect(self.fun_sha6_bias)   
        
        lbl_sha7_bias = QLabel("sha7_bias")
        self.sp_sha7_bias = QSpinBox()
        self.sp_sha7_bias.setSuffix("uA")
        self.sp_sha7_bias.setRange(10,80)
        self.sp_sha7_bias.setValue(50)
        self.sp_sha7_bias.setSingleStep(10)
        self.sp_sha7_bias.valueChanged.connect(self.fun_sha7_bias)
        
        lbl_sha_clk = QLabel("sha_clk")
        self.cbox_sha_clk_select = QComboBox()
        self.cbox_sha_clk_select.addItem("backend")
        self.cbox_sha_clk_select.addItem("internal")        
        self.cbox_sha_clk_select.activated[str].connect(self.fun_sha_clk_select)
        
        
        lbl_sha_pd_0 = QLabel("ADC0_pd")
        self.cbox_sha_pd_0 = QComboBox()
        self.cbox_sha_pd_0.addItem("Normal")
        self.cbox_sha_pd_0.addItem("Powerdown")        
        self.cbox_sha_pd_0.activated[str].connect(self.fun_sha_pd_0)

        lbl_sha_pd_1 = QLabel("ADC1_pd")
        self.cbox_sha_pd_1 = QComboBox()
        self.cbox_sha_pd_1.addItem("Normal")
        self.cbox_sha_pd_1.addItem("Powerdown")        
        self.cbox_sha_pd_1.activated[str].connect(self.fun_sha_pd_1)    

        shaper_layout = QGridLayout()
        
        shaper_layout.addWidget(lbl_freeze_sha0,0,0)
        shaper_layout.addWidget(self.cbox_freeze_sha0,0,1)
        shaper_layout.addWidget(lbl_freeze_sha1,0,2)
        shaper_layout.addWidget(self.cbox_freeze_sha1,0,3)
        
        shaper_layout.addWidget(lbl_freeze_select0,1,0)
        shaper_layout.addWidget(self.sp_freeze_select0,1,1)
        shaper_layout.addWidget(lbl_freeze_select1,1,2)
        shaper_layout.addWidget(self.sp_freeze_select1,1,3)
        
        shaper_layout.addWidget(lbl_sha0_bias,2,0)
        shaper_layout.addWidget(self.sp_sha0_bias,2,1)
        shaper_layout.addWidget(lbl_sha1_bias,2,2)
        shaper_layout.addWidget(self.sp_sha1_bias,2,3)    
      
        shaper_layout.addWidget(lbl_sha2_bias,3,0)
        shaper_layout.addWidget(self.sp_sha2_bias,3,1)
        shaper_layout.addWidget(lbl_sha3_bias,3,2)
        shaper_layout.addWidget(self.sp_sha3_bias,3,3) 

        shaper_layout.addWidget(lbl_sha4_bias,4,0)
        shaper_layout.addWidget(self.sp_sha4_bias,4,1)
        shaper_layout.addWidget(lbl_sha5_bias,4,2)
        shaper_layout.addWidget(self.sp_sha5_bias,4,3) 

        shaper_layout.addWidget(lbl_sha6_bias,5,0)
        shaper_layout.addWidget(self.sp_sha6_bias,5,1)
        shaper_layout.addWidget(lbl_sha7_bias,5,2)
        shaper_layout.addWidget(self.sp_sha1_bias,5,3) 
        
        shaper_layout.addWidget(lbl_sha_pd_0,6,0)
        shaper_layout.addWidget(self.cbox_sha_pd_0,6,1)
        
        shaper_layout.addWidget(lbl_sha_pd_1,6,2)
        shaper_layout.addWidget(self.cbox_sha_pd_1,6,3)
        
        shaper_layout.addWidget(lbl_sha_clk,7,0)
        shaper_layout.addWidget(self.cbox_sha_clk_select,7,1)
        gbox_shaper.setLayout(shaper_layout)

        tab2_layout = QGridLayout()
        tab2_layout.addWidget(gbox_config,0,0,1,1)
        tab2_layout.addWidget(gbox_inputbuffer,1,0,1,1)
        tab2_layout.addWidget(gbox_debug,2,0,1,1)
        tab2_layout.addWidget(gbox_converter,3,0,1,1)
        tab2_layout.addWidget(gbox_ref,0,1,2,1)
        tab2_layout.addWidget(gbox_shaper,2,1,2,1)
        tab2.setLayout(tab2_layout)        
        
        #---------------------------tab3------------------------#
        tab3 = QWidget()
        tab3_layout = QGridLayout()
        self.FPGActrlGroupBox()
        self.ViewControl()
        self.ChannelGroupBox()
        self.COTS_ADC()
        tab3_layout.addWidget(self.FPGAgroupBox,0,0)
        tab3_layout.addWidget(self.ViewControlgroupBox,1,0)
        tab3_layout.addWidget(self.ChngroupBox,0,1)
        tab3_layout.addWidget(self.gbox_cots_adc,1,1)
        
        tab3.setLayout(tab3_layout)
        
        #add tables
        self.ControlTab.addTab(tab1,"&FE")
        self.ControlTab.addTab(tab2,"&ADC")
        self.ControlTab.addTab(tab3,"&FPGA")
    #---------------data Visualization- a part of show-------------------#

    def VisualTabWidget(self):
        self.VisualTab = QTabWidget()
        #--------------tab1 Waveform and FFT-------------#
        tab1 = QWidget()
        Canvas = pg.GraphicsWindow()        
        self.data_plot = Canvas.addPlot(title = "Time Domain")
        self.data_plot.setXRange(0 ,self.CHUNK)
        self.data_plot.showGrid(True, True)
        #chn = self.ChannelSelect()
        self.data_plot.addLegend()
        self.time_curve = self.data_plot.plot(pen=(119,172,48),symbolBrush=(119,172,48),symbolPen='w',symbol='o',symbolSize=2, name = "Time Domain Audio")
        
        # create a plot for the frequency domain data
        Canvas.nextRow()
        self.fft_plot = Canvas.addPlot(title="Frequency Domain") 
        self.fft_plot.addLegend()
        self.fft_plot.showGrid(True, True)
        self.fft_plot.enableAutoRange('xy',True)
        self.fft_curve = self.fft_plot.plot(pen='y', name = "Power Spectrum")
        
        tab1_layout = QGridLayout()
        tab1_layout.addWidget(Canvas)
        tab1.setLayout(tab1_layout)
        
        #----------tab2 histogram DNL and INL-----------#
        tab2 = QWidget()
        tab2_win = pg.GraphicsLayoutWidget(show=True)
        self.p1 = tab2_win.addPlot(title = "ADC0 histogram")
        #self.p1.setXRange(0,4095)
        self.ADC0_hist_0 = self.p1.plot(pen = (19,234,201))
        self.ADC0_hist_1 = self.p1.plot(pen = (0,128,0))
        self.ADC0_hist_2 = self.p1.plot(pen = (19,234,201))
        self.ADC0_hist_3 = self.p1.plot(pen = (195,46,212))
        self.ADC0_hist_4 = self.p1.plot(pen = (250,194,5))
        self.ADC0_hist_5 = self.p1.plot(pen = (54,55,55))
        self.ADC0_hist_6 = self.p1.plot(pen = (0,114,189))
        self.ADC0_hist_7 = self.p1.plot(pen = (217,83,25))
        
        self.p2 = tab2_win.addPlot(title = "ADC1 histogram")
        #self.p2.setXRange(0,4095)
        self.ADC1_hist_0 = self.p2.plot(pen = (19,234,201))
        self.ADC1_hist_1 = self.p2.plot(pen = (0,128,0))
        self.ADC1_hist_2 = self.p2.plot(pen = (19,234,201))
        self.ADC1_hist_3 = self.p2.plot(pen = (195,46,212))
        self.ADC1_hist_4 = self.p2.plot(pen = (250,194,5))
        self.ADC1_hist_5 = self.p2.plot(pen = (54,55,55))
        self.ADC1_hist_6 = self.p2.plot(pen = (0,114,189))
        self.ADC1_hist_7 = self.p2.plot(pen = (217,83,25))    
        
        tab2_win.nextRow()
        self.p3 = tab2_win.addPlot(title = "ADC0 DNL")
        self.ADC0_dnl_0 = self.p3.plot(pen = (19,234,201))
        self.ADC0_dnl_1 = self.p3.plot(pen = (0,128,0))
        self.ADC0_dnl_2 = self.p3.plot(pen = (19,234,201))
        self.ADC0_dnl_3 = self.p3.plot(pen = (195,46,212))
        self.ADC0_dnl_4 = self.p3.plot(pen = (250,194,5))
        self.ADC0_dnl_5 = self.p3.plot(pen = (54,55,55))
        self.ADC0_dnl_6 = self.p3.plot(pen = (0,114,189))
        self.ADC0_dnl_7 = self.p3.plot(pen = (217,83,25))
        
        self.p4 = tab2_win.addPlot(title = "ADC1 DNL")  
        
        self.ADC1_dnl_0 = self.p4.plot(pen = (19,234,201))
        self.ADC1_dnl_1 = self.p4.plot(pen = (0,128,0))
        self.ADC1_dnl_2 = self.p4.plot(pen = (19,234,201))
        self.ADC1_dnl_3 = self.p4.plot(pen = (195,46,212))
        self.ADC1_dnl_4 = self.p4.plot(pen = (250,194,5))
        self.ADC1_dnl_5 = self.p4.plot(pen = (54,55,55))
        self.ADC1_dnl_6 = self.p4.plot(pen = (0,114,189))
        self.ADC1_dnl_7 = self.p4.plot(pen = (217,83,25))
        
        
        tab2_win.nextRow()
        self.p5 = tab2_win.addPlot(title = "ADC0 INL")
        self.ADC0_inl_0 = self.p5.plot(pen = (19,234,201))
        self.ADC0_inl_1 = self.p5.plot(pen = (0,128,0))
        self.ADC0_inl_2 = self.p5.plot(pen = (19,234,201))
        self.ADC0_inl_3 = self.p5.plot(pen = (195,46,212))
        self.ADC0_inl_4 = self.p5.plot(pen = (250,194,5))
        self.ADC0_inl_5 = self.p5.plot(pen = (54,55,55))
        self.ADC0_inl_6 = self.p5.plot(pen = (0,114,189))
        self.ADC0_inl_7 = self.p5.plot(pen = (217,83,25))        
        
        self.p6 = tab2_win.addPlot(title = "ADC1 INL")   
             
        self.ADC1_inl_0 = self.p6.plot(pen = (19,234,201)) #0 0 200
        self.ADC1_inl_1 = self.p6.plot(pen = (0,128,0))
        self.ADC1_inl_2 = self.p6.plot(pen = (19,234,201))
        self.ADC1_inl_3 = self.p6.plot(pen = (195,46,212))
        self.ADC1_inl_4 = self.p6.plot(pen = (250,194,5))
        self.ADC1_inl_5 = self.p6.plot(pen = (54,55,55))
        self.ADC1_inl_6 = self.p6.plot(pen = (0,114,189))
        self.ADC1_inl_7 = self.p6.plot(pen = (217,83,25))  

        tab2_layout = QGridLayout()
        tab2_layout.addWidget(tab2_win)
        tab2.setLayout(tab2_layout)
        
        #----------tab3 DAC SCAN-----------#
        tab3 = QWidget()
        tab3_win = pg.GraphicsLayoutWidget(show=True)
        self.tab3_p1 = tab3_win.addPlot(title="DAC SCAN")
        self.tab3_p1.setLabel('bottom',"DAC")
        self.tab3_p1.setLabel('left',"Amplitude",units='V')
        self.tab3_p1.setXRange(0,255)
        self.dacscanplot = self.tab3_p1.plot(pen=(119,172,48),symbolBrush=(119,172,48),symbolPen='w',symbol='o',symbolSize=2)
        
        tab3_layout = QGridLayout()
        tab3_layout.addWidget(tab3_win)
        tab3.setLayout(tab3_layout)
        
        
        #---------tab4 Xtalk------------------ 
        tab4 = QWidget()
        tab4_win = pg.GraphicsLayoutWidget(show=True)
        
        self.xtalk_chn0 = tab4_win.addPlot(title = "Chn0")
        self.xtalk_chn0.showGrid(x=False,y=True)
        self.ADC_xtalk_0 = self.xtalk_chn0.plot(pen = (19,234,201))
        
        self.xtalk_chn1 = tab4_win.addPlot(title = "Chn1")
        self.xtalk_chn1.showGrid(x=False,y=True)
        self.ADC_xtalk_1 = self.xtalk_chn1.plot(pen = (19,234,201)) 

        self.xtalk_chn2 = tab4_win.addPlot(title = "Chn2")
        self.xtalk_chn2.showGrid(x=False,y=True)
        self.ADC_xtalk_2 = self.xtalk_chn2.plot(pen = (19,234,201))
        
        self.xtalk_chn3 = tab4_win.addPlot(title = "Chn3")
        self.xtalk_chn3.showGrid(x=False,y=True)
        self.ADC_xtalk_3 = self.xtalk_chn3.plot(pen = (19,234,201))       
        
        tab4_win.nextRow()
        
        self.xtalk_chn4 = tab4_win.addPlot(title = "Chn4")
        self.xtalk_chn4.showGrid(x=False,y=True)
        self.ADC_xtalk_4 = self.xtalk_chn4.plot(pen = (19,234,201))
        
        self.xtalk_chn5 = tab4_win.addPlot(title = "Chn5")
        self.xtalk_chn5.showGrid(x=False,y=True)
        self.ADC_xtalk_5 = self.xtalk_chn5.plot(pen = (19,234,201)) 

        self.xtalk_chn6 = tab4_win.addPlot(title = "Chn6")
        self.xtalk_chn6.showGrid(x=False,y=True)
        self.ADC_xtalk_6 = self.xtalk_chn6.plot(pen = (19,234,201))
        
        self.xtalk_chn7 = tab4_win.addPlot(title = "Chn7")
        self.xtalk_chn7.showGrid(x=False,y=True)
        self.ADC_xtalk_7 = self.xtalk_chn7.plot(pen = (19,234,201))             
        
        tab4_win.nextRow()
        
        self.xtalk_chn8 = tab4_win.addPlot(title = "Chn8")
        self.xtalk_chn8.showGrid(x=False,y=True)
        self.ADC_xtalk_8 = self.xtalk_chn8.plot(pen = (19,234,201))
        
        self.xtalk_chn9 = tab4_win.addPlot(title = "Chn9")
        self.xtalk_chn9.showGrid(x=False,y=True)
        self.ADC_xtalk_9 = self.xtalk_chn9.plot(pen = (19,234,201)) 

        self.xtalk_chn10 = tab4_win.addPlot(title = "Chn10")
        self.xtalk_chn10.showGrid(x=False,y=True)
        self.ADC_xtalk_10 = self.xtalk_chn10.plot(pen = (19,234,201))
        
        self.xtalk_chn11 = tab4_win.addPlot(title = "Chn11")
        self.xtalk_chn11.showGrid(x=False,y=True)
        self.ADC_xtalk_11 = self.xtalk_chn11.plot(pen = (19,234,201))    
        
        tab4_win.nextRow()
        
        self.xtalk_chn12 = tab4_win.addPlot(title = "Chn12")
        self.xtalk_chn12.showGrid(x=False,y=True)
        self.ADC_xtalk_12 = self.xtalk_chn12.plot(pen = (19,234,201))
        
        self.xtalk_chn13 = tab4_win.addPlot(title = "Chn13")
        self.xtalk_chn13.showGrid(x=False,y=True)
        self.ADC_xtalk_13 = self.xtalk_chn13.plot(pen = (19,234,201)) 

        self.xtalk_chn14 = tab4_win.addPlot(title = "Chn14")
        self.xtalk_chn14.showGrid(x=False,y=True)
        self.ADC_xtalk_14 = self.xtalk_chn14.plot(pen = (19,234,201))
        
        self.xtalk_chn15 = tab4_win.addPlot(title = "Chn15")
        self.xtalk_chn15.showGrid(x=False,y=True)
        self.ADC_xtalk_15 = self.xtalk_chn15.plot(pen = (19,234,201))         
        
        tab4_layout = QGridLayout()
        tab4_layout.addWidget(tab4_win)
        tab4.setLayout(tab4_layout)
        
        self.VisualTab.addTab(tab1,"&Wave/FFT")
        self.VisualTab.addTab(tab2,"DNL/INL")
        self.VisualTab.addTab(tab3,"DAC/SCAN")
        self.VisualTab.addTab(tab4,"Xtalk")
    #----------------------Action-------------------#    
    #----------------COTS ADC related----------------#
    def fun_BJT_mon(self,text):
        self.brd_config.cots_adc_bjt_mon_src(text)
    def fun_MUX_mon(self,text):
        self.brd_config.cots_adc_mux_mon_src(text)
    def btn_read_cots_adc_clicked(self):
        N = int(self.ledit_cots_avr_points.text(),0)
        amp = self.brd_config.cots_adc_data(N)
        self.ledit_cotsadc_result.setText("%.3fV"%amp)
        
    def fun_dac_steps(self):
        val = self.sp_dac_steps.value()
        return val-1
        #self.brd_config.adc_sha2_bias(val)
    
    def btn_dacscan_start_clicked(self):
        reg = self.brd_config.dac_reg #works
        N = int(self.ledit_cots_avr_points.text(),0)
        step_t = self.fun_dac_steps()
        if step_t == 0:
            step = 1
        else:
            step = step_t
##--------code for UI ----------#
#        val =[]
#        codex =[]
#        for code in range(0,256,step):
#            self.brd_config.adc_write_reg(reg,code)
#            time.sleep(0.5)
#            amp = self.brd_config.cots_adc_data(N)
#            codex.append(code)
#            val.append(amp)
#            time.sleep(0.2)        
#        self.dacscanplot.setData(codex,val)       
##--------code for thread-----------#          
        self.DacScanThread_inst = DacScanThread(reg,N,step)
        self.DacScanThread_inst.interact.connect(self.Update_DACSCAN)
        self.DacScanThread_inst.start()         
        #self.btn_dacscan_start.setDisabled(True)
        #self.btn_dacscan_stop.setEnabled(True)
        
    def btn_dacscan_stop_clicked(self):
        pass        
#        self.DacScanThread_inst.stop()
#        self.DacScanThread_inst.quit()
#        self.DacScanThread_inst.wait()
#        self.btn_dacscan_start.setEnabled(True)
#        self.btn_dacscan_stop.setDisabled(True)
        
        
    def Update_DACSCAN(self,result1):
        if self.DacScanThread_inst.mutex.tryLock():
            result = copy(result1)
            self.DacScanThread_inst.mutex.unlock()
            self.dacscanplot.setData(result[0],result[1])
    #------------------------------------------------#
    #---------FE control--------#  
    
    def fun_fe_baseline(self,text):
        self.brd_config.fe_chn_baseline(text)
        
    def fun_fe_gain(self,text):
        self.brd_config.fe_chn_gain(text)
    
    def fun_fe_peaktime(self,text):
        self.brd_config.fe_chn_peaktime(text)
        
    def fun_fe_mon(self,text):
        self.brd_config.fe_chn_monitor(text)
    
    def fun_fe_buffer(self,text):
        self.brd_config.fe_chn_buffer(text)
        
        
    #----------all channels settings---------#
    def fun_fe_input_all(self,text):
        #set text to all individual channels
        for fe_input in self.cbox_fe_inputs:
            fe_input.setCurrentText(text)
        #pass
    def fun_fe_baseline_all(self,text):
        #set text to all individual channels
        for fe_baseline in self.cbox_fe_baselines:
            fe_baseline.setCurrentText(text)
    def fun_fe_gain_all(self,text):
        #set text to all individual channels
        for fe_gain in self.cbox_fe_gains:
            fe_gain.setCurrentText(text)
    def fun_fe_peaktime_all(self,text):
        #set text to all individual channels
        for fe_peaktime in self.cbox_fe_peaktimes:
            fe_peaktime.setCurrentText(text)
    def fun_fe_mon_all(self,text):
        #set text to all individual channels
        for fe_mon in self.cbox_fe_mons:
            fe_mon.setCurrentText(text)
    def fun_fe_buffer_all(self,text):
        #set text to all individual channels
        for fe_buffer in self.cbox_fe_buffers:
            fe_buffer.setCurrentText(text)
    #--------------FE global registers settings-----#    
    def fun_fe_pulse_src(self,text):
        self.brd_config.fe_pulse_src(text)
        self.brd_config.fe_pulse_config(text) #Pulse scource and pulse config will do this job
        
    def fun_fe_coupling(self,text):
        self.brd_config.fe_Coupled(text)
    
    def fun_fe_leakage(self,text):
        self.brd_config.fe_Leakage(text)
        
    def fun_fe_mon_type(self,text):
        self.brd_config.fe_monitor_type(text)
    
    def fun_fe_asicdac(self,text):
        val = self.sp_asic_dac.value()
        self.brd_config.fe_sdac(val)
        
    @pyqtSlot()     
    def fun_FeSpiConfig_clicked(self):
        #Do something here.
        #get Current text of each combobox 
        fe_inputs = []
        for fe_input in self.cbox_fe_inputs:
            tem = fe_input.currentText()
            fe_inputs.append(tem)          
        fe_baselines = []
        for fe_baseline in self.cbox_fe_baselines:
            tem = fe_baseline.currentText()
            fe_baselines.append(tem)      
        fe_gains = []
        for fe_gain in self.cbox_fe_gains:
            tem = fe_gain.currentText()
            fe_gains.append(tem)      
        fe_peaktimes = []
        for fe_peaktime in self.cbox_fe_peaktimes:
            tem = fe_peaktime.currentText()
            fe_peaktimes.append(tem)          
        fe_mons = []
        for fe_mon in self.cbox_fe_mons:
            tem = fe_mon.currentText()
            fe_mons.append(tem)         
        fe_buffers=[]
        for fe_buffer in self.cbox_fe_buffers:
            tem = fe_buffer.currentText()
            fe_buffers.append(tem)
        # now generate channel register value for all 16 channels
        #Now we can generate 16 channels register individually.
        self.brd_config.fe_chn_input(fe_inputs)
        self.brd_config.fe_chn_baseline(fe_baselines)
        self.brd_config.fe_chn_gain(fe_gains)
        self.brd_config.fe_chn_peaktime(fe_peaktimes)
        self.brd_config.fe_chn_monitor(fe_mons)
        self.brd_config.fe_chn_buffer(fe_buffers)
        #print(fe_inputs)
        self.brd_config.fe_spi_config()  
        
    @pyqtSlot()          
    def fun_SetPulseParam_clicked(self):
        delay = int(self.ledit_dly.text(),0)
        period = int(self.ledit_period.text(),0)
        width = int(self.ledit_width.text(),0)
        self.brd_config.fe_pulse_param(delay,period,width)
        
    def fun_fe_fpgadac(self):
        amp = self.sp_fpga_dac.value()
        self.brd_config.fe_fpga_dac(amp)
        
    #-----------------------------------------------#
    @pyqtSlot()  
    def FPGAwritebtn_clicked(self):
        reg = int(self.FPGARegAddrlineEdit.text(),0)
        val = int(self.FPGARegVallineEdit.text(),0)
        self.brd_config.write_fpga_reg(reg,val)

    @pyqtSlot()  
    def FPGAreadbtn_clicked(self):   
        reg = int(self.FPGARegAddrlineEdit.text(),0)
        string = self.brd_config.read_fpga_reg(reg)
        self.FPGARegVallineEdit.setText(string)
    
    def fun_wordorder(self):
        #value = int(sb.value())
        value = int(self.sp_word_order.value())
        self.brd_config.word_order_slider(value)
    def Change_mode(self,text):
        if text == "Normal":
            self.brd_config.Acq_mode('normal')
        elif text == "F_Suffix":
            val = int(self.SuffixlineEdit.text(),0)
            self.brd_config.Acq_mode('fake1',val)
        elif text == "F_ChnID":
            self.brd_config.Acq_mode('fake2')
        
    def fun_testdatamode(self,text):
        self.brd_config.adc_test_data_mode(text)
#        if text == "Normal":
#            self.
#        elif text == "Test Pattern":
        
    def fun_adc_bias(self):
        value = self.sp_adc_bias.value()
        self.brd_config.adc_set_adc_bias(value)
        
    def fun_edgeselect(self,text):
        self.brd_config.adc_edge_select(text)
        
    def fun_outputformat(self,text):
        self.brd_config.adc_outputformat(text)
    
    def fun_syncmode(self,text):
        self.brd_config.adc_sync_mode(text)
    
    def fun_testinput(self,text):
        self.brd_config.adc_test_input(text)
    
    def fun_outputselect(self,text):
        self.brd_config.adc_output_select(text)
        
    def fun_sdc(self,text):
        self.brd_config.adc_sdc_select(text)
    
    def fun_db(self,text):
        self.brd_config.adc_db_select(text)
        
    def fun_sha_se(self,text):
        if text == "Diff":
            self.brd_config.adc_sha_input(0)
        else:
           self.brd_config.adc_sha_input(1) 
    
    def fun_currsc(self,text):
        self.brd_config.adc_ibuff_ctrl(text)
    
    def fun_refVolMode(self,text):
        if text == "BJT":
            self.refVolMode = "BJT"
        elif text == "BJT_EXT":
            self.refVolMode = "BJT_EXT"
        elif text == "CMOS":
            self.refVolMode = "CMOS"
        elif text == "EXTERNAL":
            self.refVolMode = "EXTERNAL"
        self.brd_config.adc_ref_vol_src(self.refVolMode)

    def fun_biasCurMode(self,text):
        if text == "BJT":
            self.biasCurMode = "BJT"
        elif text == "CMOS_INTR":
            self.biasCurMode = "CMOS_INTR"
        elif text == "CMOS_EXTR":
            self.biasCurMode = "CMOS_EXTR"
        elif text == "PlanB":
            self.biasCurMode = "PlanB"
        self.brd_config.adc_bias_curr_src(self.biasCurMode)         

    def fun_ioffset_vrefp(self,text):
        if text == "9.5pA":
            self.ioffset_vrefp = 0
        elif text == "6.3uA":
            self.ioffset_vrefp = 1
        elif text == "9.5uA":
            self.ioffset_vrefp = 2
        elif text == "12.6uA":
            self.ioffset_vrefp = 3
        return self.ioffset_vrefp
    
    def fun_ioffset_vrefn(self,text):
        if text == "9.5pA":
            self.ioffset_vrefn = 0
        elif text == "6.3uA":
            self.ioffset_vrefn = 1
        elif text == "9.5uA":
            self.ioffset_vrefn = 2
        elif text == "12.6uA":
            self.ioffset_vrefn = 3
        return self.ioffset_vrefn   
    
    def fun_ioffset_vcmi(self,text):
        if text == "9.5pA":
            self.ioffset_vcmi = 0
        elif text == "6.3uA":
            self.ioffset_vcmi = 1
        elif text == "9.5uA":
            self.ioffset_vcmi = 2
        elif text == "12.6uA":
            self.ioffset_vcmi = 3
        return self.ioffset_vcmi
    
    def fun_ioffset_vcmo(self,text):
        if text == "9.5pA":
            self.ioffset_vcmo = 0
        elif text == "6.3uA":
            self.ioffset_vcmo = 1
        elif text == "9.5uA":
            self.ioffset_vcmo = 2
        elif text == "12.6uA":
            self.ioffset_vcmo = 3
        return self.ioffset_vcmo   
    
    #----------------CMOS reference-------------#
    @pyqtSlot()  
    def btn_SetCMOSRefV_clicked(self):
        vrefp = int(self.ledit_CMOS_VREFP.text(),0)
        vrefn = int(self.ledit_CMOS_VREFN.text(),0)
        vcmi  = int(self.ledit_CMOS_VCMI.text(),0)
        vcmo  = int(self.ledit_CMOS_VCMO.text(),0)
        self.brd_config.adc_set_cmos_vrefs(vrefp,vrefn,vcmi,vcmo)

    @pyqtSlot()
    def btn_SetCMOSibuff_clicked(self):
        ibuff0 = int(self.ledit_CMOS_ibuff0.text(),0)
        ibuff1 = int(self.ledit_CMOS_ibuff1.text(),0)
        self.brd_config.adc_set_cmos_ibuff(ibuff0,ibuff1)
        
    def fun_vt_iref_trim(self):
        val = self.sp_vt_iref_trim.value()
        self.brd_config.adc_set_cmos_iref_trim(val)
    #-----------------shaper-----------------------------#
    def fun_freeze_sha0(self,text):
        self.brd_config.adc_freeze_sha0(text)
        
    def fun_freeze_sha1(self,text):
        self.brd_config.adc_freeze_sha1(text)
    
    def fun_freeze_select_0(self):
        val = self.sp_freeze_select0.value()
        self.brd_config.adc_freeze_select_0(val)
        
    def fun_freeze_select_1(self):
        val = self.sp_freeze_select1.value()
        self.brd_config.adc_freeze_select_1(val)
        
    def fun_sha0_bias(self):
        val = self.sp_sha0_bias.value()
        self.brd_config.adc_sha0_bias(val)
        
    def fun_sha1_bias(self):
        val = self.sp_sha1_bias.value()
        self.brd_config.adc_sha1_bias(val)
        
    def fun_sha2_bias(self):
        val = self.sp_sha2_bias.value()
        self.brd_config.adc_sha2_bias(val)
        
    def fun_sha3_bias(self):
        val = self.sp_sha3_bias.value()
        self.brd_config.adc_sha3_bias(val)
        
    def fun_sha4_bias(self):
        val = self.sp_sha4_bias.value()
        self.brd_config.adc_sha4_bias(val)
        
    def fun_sha5_bias(self):
        val = self.sp_sha5_bias.value()
        self.brd_config.adc_sha5_bias(val)  
        
    def fun_sha6_bias(self):
        val = self.sp_sha6_bias.value()
        self.brd_config.adc_sha6_bias(val)
        
    def fun_sha7_bias(self):
        val = self.sp_sha7_bias.value()
        self.brd_config.adc_sha7_bias(val)           
    
    def fun_sha_pd_0(self,text):
        self.brd_config.adc_sha_pd_0(text)
    def fun_sha_pd_1(self,text):
        self.brd_config.adc_sha_pd_1(text)
    
    def fun_sha_clk_select(self,text):
        self.brd_config.adc_sha_clk_sel(text)
    #------------------end-------------------------------#  
    @pyqtSlot() 
    def btn_readout_reg_clicked(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filename,_ = QFileDialog.getSaveFileName(self,"Save register values","","reg files(*.txt)",options=options)
        if filename: #return the filename correctly
            #print(filename)
            reg,val = self.brd_config.adc_read_weights()
            reg1,val1,reg2,val2 = self.brd_config.adc_read_config_regs()          
            file = open(filename,"a+")
            file.write("#ADC registers default settings\n")
            file.write("#ADC0 0x0~0xd w0l,w0h; 0x20~0x2d w2l,w2h\n")
            file.write("#ADC1 0x40~0x4d w0l,w0h; 0x60~0x6d w2l,w2h\n")
            #write lines of data to the file
            for i in range(len(reg)):
                file.write("0x%x,0x%x\n"%(reg[i],val[i]))   
                
            file.write("#Configuration registers offset = 0x80\n")
    
            for i in range(len(reg1)):
                file.write("reg%d=0x%x\n"%(reg1[i],val1[i]))
                
            file.write("#registers on page2\n") 
                       
            for i in range(len(reg2)):
                file.write("reg%d=0x%x\n"%(reg2[i],val2[i]))
                
            file.close()
            self.lbl_readoutreg.setText("Done read")
            
    @pyqtSlot()  
    def btn_autocali_clicked(self):
        #Do calibration or 50 times.
        samples = int(self.ledit_samples_avr.text(),0)
        runs = int(self.ledit_run_time.text(),0)
        self.lbl_calistatus.setText("Process")        
        for i in range(runs):
            self.brd_config.adc_autocali(samples)
        self.lbl_calistatus.setText("Done")
    
    @pyqtSlot()
    def btn_calionebyone_clicked(self):
        samples = int(self.ledit_samples_avr.text(),0)
        self.brd_config.adc_autocali_onebyone(samples)
        self.lbl_calistatus.setText("Done one by one")
    @pyqtSlot()    
    def btn_save_weights_clicked(self):
        
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filename,_ = QFileDialog.getSaveFileName(self,"Save calibration weitghs","","Weight files(*.txt)",options=options)
        if filename: #return the filename correctly
            #print(filename)
            #read all the weight
            self.lbl_load_status.setText("Wait...")
            reg,val = self.brd_config.adc_read_weights()
            file = open(filename,"a+")
            file.write("#ADC manual calibration weights\n")
            file.write("#ADC0 0x0~0xd w0l,w0h; 0x20~0x2d w2l,w2h\n")
            file.write("#ADC1 0x40~0x4d w0l,w0h; 0x60~0x6d w2l,w2h\n")
            file.write("#REG,Value stage0~stage6, stage0 is the most significant stage\n")
            #write lines of data to the file
            for i in range(len(reg)):
                file.write("0x%x,0x%x\n"%(reg[i],val[i]))    
            #close the file
            file.close()
            self.lbl_load_status.setText("Save Done")
    @pyqtSlot()
    def btn_load_weights_clicked(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filename,_ = QFileDialog.getOpenFileName(self,"Load calibration weights","","Weight files(*.txt)", options=options)
        reg=[]
        val=[]
        if filename: #return filename correctly, now open the file and read registers then write into the registers
            #print(filename)
            self.lbl_load_status.setText("Wait...")
            file = open(filename,'r')
            for line in file:
                if line[0] == '#':
                    continue
                else:
                    c = [int(e,16) for e in line.split(",")]
                    reg.append(c[0])
                    val.append(c[1])
            file.close()
            self.brd_config.adc_load_weights(reg,val)
            self.lbl_load_status.setText("Load Done")
    @pyqtSlot()    
    def btn_SetRefVol_clicked(self):
        vrefp = int(self.ledit_VREFP.text(),0)
        vrefn = int(self.ledit_VREFN.text(),0)
        vcmi  = int(self.ledit_VCMI.text(),0)
        vcmo  = int(self.ledit_VCMO.text(),0)
        self.brd_config.adc_set_vrefs(vrefp,vrefn,vcmo,vcmi)
        
    @pyqtSlot()     
    def btn_Setoffset_clicked(self):
        #val = (self.ioffset_vcmi << 6) + (self.ioffset_vcmo << 4) + (self.ioffset_vrefn << 2) + self.ioffset_vrefp     
        self.brd_config.adc_set_ioffset(self.ioffset_vrefp,self.ioffset_vrefn,self.ioffset_vcmo,self.ioffset_vcmi)
        
    @pyqtSlot()     
    def btn_Setibuff_clicked(self):
        ibuff0 = int(self.ledit_ibuff0.text(),0)
        ibuff1 = int(self.ledit_ibuff1.text(),0)
        self.brd_config.adc_set_curr_ibuff(ibuff0,ibuff1)
        
    @pyqtSlot()     
    def btn_Setidac_clicked(self):
        idac0 = int(self.ledit_idac0.text(),0)
        idac1 = int(self.ledit_idac1.text(),0)
        self.brd_config.adc_set_curr_vdac(idac0,idac1)
        
    @pyqtSlot()     
    def btn_SetrefMon_clicked(self): 
        Lbyte = int(self.ledit_refmon_L.text(),0)
        Hbyte = int(self.ledit_refmon_H.text(),0)
        self.brd_config.adc_ref_monitor(Lbyte,Hbyte)
        
    @pyqtSlot()     
    def btn_Setpwrdown_clicked(self):    
        Lbyte = int(self.ledit_refpwd_L.text(),0)
        Hbyte = int(self.ledit_refpwd_H.text(),0)
        self.brd_config.adc_ref_powerdown(Lbyte,Hbyte)
    @pyqtSlot()      
    def btn_LoadADC0Pattern_clicked(self):
        Lbyte = int(self.ledit_adc0_pattern_L.text(),0)
        Hbyte = int(self.ledit_adc0_pattern_H.text(),0)
        self.brd_config.adc_load_pattern_0(Lbyte,Hbyte) 
        
    @pyqtSlot()      
    def btn_LoadADC1Pattern_clicked(self):
        Lbyte = int(self.ledit_adc1_pattern_L.text(),0)
        Hbyte = int(self.ledit_adc1_pattern_H.text(),0)
        self.brd_config.adc_load_pattern_1(Lbyte,Hbyte)         
        
    @pyqtSlot()  
    def fun_framemakershift(self):
        value = self.sp_framemarker_shift.value()
        self.brd_config.adc_framemarker_shift(value)     
        
    def ChannelSelect(self):
        val = self.ChnSlider.value()
        return val
    #Setup for I2C or UART tool
    def I2C_UART_switch(self,rbtn):
        if rbtn.isChecked() == True:
            if rbtn.text() == "I2C":
                self.cbox_page.setEnabled(True)
                self.brd_config.adc_i2c_uart("I2C")
                self.tool = "I2C"

            elif rbtn.text()=="UART":
                self.cbox_page.setDisabled(True)
                self.brd_config.adc_i2c_uart("UART")
                self.tool = "UART"
            
    @pyqtSlot() 
    def ADCwritebtn_clicked(self):
        reg = int(self.ledit_AdcRegAddr.text(),0)
        val = int(self.ledit_AdcRegVal.text(),0)
        self.brd_config.adc_write_reg(reg,val)
        #self.ADC.ADC_reg_write(self.tool,reg1,val)
    
    @pyqtSlot()
    def ADCreadbtn_clicked(self):

        reg = int(self.ledit_AdcRegAddr.text(),0)
        string = self.brd_config.adc_read_reg(reg)        
        self.ledit_AdcRegVal.setText(string)     
    
    @pyqtSlot()
    def btn_AdcHardreset_clicked(self):
        self.brd_config.adc_hard_reset()
    @pyqtSlot()        
    def btn_AdcSoftreset_clicked(self):
        self.brd_config.adc_soft_reset()

    @pyqtSlot() 
    def AcqStartbtn_clicked(self):
        self.brd_config.Acq_start_stop(1) #Acq start   
        #time.sleep(0.5)
        self.Wavethread = QThread()       
        self.DFrame = DataFrameThread(self.total_data,self.CHUNK) #PKT num is limited to 174 pkts, otherwise get wrong, get channel 0 by default
        self.DFrame.moveToThread(self.Wavethread)
        self.DFrame.interact.connect(self.Update)
        self.Wavethread.started.connect(self.DFrame.stream)
        self.Wavethread.start()        
        self.AcqStartButton.setDisabled(True)
        self.AcqStopButton.setEnabled(True)
        
    @pyqtSlot()
    def AcqStopbtn_clicked(self):
        self.DFrame.stop()
        self.Wavethread.quit()
        self.Wavethread.wait()
        self.brd_config.Acq_start_stop(0) #Acq stop 
        time.sleep(0.5)
        self.brd_config.Acq_start_stop(0) #Acq stop        
        self.AcqStartButton.setEnabled(True)
        self.AcqStopButton.setDisabled(True)
        
    @pyqtSlot() 
    def btn_CodeScanStart_clicked(self):
        self.brd_config.Acq_start_stop(1) #Acq start   
        #time.sleep(0.5)
        #CodeScanThread(QThread):
        self.Codethread = QThread()       
        self.CodeFrame = CodeScanThread(self.CHUNK) #PKT num is limited to 174 pkts, otherwise get wrong, get channel 0 by default
        self.CodeFrame.moveToThread(self.Codethread)
        self.CodeFrame.interact.connect(self.Update_histo)
        self.Codethread.started.connect(self.CodeFrame.stream)
        self.Codethread.start()        
        self.btn_CodeScanStart.setDisabled(True)
        self.btn_CodeScanStop.setEnabled(True)  
        
    @pyqtSlot()   
    def btn_CodeScanStop_clicked(self):
        self.CodeFrame.stop()
        self.Codethread.quit()
        self.Codethread.wait()
        self.brd_config.Acq_start_stop(0) #Acq stop 
        time.sleep(0.5)
        self.brd_config.Acq_start_stop(0) #Acq stop        
        self.btn_CodeScanStart.setEnabled(True)
        self.btn_CodeScanStop.setDisabled(True)               
    
    @pyqtSlot()
    def btn_NoiseRunStart_clicked(self):
        self.brd_config.Acq_start_stop(1) #Acq start   
        #time.sleep(0.5)
        #CodeScanThread(QThread):
        self.Noisethread = QThread()       
        self.NoiseFrame = NoiseScanThread(self.CHUNK*16) #4096 points PKT num is limited to 174 pkts, otherwise get wrong, get channel 0 by default
        self.NoiseFrame.moveToThread(self.Noisethread)
        self.NoiseFrame.interact.connect(self.Update_Noise_scan)
        self.Noisethread.started.connect(self.NoiseFrame.stream)
        
        self.Noisethread.start() 
        
        self.btn_NoiseRunStart.setDisabled(True)
        self.btn_NoiseRunStop.setEnabled(True)          
        
    def btn_NoiseRunStop_clicked(self):
        self.NoiseFrame.stop()
        self.Noisethread.quit()
        self.Noisethread.wait()
        self.brd_config.Acq_start_stop(0) #Acq stop 
        time.sleep(0.5)
        self.brd_config.Acq_start_stop(0) #Acq stop        
        self.btn_NoiseRunStart.setEnabled(True)
        self.btn_NoiseRunStop.setDisabled(True)           
        
    @pyqtSlot(object)    
    def Update(self,result1):
        if self.DFrame.mutex.tryLock():
            result = copy(result1)
            self.DFrame.mutex.unlock()
            #Select Channel here -- success
            self.Channel = self.ChannelSelect()
            self.time_curve.setData(result[self.Channel])  
            
    def Update_histo(self,result1):
        if self.CodeFrame.mutex.tryLock():
            result = copy(result1)
            self.CodeFrame.mutex.unlock()
            xdata= result[0]
            xcor = result[1]

            self.p1.setXRange(xcor[0][0],xcor[0][1]) 
            
            self.ADC0_hist_0.setData(xdata[0])
#            self.ADC0_hist_1.setData(xdata[1])
#            self.ADC0_hist_2.setData(xdata[2])
#            self.ADC0_hist_3.setData(xdata[3])
#            self.ADC0_hist_4.setData(xdata[4])
#            self.ADC0_hist_5.setData(xdata[5])
#            self.ADC0_hist_6.setData(xdata[6])
#            self.ADC0_hist_7.setData(xdata[7])

            self.p2.setXRange(xcor[8][0],xcor[8][1]) 
            self.ADC1_hist_0.setData(xdata[8])
#            self.ADC1_hist_1.setData(xdata[9])
#            self.ADC1_hist_2.setData(xdata[10])
#            self.ADC1_hist_3.setData(xdata[11])
#            self.ADC1_hist_4.setData(xdata[12])
#            self.ADC1_hist_5.setData(xdata[13])
#            self.ADC1_hist_6.setData(xdata[14])
#            self.ADC1_hist_7.setData(xdata[15])   
            
            #self.p3.setXRange(xcor[0][0],xcor[0][1]) 
            #self.ADC0_dnl_0.setData(DNL[0])
#            self.ADC0_dnl_1.setData(DNL[1])
#            self.ADC0_dnl_2.setData(DNL[2])
#            self.ADC0_dnl_3.setData(DNL[3])
#            self.ADC0_dnl_4.setData(DNL[4])
#            self.ADC0_dnl_5.setData(DNL[5])
#            self.ADC0_dnl_6.setData(DNL[6])
#            self.ADC0_dnl_7.setData(DNL[7])
            
            #self.p4.setXRange(xcor[8][0],xcor[8][1]) 
            #self.ADC1_dnl_0.setData(DNL[8])
#            self.ADC1_dnl_1.setData(DNL[9])
#            self.ADC1_dnl_2.setData(DNL[10])
#            self.ADC1_dnl_3.setData(DNL[11])
#            self.ADC1_dnl_4.setData(DNL[12])
#            self.ADC1_dnl_5.setData(DNL[13])
#            self.ADC1_dnl_6.setData(DNL[14])
#            self.ADC1_dnl_7.setData(DNL[15])

            #self.p5.setXRange(xcor[0][0],xcor[0][1]) 
            #self.ADC0_inl_0.setData(INL[0])
#            self.ADC0_inl_1.setData(INL[1])
#            self.ADC0_inl_2.setData(INL[2])
#            self.ADC0_inl_3.setData(INL[3])
#            self.ADC0_inl_4.setData(INL[4])
#            self.ADC0_inl_5.setData(INL[5])
#            self.ADC0_inl_6.setData(INL[6])
#            self.ADC0_inl_7.setData(INL[7])
            
            #self.p6.setXRange(xcor[8][0],xcor[8][1]) 
            #self.ADC1_inl_0.setData(INL[8])
#            self.ADC1_inl_1.setData(INL[9])
#            self.ADC1_inl_2.setData(INL[10])
#            self.ADC1_inl_3.setData(INL[11])
#            self.ADC1_inl_4.setData(INL[12])
#            self.ADC1_inl_5.setData(INL[13])
#            self.ADC1_inl_6.setData(INL[14])
#            self.ADC1_inl_7.setData(INL[15])
#            
    def Update_Noise_scan(self,result1): 
        if self.NoiseFrame.mutex.tryLock():
            xdata = copy(result1)
            self.NoiseFrame.mutex.unlock()
                    
            #xdata= result[0]
            #xcor = result[1]
            
            #self.xtalk_chn0.setXRange(xcor[0][0],xcor[0][1])
            self.ADC_xtalk_0.setData(xdata[0])
            
            #self.xtalk_chn1.setXRange(xcor[1][0],xcor[1][1])
            self.ADC_xtalk_1.setData(xdata[1])
            
            #self.xtalk_chn2.setXRange(xcor[2][0],xcor[2][1])
            self.ADC_xtalk_2.setData(xdata[2])
            
            #self.xtalk_chn3.setXRange(xcor[3][0],xcor[3][1])
            self.ADC_xtalk_3.setData(xdata[3])
            
            #self.xtalk_chn4.setXRange(xcor[4][0],xcor[4][1])
            self.ADC_xtalk_4.setData(xdata[4])
            
            #self.xtalk_chn5.setXRange(xcor[5][0],xcor[5][1])
            self.ADC_xtalk_5.setData(xdata[5])
                   
            #self.xtalk_chn6.setXRange(xcor[6][0],xcor[6][1])
            self.ADC_xtalk_6.setData(xdata[6])
            
            #self.xtalk_chn7.setXRange(xcor[7][0],xcor[7][1])
            self.ADC_xtalk_7.setData(xdata[7])
            
            #self.xtalk_chn8.setXRange(xcor[8][0],xcor[8][1])
            self.ADC_xtalk_8.setData(xdata[8])
            
            #self.xtalk_chn9.setXRange(xcor[9][0],xcor[9][1])
            self.ADC_xtalk_9.setData(xdata[9])
            
            #self.xtalk_chn10.setXRange(xcor[10][0],xcor[10][1])
            self.ADC_xtalk_10.setData(xdata[10])
            
            #self.xtalk_chn11.setXRange(xcor[11][0],xcor[11][1])
            self.ADC_xtalk_11.setData(xdata[11])
            
            #self.xtalk_chn12.setXRange(xcor[12][0],xcor[12][1])
            self.ADC_xtalk_12.setData(xdata[12])
            
            #self.xtalk_chn13.setXRange(xcor[13][0],xcor[13][1])
            self.ADC_xtalk_13.setData(xdata[13])
            
            #self.xtalk_chn14.setXRange(xcor[14][0],xcor[14][1])
            self.ADC_xtalk_14.setData(xdata[14])
            
            #self.xtalk_chn15.setXRange(xcor[15][0],xcor[15][1])
            self.ADC_xtalk_15.setData(xdata[15])            
           
            
    def __init__(self, parent = None):
        #----------attributes definition---------#
        self.brd_config = Brd_Config()
        #self.brd_config.sockets_init()
        #self.ADC = COLDADC_Config()
        #self.MAX_PLOT_SIZE = 51200
        self.CHUNK = 256
        self.total_data=[]
        self.Channel = 0
        self.spi_param=[]
        self.ioffset_vrefp = 0
        self.ioffset_vrefn = 0
        self.ioffset_vcmi = 0
        self.ioffset_vcmo = 0
        self.tool = "I2C"
        self.refVolMode = "BJT"
        self.biasCurMode = "BJT"
        #----------------------------------------#        
        super(MainWindow,self).__init__(parent)
        #Create widgets
        self.setWindowTitle("Single COLD ADC TESTER V1.1")
        #resize
        self.resize(1600,600)
        self.ControlTabWidget()
        self.VisualTabWidget()
        
        mainLayout = QGridLayout()
        mainLayout.addWidget(self.ControlTab,0,0)
        
        mainLayout.addWidget(self.VisualTab,0,1)
        #Set Layout
        self.setLayout(mainLayout)        
        self.Change_mode('Normal')   
        #self.fun_SetFedacMode('RMS')
        
## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    #app = QApplication([])
    app = QApplication(sys.argv)
    app.aboutToQuit.connect(app.deleteLater)
    app.setStyle("windows") #Change it to Windows Style
    app.setPalette(QApplication.style().standardPalette())
    window = MainWindow()
    window.show()
    sys.exit(app.exec_()) #Run the main Qt loop #QtGui.QApplication.instance().exec_()            
     

    
