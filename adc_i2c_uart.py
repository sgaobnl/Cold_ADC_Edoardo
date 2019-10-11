# -*- coding: utf-8 -*-
"""
Created on Tue Jan 22 16:47:52 2019

@author: JunbinZhang
"""
from udp import UDP
from fpga_reg import FPGA_REG
#from adc_reg import ADC_REG
from bit_op import Bit_Op
import time
#import sys
class COLDADC_tool:
    
    def config_tool(self,tool):
        #self.udp.write(self.fpga_reg.MASTER_RESET,1)
        #time.sleep(0.01)
        if(tool == 'uart' or tool == 'UART'):
            self.uart_flag = True
            self.udp.write(self.fpga_reg.I2C_UART_SEL,1)
#            print (self.uart_flag)
        else:
            self.udp.write(self.fpga_reg.I2C_UART_SEL,0)
            self.uart_flag = False
            
    def hard_reset(self):
        self.udp.write(self.fpga_reg.MASTER_RESET,0)
        time.sleep(0.5)
        self.udp.write(self.fpga_reg.MASTER_RESET,1)  
        
        
    def I2C_read(self,chip_id,page,addr):
        if (self.uart_flag):
            if (page ==2):
                if (addr == 1):
                    ladr = ((0x80+49)&0xff)<<20  
                elif (addr == 2):
                    ladr = ((0x80+48)&0xff)<<20  
                elif (addr == 3):
                    ladr = ((0x80+50)&0xff)<<20
                else: 
                    print ("invaid address")
                    ladr = ((0x80+0x7f)&0xff)<<20
            else:
                ladr = (addr&0xff)<<20          
            ldata = (0x00&0xff)<<12 #useless
            lwen = (0x00&0x01)<<7 #read 
            lchip_id = (chip_id&0x07)<<8
            data = (ladr&0x0ff00000) + (ldata&0x000ff000) + (lchip_id&0x700) + (lwen&0x80)
            par_cnt = 0
            for i in range(32):
                if (data>>i)&0x01 == 0x01:
                    par_cnt = par_cnt + 1
            if par_cnt%2 == 1:
                par_chk = 0
            else:
                par_chk =1
            data = ((par_chk<<28)&0x10000000) + data
            self.udp.write_reg(2, data + 0x01)
            vreg = self.udp.read_reg(3)
            rdadr = (vreg>>16)&0xff
            rddata = (vreg>>8)&0xff
#            print (hex(chip_id), hex(vreg), hex(rdadr), hex(rddata))
            time.sleep(0.01)
            self.udp.write_reg(2, data + 0x00)
            temp = rddata
        else: 
            #load address
            self.udp.write(self.fpga_reg.i2c_rw,1) #read
            #load data
            self.udp.write(self.fpga_reg.i2c_chip_id,chip_id)
            #load byte count
            self.udp.write(self.fpga_reg.i2c_page,page)
            
            self.udp.write(self.fpga_reg.i2c_reg_addr,addr)
            #run strobe
            self.udp.write(self.fpga_reg.i2c_ena,1)
            time.sleep(0.01)
            check_done =1
            while(check_done):
                check_done = self.udp.read(self.fpga_reg.i2c_busy)
            #print(self.udp.read(self.fpga_reg.i2c_ack_error))
            temp = self.udp.read(self.fpga_reg.i2c_data_rd)
            self.udp.write(self.fpga_reg.i2c_ena,0)
        
        return temp

    def I2C_write(self,chip_id,page,addr,data):
        if (self.uart_flag):
            if (page ==2):
                if (addr == 1):
                    ladr = ((0x80+49)&0xff)<<20  
                elif (addr == 2):
                    ladr = ((0x80+48)&0xff)<<20  
                elif (addr == 3):
                    ladr = ((0x80+50)&0xff)<<20
                else: 
                    print ("invaid address")
                    ladr = ((0x80+0x7f)&0xff)<<20
            else:
                ladr = (addr&0xff)<<20            
            ldata = (data&0xff)<<12 
            lwen = (0x01&0x01)<<7 #read 
            lchip_id = (chip_id&0x07)<<8
            data_w = (ladr&0x0ff00000) + (ldata&0x000ff000) + (lchip_id&0x700) + (lwen&0x80)
            par_cnt = 0
            for i in range(32):
                if (data>>i)&0x01 == 0x01:
                    par_cnt = par_cnt + 1
            if par_cnt%2 == 1:
                par_chk = 0
            else:
                par_chk =1
            data_w = ((par_chk<<28)&0x10000000) + data_w
            self.udp.write_reg(2, data_w + 0x01)
