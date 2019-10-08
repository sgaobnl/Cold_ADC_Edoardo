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
        self.adc_method = ADC_method()
        self.hist_chns = [[0]*4096,[0]*4096,[0]*4096,[0]*4096,[0]*4096,[0]*4096,[0]*4096,[0]*4096,[0]*4096,[0]*4096,[0]*4096,[0]*4096,[0]*4096,[0]*4096,[0]*4096,[0]*4096]
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
            self.result= self.adc_method.ramp_dnl_inl_cali(self.hist_chns)
            
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
        
        
        self.btn_CodeScanStart = QPushButton("CodeScanStart")
        self.btn_CodeScanStart.clicked.connect(self.btn_CodeScanStart_clicked)
        self.btn_CodeScanStop = QPushButton("CodeScanStop")
        self.btn_CodeScanStop.setDisabled(True)
        self.btn_CodeScanStop.clicked.connect(self.btn_CodeScanStop_clicked)        
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
        
        layout5 = QHBoxLayout()
        layout5.addWidget(self.btn_CodeScanStart)
        layout5.addWidget(self.btn_CodeScanStop)            
        #layout3.addWidget(self.AcqStartButton)     
        layout = QVBoxLayout()
        layout.addLayout(layout1)
        layout.addLayout(layout2)
        layout.addLayout(layout3)
        layout.addLayout(layout4)
        layout.addLayout(layout5)
        #Set Layout
        self.FPGAgroupBox.setLayout(layout)   
        
    def ViewControl(self):
        self.ViewControlgroupBox = QGroupBox("View Control")
        #Integer with bounds
 
        lbl_word_order = QLabel("Word order")
        self.sp_word_order = QSpinBox()
        self.sp_word_order.setRange(0,7)
        self.sp_word_order.setValue(0)
        self.sp_word_order.setSingleStep(1)
        self.sp_word_order.valueChanged.connect(self.fun_wordorder)
        
        layout3 = QHBoxLayout()
        layout3.addWidget(lbl_word_order)
        layout3.addWidget(self.sp_word_order)     
        
        layout = QVBoxLayout()
