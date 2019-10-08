# -*- coding: utf-8 -*-
"""
Created on Thu Feb 28 12:17:27 2019

@author: JunbinZhang
"""

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
from adc_config import COLDADC_Config
from frame import Frames
from copy import copy
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
        
        #self.chn = chn
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
        chns=[[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
        for i in range(self.CHUNK):
            for j in range(16): #16 channels
                chns[j].append(frames[i].ADCdata[j])
        return chns
#        self.total_data = np.concatenate([self.total_data,channel]) 
#        if len(self.total_data) > self.MAX_PLOT_SIZE:
#            self.total_data = self.total_data[self.CHUNK:]
#        return self.total_data
    def stream(self):
        while self.running():
            self.mutex.lock()
            self.result = self.get_rawdata()
            self.mutex.unlock()
            self.interact.emit(self.result)
            QThread.msleep(1)
        self.sgnFinished.emit()
        
#---------------MainWindow---------------#    
class MainWindow(QWidget):
    def ConnectionChkGroupBox(self):
        self.sCheckgroupBox = QGroupBox("Network check")
        self.status_lbl = QLabel("Network checking")
        font = QFont("Times",12,QFont.Bold)
        self.status_lbl.setFont(font)
        
        self.sCheckbtn = QPushButton("check")
        self.sCheckbtn.clicked.connect(self.sCheckbtn_clicked)
        layout = QVBoxLayout()
        layout.addWidget(self.status_lbl)
        layout.addWidget(self.sCheckbtn)
        
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
        
    def ADCctrlGroupBox(self):
        self.ADCgroupBox = QGroupBox("ADC REG control")
        self.I2CradioButton = QRadioButton("I2C")
        self.I2CradioButton.setChecked(True)
        self.UARTradioButton = QRadioButton("UART")
        self.I2CradioButton.toggled.connect(lambda:self.I2C_UART_switch(self.I2CradioButton))
        self.UARTradioButton.toggled.connect(lambda:self.I2C_UART_switch(self.UARTradioButton))
        
        
        label3 = QLabel("Page")
        self.PageComboBox = QComboBox()
        self.PageComboBox.addItem("1")
        self.PageComboBox.addItem("2")
        self.PageComboBox.addItem("0")
        self.PageComboBox.activated[str].connect(self.Change_I2C_page)
        
        self.ADCRegAddrlineEdit = QLineEdit("hex")
        self.ADCRegVallineEdit = QLineEdit("hex")
        label1 = QLabel("Reg")
        label2 = QLabel("Val")
        self.ADCwriteRegButton = QPushButton("&write")
        self.ADCwriteRegButton.clicked.connect(self.ADCwritebtn_clicked)
       
        self.ADCreadRegButton = QPushButton("&read")
        self.ADCreadRegButton.clicked.connect(self.ADCreadbtn_clicked)
        #Layout
        layout1 = QHBoxLayout()
        layout1.addWidget(self.I2CradioButton)
        layout1.addWidget(self.UARTradioButton)
        layout1.addWidget(label3)
        layout1.addWidget(self.PageComboBox)
        
        layout2 = QHBoxLayout()
        layout2.addWidget(label1)
        layout2.addWidget(self.ADCRegAddrlineEdit)
        layout2.addWidget(label2)
        layout2.addWidget(self.ADCRegVallineEdit)
        
        layout3 = QHBoxLayout()
        layout3.addWidget(self.ADCwriteRegButton)
        layout3.addWidget(self.ADCreadRegButton)
        
        layout = QVBoxLayout()
        layout.addLayout(layout1)
        layout.addLayout(layout2)
        layout.addLayout(layout3)
        #layout.addStretch(1)
        #Set Layout
        self.ADCgroupBox.setLayout(layout)
        #Layout end
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
        
        #layout3.addWidget(self.AcqStartButton)     
        layout = QVBoxLayout()
        layout.addLayout(layout1)
        layout.addLayout(layout2)
        layout.addLayout(layout3)
        layout.addLayout(layout4)
        #Set Layout
        self.FPGAgroupBox.setLayout(layout)   
    def ViewControl(self):
        self.ViewControlgroupBox = QGroupBox("View Control")
        
        #Integer with bounds
        label1 = QLabel("Freq")
        label2 = QLabel("DAC")
        self.freqsp = pg.SpinBox(value=10, suffix='Hz',siPrefix=True, bounds=[10,20], minStep=1,step=1,wrapping=False)
        self.dacsp  = pg.SpinBox(value=10,step=1,int=True,bounds=[0,None],format='0x{value:X}',
                                 regex='(0x)?(?P<number>[0-9a-fA-F]+)$',evalFunc=lambda s: ast.literal_eval('0x'+s))
        
        self.DacSelectbtn = QPushButton("External")
        self.DacSelectbtn.setCheckable(True) 
        
        self.Alignbtn = QPushButton("Align")
        layout1 = QHBoxLayout()
        layout1.addWidget(label1)
        layout1.addWidget(self.freqsp)
        layout1.addWidget(label2)
        layout1.addWidget(self.dacsp)
        
        layout2 = QHBoxLayout()
        layout2.addWidget(self.DacSelectbtn)
        layout2.addWidget(self.Alignbtn)
        
        layout = QVBoxLayout()
        layout.addLayout(layout1)
        layout.addLayout(layout2)
        #Set Layout
        self.ViewControlgroupBox.setLayout(layout)   
    def Visualization(self):
        self.Canvas = pg.GraphicsWindow()        
        self.data_plot = self.Canvas.addPlot(title = "Time Domain")
        self.data_plot.setXRange(0 ,self.CHUNK)
        self.data_plot.showGrid(True, True)
        #chn = self.ChannelSelect()
        self.data_plot.addLegend()
        self.time_curve = self.data_plot.plot(pen=(119,172,48),symbolBrush=(119,172,48),symbolPen='w',symbol='o',symbolSize=2, name = "Time Domain Audio")
        
        # create a plot for the frequency domain data
        self.Canvas.nextRow()
        self.fft_plot = self.Canvas.addPlot(title="Frequency Domain") 
        self.fft_plot.addLegend()
        self.fft_plot.showGrid(True, True)
        self.fft_plot.enableAutoRange('xy',True)
        self.fft_curve = self.fft_plot.plot(pen='y', name = "Power Spectrum")
    #----------------------Action-------------------#    
    @pyqtSlot()    
    def sCheckbtn_clicked(self):
        if self.brd_config.check_board() == True:
            self.status_lbl.setText("Success")
            self.status_lbl.setStyleSheet("QLabel{color:green}");
        else:
            self.status_lbl.setText("Failed")
            self.status_lbl.setStyleSheet("QLabel{color:red}");
            
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
        
    def Change_mode(self,text):
        if text == "Normal":
            self.brd_config.Acq_mode('normal')
        elif text == "F_Suffix":
            val = int(self.SuffixlineEdit.text(),0)
            self.brd_config.Acq_mode('fake1',val)
        elif text == "F_ChnID":
            self.brd_config.Acq_mode('fake2')
            
    def Change_I2C_page(self,text):    
        if text == "1":
            self.brd_config.I2C_DEV(1)
        elif text == "2":
            self.brd_config.I2C_DEV(2)
        elif text == "0":
            self.brd_config.I2C_DEV(0)
            
    def ChannelSelect(self):
        val = self.ChnSlider.value()
        return val
    #Setup for I2C or UART tool
    def I2C_UART_switch(self,rbtn):
        if rbtn.isChecked() == True:
            if rbtn.text() == "I2C":
                self.PageComboBox.setEnabled(True)
                self.brd_config.i2c_uart_switch("I2C")
                self.tool = "I2C"

            elif rbtn.text()=="UART":
                self.PageComboBox.setDisabled(True)
                #force to select page 1
                self.brd_config.I2C_DEV(1)
                self.brd_config.i2c_uart_switch("UART")
                self.tool = "UART"
    @pyqtSlot() 
    def ADCwritebtn_clicked(self):
        reg = int(self.ADCRegAddrlineEdit.text(),0)
        reg1 = [reg,0xff]
        val = int(self.ADCRegVallineEdit.text(),0)
        self.ADC.ADC_reg_write(self.tool,reg1,val)
    
    @pyqtSlot()
    def ADCreadbtn_clicked(self):
        reg = int(self.ADCRegAddrlineEdit.text(),0)
        reg1 = [reg,0xff]
        string = self.ADC.ADC_reg_read(self.tool,reg1)
        self.ADCRegVallineEdit.setText(string)     
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
        
    @pyqtSlot(object)    
    def Update(self,result1):
        if self.DFrame.mutex.tryLock():
            result = copy(result1)
            self.DFrame.mutex.unlock()
            
            #Select Channel here -- success
            self.Channel = self.ChannelSelect()
            self.time_curve.setData(result[self.Channel])       
    def __init__(self, parent = None):
        #----------attributes definition---------#
        self.brd_config = Brd_Config()
        self.ADC = COLDADC_Config()
        #self.MAX_PLOT_SIZE = 51200
        self.CHUNK = 128
        self.total_data=[]
        self.Channel = 0
        self.tool = "I2C"
        #----------------------------------------#        
        super(MainWindow,self).__init__(parent)
        #Create widgets
        self.setWindowTitle("Single COLD ADC TESTER V1.0")
        #resize
        self.resize(1200,600)
        self.ConnectionChkGroupBox()
        self.ADCctrlGroupBox()
        self.FPGActrlGroupBox()
        self.Visualization()
        self.MessageGroupBox()
        self.ViewControl()
        self.ChannelGroupBox()
        
        mainLayout = QGridLayout()
        mainLayout.addWidget(self.MsggroupBox,0,0,4,1)
        #mainLayout.addWidget(self.sCheckgroupBox,0,1)
        mainLayout.addWidget(self.ADCgroupBox,0,1)
        mainLayout.addWidget(self.FPGAgroupBox,1,1)
        mainLayout.addWidget(self.ViewControlgroupBox,2,1)
        mainLayout.addWidget(self.ChngroupBox,3,1)
        mainLayout.addWidget(self.Canvas,0,2,4,1)
        #Set Layout
        self.setLayout(mainLayout)        
        self.Change_mode('Normal')    
        
## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    app = QApplication([])
    app.setStyle("windows") #Change it to Windows Style
    app.setPalette(QApplication.style().standardPalette())
    window = MainWindow()
    window.show()
    sys.exit(app.exec_()) #Run the main Qt loop #QtGui.QApplication.instance().exec_()            
     

    
