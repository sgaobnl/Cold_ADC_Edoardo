# -*- coding: utf-8 -*-
"""
Created on Tue Feb  5 16:08:39 2019

@author: JunbinZhang
"""

class FPGA_REG:
    def __init__(self):
        
        self.SYS_RESET = [0x0,0x1]    # 1 bit, system reset Auto reset
        self.FE_RESET  = [0x0,0x2]    # 1 bit, FE reset Auto reset
        
        self.MASTER_RESET = [0x1,0x1] # 1 bit, ADC reset.
        self.I2C_UART_SEL = [0x1,0x2] # 1 bit, I2C or UART, 1-> UART, 0-> I2C
        
        self.udp_fifo_clr = [0x1,0x4] # 1 bit, Clear UDP fifo
        
        self.uart_tx_ena  = [0x2,0x1]      # 1  bit,  uart tx enable
        self.uart_tx_data = [0x2,0x3FFFFE] # 21 bits, uart tx data
        
        self.uart_rx_data = [0x3,0xFFFFF8] # 21 bits, uart rx data
        self.uart_tx_busy = [0x3,0x4]      # 1 bit, tx busy
        self.uart_rx_busy = [0x3,0x2]      # 1 bit, rx busy
        self.uart_rx_error = [0x3,0x1]      # 1 bits, uart rx error
        
        self.i2c_ena     = [0x4,0x1] #1 bit
        self.i2c_rw      = [0x4,0x100] # 1bit
        self.i2c_page    = [0x4,0xe00] # 3bit
        self.i2c_chip_id = [0x4,0xf000] # 4 bit
        self.i2c_reg_addr= [0x4,0xff000000]
        self.i2c_data_wr = [0x4,0xff0000]
        
        self.i2c_data_rd = [0x6,0xff]
        self.i2c_ack_error = [0x9,0x2]
        self.i2c_busy      = [0x9,0x1]
        
        self.MUX_ADDR     = [0x7,0x7] # 3 bits
        self.WRITE_SPI    = [0x8,0x1] # 1 bit
        
        self.UDP_FRAME_SIZE  = [0xa,0xFFF]
        
        self.ADC_TST_PATT_EN = [0xb,0x1]
        self.ADC_TST_PATT_MODE=[0xb,0x6]
        self.ADC_TST_PATT    = [0xb,0xFFFF0000] # 16 bits
        self.ACQ_START      = [0xf,0xffffffff]
        
        self.FPGA_TP_EN     = [0xc,0x1]
        self.ASIC_TP_EN     = [0xc,0x2]
        self.INT_TP_EN      = [0xc,0x4]    
        self.FPGA_DAC_SELECT = [0xc,0x8] # 1 bit       
        self.EXT_TP_EN      =  [0xc,0x10] #000
        #self.TP_EXT_GEN     = [0xc,0x10]
        #self.TP_INT_GEN     = [0xc,0x20]
        
        self.PULSE_WIDTH    = [0xd,0xFFFFFFFF]
        
        self.TP_AMPL        = [0xe,0x3F]
        self.TP_DLY         = [0xe,0xFF00]
        self.TP_FREQ        = [0xe,0xFFFF0000]
        
        self.word_order     = [0x10,0x7]
        #self.word_order     = 0x10
        self.cots_adc_start = [0x11,0x1] #start acquisition
        self.cost_adc_data  = [0x12,0xfff]
        self.cots_adc_busy  = [0x13,0x1] #busy
        
        self.BRD_V          = [0x101,0xffffffff]
        
        self.SPI_WRITE_BASE = 0x200
        self.SPI_READ_BASE  = 0x250