#        layout.addLayout(layout1)
#        layout.addLayout(layout2)
        layout.addLayout(layout3)
        #Set Layout
        self.ViewControlgroupBox.setLayout(layout)   
    #def FEcontrol_Tab(self):
    #---------------------------a part of show----------------------------#    
    def ControlTabWidget(self):
        self.ControlTab = QTabWidget()
        #-------------------------tab1----------------------------#
        tab1 = QWidget()
        
        gbox_SpiCtrl = QGroupBox("spi control")
        lbl_fedacmode = QLabel("DAC_MODE")
        self.cbox_fedacmode = QComboBox()
        self.cbox_fedacmode.addItem("RMS")
        self.cbox_fedacmode.addItem("FDAC")
        self.cbox_fedacmode.addItem("ADAC")
        self.cbox_fedacmode.activated[str].connect(self.fun_SetFedacMode)
        
        lbl_fe_baseline = QLabel("Baseline")
        self.cbox_fe_baseline = QComboBox()
        self.cbox_fe_baseline.addItem("900mV")
        self.cbox_fe_baseline.addItem("200mV")
        self.cbox_fe_baseline.activated[str].connect(self.fun_fe_baseline)
        
        lbl_fe_gain = QLabel("Gain")
        self.cbox_fe_gain = QComboBox()
        self.cbox_fe_gain.addItem("14mV/fC")
        self.cbox_fe_gain.addItem("4.7mV/fC")
        self.cbox_fe_gain.addItem("7.8mV/fC")
        self.cbox_fe_gain.addItem("25mV/fC")
        self.cbox_fe_gain.activated[str].connect(self.fun_fe_gain)
        
        lbl_fe_peaktime = QLabel("Peaktime")
        self.cbox_fe_peaktime = QComboBox()
        self.cbox_fe_peaktime.addItem("2us")
        self.cbox_fe_peaktime.addItem("0.5us")
        self.cbox_fe_peaktime.addItem("1us")
        self.cbox_fe_peaktime.addItem("3us")
        self.cbox_fe_peaktime.activated[str].connect(self.fun_fe_peaktime)
        
        lbl_fe_mon = QLabel("Mon")
        self.cbox_fe_mon = QComboBox()
        self.cbox_fe_mon.addItem("off")
        self.cbox_fe_mon.addItem("on")
        self.cbox_fe_mon.activated[str].connect(self.fun_fe_mon)
        
        lbl_fe_buffer = QLabel("Buffer")
        self.cbox_fe_buffer = QComboBox()
        self.cbox_fe_buffer.addItem("off")
        self.cbox_fe_buffer.addItem("on")
        self.cbox_fe_buffer.activated[str].connect(self.fun_fe_buffer)
        
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

        self.btn_fe_spi_config = QPushButton("spi write")
        self.btn_fe_spi_config.clicked.connect(self.fun_FeSpiConfig_clicked) 
        
        SpiCtrl_layout = QGridLayout()
        
        SpiCtrl_layout.addWidget(lbl_fedacmode,0,0)
        SpiCtrl_layout.addWidget(self.cbox_fedacmode,0,1)
        
        SpiCtrl_layout.addWidget(lbl_fe_baseline,1,0)
        SpiCtrl_layout.addWidget(self.cbox_fe_baseline,1,1) 
        
        SpiCtrl_layout.addWidget(lbl_fe_gain,2,0)
        SpiCtrl_layout.addWidget(self.cbox_fe_gain,2,1)
        
        SpiCtrl_layout.addWidget(lbl_fe_peaktime,3,0)
        SpiCtrl_layout.addWidget(self.cbox_fe_peaktime,3,1)        
        
        SpiCtrl_layout.addWidget(lbl_fe_mon,4,0)
        SpiCtrl_layout.addWidget(self.cbox_fe_mon,4,1)

        SpiCtrl_layout.addWidget(lbl_fe_buffer,5,0)
        SpiCtrl_layout.addWidget(self.cbox_fe_buffer,5,1)
        
        SpiCtrl_layout.addWidget(lbl_fe_coupling,6,0)
        SpiCtrl_layout.addWidget(self.cbox_fe_coupling,6,1)
             
        SpiCtrl_layout.addWidget(lbl_fe_leakage,7,0)
        SpiCtrl_layout.addWidget(self.cbox_fe_leakage,7,1)        

        SpiCtrl_layout.addWidget(lbl_fe_mon_type,8,0)
        SpiCtrl_layout.addWidget(self.cbox_fe_mon_type,8,1)  
        
        SpiCtrl_layout.addWidget(lbl_asic_dac,9,0)
        SpiCtrl_layout.addWidget(self.sp_asic_dac,9,1)          

        SpiCtrl_layout.addWidget(self.btn_fe_spi_config,10,0)          
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
        tab1_layout.addWidget(gbox_SpiCtrl,0,0,2,1)
        tab1_layout.addWidget(gbox_pulse_param,0,1,1,1)        
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
        gbox_config.setLayout(config_layout)
        
        gbox_ref = QGroupBox("Reference")
        
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
        
        ref_layout = QGridLayout()
        ref_layout.addWidget(lbl_refVol,0,0)
        ref_layout.addWidget(self.cbox_refvol,0,1)
        ref_layout.addWidget(lbl_biasCur,0,2)
        ref_layout.addWidget(self.cbox_biascur,0,3)
        
        ref_layout.addWidget(lbl_VREFP,1,0)
        ref_layout.addWidget(self.ledit_VREFP,1,1)
        ref_layout.addWidget(lbl_ioffset_vrefp,1,2)
        ref_layout.addWidget(self.cbox_ioffset_vrefp,1,3)        
        
        ref_layout.addWidget(lbl_VREFN,2,0)
        ref_layout.addWidget(self.ledit_VREFN,2,1)
        ref_layout.addWidget(lbl_ioffset_vrefn,2,2)
        ref_layout.addWidget(self.cbox_ioffset_vrefn,2,3) 

        ref_layout.addWidget(lbl_VCMI,3,0)
        ref_layout.addWidget(self.ledit_VCMI,3,1)
        ref_layout.addWidget(lbl_ioffset_vcmi,3,2)
        ref_layout.addWidget(self.cbox_ioffset_vcmi,3,3)               
        
        ref_layout.addWidget(lbl_VCMO,4,0)
        ref_layout.addWidget(self.ledit_VCMO,4,1)
        ref_layout.addWidget(lbl_ioffset_vcmo,4,2)
        ref_layout.addWidget(self.cbox_ioffset_vcmo,4,3)            
        
        ref_layout.addWidget(self.btn_SetRefVol,5,1)
        ref_layout.addWidget(self.btn_Setoffset,5,3)
        
        
        ref_layout.addWidget(lbl_ibuff0,6,0)
        ref_layout.addWidget(self.ledit_ibuff0,6,1)
        
        ref_layout.addWidget(lbl_ibuff1,7,0)
        ref_layout.addWidget(self.ledit_ibuff1,7,1)
        
        ref_layout.addWidget(lbl_idac0,6,2)
        ref_layout.addWidget(self.ledit_idac0,6,3)
        
        ref_layout.addWidget(lbl_idac1,7,2)
        ref_layout.addWidget(self.ledit_idac1,7,3)   
             
        ref_layout.addWidget(self.btn_Setibuff,8,1)          
        ref_layout.addWidget(self.btn_Setidac,8,3)
        
        ref_layout.addWidget(lbl_ref_monitor,9,0) 
        ref_layout.addWidget(self.ledit_refmon_H,9,1)
        ref_layout.addWidget(self.ledit_refmon_L,9,2)

        ref_layout.addWidget(lbl_ref_powerdone,10,0) 
        ref_layout.addWidget(self.ledit_refpwd_H,10,1)
        ref_layout.addWidget(self.ledit_refpwd_L,10,2)
        
        ref_layout.addWidget(self.btn_SetrefMon,9,3)        
        ref_layout.addWidget(self.btn_Setpwrdown,10,3) 
        gbox_ref.setLayout(ref_layout)
        
        gbox_debug = QGroupBox("debug")
        
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
        self.btn_autocali = QPushButton("AutoCali")
        self.btn_autocali.clicked.connect(self.btn_autocali_clicked)
        self.lbl_calistatus = QLabel("Process...")
        
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
        
        debug_layout.addWidget(self.btn_autocali,3,2)
        debug_layout.addWidget(self.lbl_calistatus,3,3)
        
        gbox_debug.setLayout(debug_layout)
    
    
        gbox_converter = QGroupBox("Converter Config")
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
        tab3_layout.addWidget(self.FPGAgroupBox,0,0)
        tab3_layout.addWidget(self.ViewControlgroupBox,0,1)
        tab3_layout.addWidget(self.ChngroupBox,1,0)
        
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
        self.VisualTab.addTab(tab1,"&Wave/FFT")
        self.VisualTab.addTab(tab2,"DNL/INL")
    #----------------------Action-------------------#    
    #---------FE control--------#
    def fun_SetFedacMode(self,text):
        self.brd_config.fe_pulse_config(text)
        self.brd_config.fe_config(text)    
    
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
        
    def fun_testdatamode(self,text):
        self.brd_config.adc_test_data_mode(text)