#            print (hex(chip_id), hex(addr), hex(data), hex(data_w))
            time.sleep(0.01)
            self.udp.write_reg(2, data_w + 0x00)
        else: 
            #load address
            self.udp.write(self.fpga_reg.i2c_rw,0) #write
            #load data
            self.udp.write(self.fpga_reg.i2c_chip_id,chip_id)
            #load byte count
            self.udp.write(self.fpga_reg.i2c_page,page)
            
            self.udp.write(self.fpga_reg.i2c_reg_addr,addr)
            
            self.udp.write(self.fpga_reg.i2c_data_wr,data)
            #run strobe
            self.udp.write(self.fpga_reg.i2c_ena,1)
            time.sleep(0.01)
            check_done =1
            while(check_done):
                check_done = self.udp.read(self.fpga_reg.i2c_busy)
            #print("DONE")           
            self.udp.write(self.fpga_reg.i2c_ena,0)
            self.udp.write(self.fpga_reg.i2c_ena,0)

    def I2C_write_checked(self,chip_id,page,reg,data):
        for i in range(10):
            self.I2C_write(chip_id, page, reg, data)
            time.sleep(0.001)
            rdata = self.I2C_read(chip_id,page,reg)
            if data == rdata:
                break
            else:
                time.sleep(0.001)
        else:
            print ("readback value is different from written data, %d, %x, %x"%(reg, data, rdata))


        
    #ADC adc write with bit mask
    def ADC_I2C_write(self,chip_id,page,reg,data):
        regNum = reg[0] #register number
        mask   = reg[1]
        if mask == 0xff:
            self.I2C_write(chip_id,page,regNum,data)
            #print("regNum=0x%x"%regNum)
        else:
            #read the register and get original value
            temp = self.I2C_read(chip_id,page,regNum)
            #get mask bits
            index,size = self.bitop.mask(mask)
            #generate a new value
            val = self.bitop.set_bits(temp,index,size,data)
            #write again
            self.I2C_write(chip_id,page,regNum,val)
    #ADC read with bit mask
    def ADC_I2C_read(self,chip_id,page,reg):
        regNum = reg[0] #register number
        mask   = reg[1]
        #read the register to get original value
        temp = self.I2C_read(chip_id,page,regNum)
        if mask == 0xff:
            return temp
        else:
            #get mask bits
            index,size = self.bitop.mask(mask)
            return self.bitop.get_bits(temp,index,size)
    
    
    def ADC_I2C_write_checked(self,chip_id,page,reg,data):
        for i in range(10):
            self.ADC_I2C_write(chip_id, page, reg, data)
            time.sleep(0.001)
            rdata = self.ADC_I2C_read(chip_id,page,reg)
            if data == rdata:
                break
            else:
                time.sleep(0.001)
        else:
            print ("readback value is different from written data, %d, %x, %x"%(reg[0], data, rdata))
            #sys.exit()  
        
#    def write_reg_checked (self,reg, data, femb_addr = None):
#        for i in range(10):
#            self.write_reg(reg, data, femb_addr)
#            time.sleep(0.001)
#            rdata = self.read_reg(reg, femb_addr)
#            rdata = self.read_reg(reg, femb_addr)#twice
#            if data == rdata:
#                break
#            else:
#                time.sleep(i+0.001)
#        else: #the else clause executes if the loop iteration completes normally
#            print ("readback value is different from written data, %d, %x, %x"%(reg, data, rdata))
#            sys.exit()        
        
        
    def UART_write(self,chip_id,addr,data):
        #LSB-----------------------------MSB
        #WRB  ChipID[1:4] data[5:12] address[13:20] parity
        WRB = 1
        chip_id_in = self.bitop.reverseBit(chip_id,4) #MSB first in VHDL
        data_in    = self.bitop.reverseBit(data,8) #MSB first in VHDL
        addr_in    = self.bitop.reverseBit(addr,8)
        
        #temp = (addr << 13) + (data << 5) + (chip_id << 1) + WRB #chip ID = 0
        temp = (WRB << 21) + (chip_id_in << 17) + (data_in << 9)+ (addr_in << 1)
        #val = self.bitop.reverseBit(temp,22) #MSB first in VHDL
        #load data
        self.udp.write(self.fpga_reg.uart_tx_data,temp)
        #run strobe
        self.udp.write(self.fpga_reg.uart_tx_ena,1)
        check_done = 1
        while(check_done):
            check_done = self.udp.read(self.fpga_reg.uart_tx_busy)       
        time.sleep(0.01)
        self.udp.write(self.fpga_reg.uart_tx_ena,0)

    
    def UART_read(self,chip_id, addr):
        #LSB-----------------------------MSB
        #WRB  ChipID[1:4] data[5:12] address[13:20] parity  
        WRB = 0
        chip_id_in = self.bitop.reverseBit(chip_id,4) #MSB first in VHDL
        addr_in    = self.bitop.reverseBit(addr,8)
        
        temp = (WRB << 21) + (chip_id_in << 17) + (addr_in << 1)
        