#        if text == "Normal":
#            self.
#        elif text == "Test Pattern":
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
    def btn_autocali_clicked(self):
        self.lbl_calistatus.setText("Process")
        self.brd_config.adc_autocali()
        self.lbl_calistatus.setText("Done")
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
                #force to select page 1
                #self.brd_config.I2C_DEV(1)
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
        #reg1 = [reg,0xff]
        string = self.brd_config.adc_read_reg(reg)        
        self.ledit_AdcRegVal.setText(string)     
        
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
            DNL = result[1]
            INL= result[2]
            xcor = result[3]
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
            
            self.p3.setXRange(xcor[0][0],xcor[0][1]) 
            self.ADC0_dnl_0.setData(DNL[0])
#            self.ADC0_dnl_1.setData(DNL[1])
#            self.ADC0_dnl_2.setData(DNL[2])
#            self.ADC0_dnl_3.setData(DNL[3])
#            self.ADC0_dnl_4.setData(DNL[4])
#            self.ADC0_dnl_5.setData(DNL[5])
#            self.ADC0_dnl_6.setData(DNL[6])
#            self.ADC0_dnl_7.setData(DNL[7])
            
            self.p4.setXRange(xcor[8][0],xcor[8][1]) 
            self.ADC1_dnl_0.setData(DNL[8])
#            self.ADC1_dnl_1.setData(DNL[9])
#            self.ADC1_dnl_2.setData(DNL[10])
#            self.ADC1_dnl_3.setData(DNL[11])
#            self.ADC1_dnl_4.setData(DNL[12])
#            self.ADC1_dnl_5.setData(DNL[13])
#            self.ADC1_dnl_6.setData(DNL[14])
#            self.ADC1_dnl_7.setData(DNL[15])

            self.p5.setXRange(xcor[0][0],xcor[0][1]) 
            self.ADC0_inl_0.setData(INL[0])
#            self.ADC0_inl_1.setData(INL[1])
#            self.ADC0_inl_2.setData(INL[2])
#            self.ADC0_inl_3.setData(INL[3])
#            self.ADC0_inl_4.setData(INL[4])
#            self.ADC0_inl_5.setData(INL[5])
#            self.ADC0_inl_6.setData(INL[6])
#            self.ADC0_inl_7.setData(INL[7])
            
            self.p6.setXRange(xcor[8][0],xcor[8][1]) 
            self.ADC1_inl_0.setData(INL[8])
#            self.ADC1_inl_1.setData(INL[9])
#            self.ADC1_inl_2.setData(INL[10])
#            self.ADC1_inl_3.setData(INL[11])
#            self.ADC1_inl_4.setData(INL[12])
#            self.ADC1_inl_5.setData(INL[13])
#            self.ADC1_inl_6.setData(INL[14])
#            self.ADC1_inl_7.setData(INL[15])
#            
            
            
            #self.ADC1_hist.setData(result[8])
    def __init__(self, parent = None):
        #----------attributes definition---------#
        self.brd_config = Brd_Config()
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
        self.setWindowTitle("Single COLD ADC TESTER V1.0")
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
    app = QApplication([])
    app.setStyle("windows") #Change it to Windows Style
    app.setPalette(QApplication.style().standardPalette())
    window = MainWindow()
    window.show()
    sys.exit(app.exec_()) #Run the main Qt loop #QtGui.QApplication.instance().exec_()            
     

    