#        temp = (addr << 13) + (chip_id << 1) + WRB #chip ID = 0
#        val = self.bitop.reverseBit(temp,22) #MSB first in VHDL
        #load data
        self.udp.write(self.fpga_reg.uart_tx_data,temp)
        #run strobe
        self.udp.write(self.fpga_reg.uart_tx_ena,1)
        check_done = 1
        while(check_done):
            check_done = self.udp.read(self.fpga_reg.uart_tx_busy)       
        time.sleep(0.01)
        self.udp.write(self.fpga_reg.uart_tx_ena,0)       
        
        check_done =1
        while(check_done):
            check_done = self.udp.read(self.fpga_reg.uart_rx_busy)
        temp1 = self.udp.read(self.fpga_reg.uart_rx_data)  
        temp1 = (temp1 >> 9) & 0xff
        val = self.bitop.reverseBit(temp1,8)
        return val      
    
    #ADC uart write with bit mask
    def ADC_UART_write(self,reg,data):
        regNum = reg[0] #register number
        mask   = reg[1]
        if mask == 0xff:
            self.UART_write(regNum,data)
        else:
            #read the register and get original value
            temp1 = (self.UART_read(regNum) & 0xff00) >> 8
            temp = self.bitop.reverseBit(temp1,8)
            #get mask bits
            index,size = self.bitop.mask(mask)
            #generate a new value
            val = self.bitop.set_bits(temp,index,size,data)
            #write again
            self.UART_write(regNum,val)
    #ADC uart read with bit mask
    def ADC_UART_read(self,reg):
        regNum = reg[0] #register number
        mask   = reg[1]
        #read the register to get original value
        temp1 = (self.UART_read(regNum) & 0xff00) >> 8
        temp = self.bitop.reverseBit(temp1,8)
        if mask == 0xff:
            return temp
        else:
            #get mask bits
            index,size = self.bitop.mask(mask)
            return self.bitop.get_bits(temp,index,size)    
        

        
#    def write_reg_checked (self,reg, data, femb_addr = None):
#        for i in range(10):
#            self.write_reg(reg, data, femb_addr)
#            time.sleep(0.001)
#            rdata = self.read_reg(reg, femb_addr)
#            rdata = self.read_reg(reg, femb_addr)#twice
#            if data == rdata:
#                break
#            else:
#                time.sleep(i+0.001)
#        else: #the else clause executes if the loop iteration completes normally
#            print ("readback value is different from written data, %d, %x, %x"%(reg, data, rdata))
#            sys.exit()
    #ADC write function that 
#    def ADC_reg_write(self,tool,reg,data):
#        #select tool
#        #self.config_tool(tool)
#        if tool == 'uart' or 'UART':
#            self.ADC_UART_write(reg,data)
#        else:
#            self.ADC_I2C_write(reg,data)
#    #ADC read function
#    def ADC_reg_read(self,tool,reg):
#        #select tool
#        #self.config_tool(tool)
#        if tool == 'uart' or 'UART':
#            return self.ADC_UART_read(reg)
#        else:
#            return self.ADC_I2C_read(reg)
    def __init__(self):
        self.uart_flag = False
        self.udp = UDP()
        #self.adc_reg = ADC_REG()
        self.fpga_reg = FPGA_REG()
        self.bitop = Bit_Op()


#if __name__ == '__main__':
#    ADC = COLDADC_tool()
#    #ADC.ADC_I2C_write(0,1,[0x80,0xff],0x55)
#    #red=ADC.ADC_I2C_read(0,1,[0x81,0xff])
#    
#    ADC.config_tool("I2C")
#    ADC.I2C_write(0,1,0x8a,0xaa)
#    red = ADC.I2C_read(0,1,0x8a)
#    print(hex(red))
#    
#    ADC.config_tool("uart")
#    #ADC.UART_write(0,0x8c,0xaf)
#    red=ADC.UART_read(0,0x8a)
#    print(hex(red))
    #ADC.ADC_UART_write([0x80,0xff],0x55)    
#udp = UDP()
#def write_reg(self, reg, data, femb_addr = None)
#udp.write_reg(0x4,0xffffffff);
#time.sleep(1)
#print(hex(udp.read_reg(0x101)))
#class ADC_CONFIG:
#    def __init__(self):
#        self.udp = UDP()
