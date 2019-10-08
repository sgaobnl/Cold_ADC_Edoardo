# -*- coding: utf-8 -*-
"""
Created on Wed Apr 11 14:41:37 2018

@author: JunbinZhang
"""
"""The front-end ASIC includes 16 8-bit channel specific registers that only affect
    the behavior of one specific channel."""
class FE_chn:
    def fe_chn_reg(self,sts=0,snc=0,sg=0,st=0,smn=0,sbf=0):
        #STS SNC SG0 SG1 ST0 ST1 SMN SBF
        #LSB-------------------------MSB
        temp = ((sbf & 0x01) << 7) + ((smn & 0x01)<<6) + ((st & 0x03)<<4) + ((sg & 0x03)<<2)+ ((snc & 0x01)<<1) + (sts & 0x01)
        self.chn_reg = self.reverseBit(temp,8)
    def reverseBit(self, dat, n):
    #n means how many bits you want.
        res = 0
        for i in range(n):
            res = res << 1
            res = res | (dat & 1)
            dat = dat >> 1
        return res
    def __init__(self):
        self.chn_reg = 0
"""And 2 8-bit global registers that affect all channels.
    Thus, there are 18*8 = 144bits for one FE ASIC."""
class FE_glbl:
    #This function Maps the global registers of FE ASIC
    def fe_glbl_reg(self,sdc=0,slkh=0,s16=0,stb=0,slk=0,sdac=0,sdacsw=0):
        #-----------global register 1-----------#
        #RES RES SDC SLKH S16 STB STB1 SLK
        #LSB---------------------------MSB
        #-----------global register 2-----------#
        #SDAC0 SDAC1 SDAC2 SDAC3 SDAC4 SDAC5 SDACSW1 SDACSW2
        #LSB------------------------------------------MSB
        temp1 = ((slk & 0x01) << 7) + ((stb & 0x03) << 5) + ((s16 & 0x01) << 4) + ((slkh & 0x01) << 3) + ((sdc & 0x01) << 2)
        temp2 = ((sdacsw & 0x03) << 6) + (sdac & 0x3F)
        #return glbl_reg1,glbl_reg2
        self.glbl_reg1 = self.reverseBit(temp1,8)
        self.glbl_reg2 = self.reverseBit(temp2,8)
    def reverseBit(self, dat, n):
    #n means how many bits you want.
        res = 0
        for i in range(n):
            res = res << 1
            res = res | (dat & 1)
            dat = dat >> 1
        return res
    def __init__(self):
        self.glbl_reg1 = 0
        self.glbl_reg2 = 0
        
class FE_REG(FE_chn,FE_glbl):
    def set_fe_reg(self):
        CHIP_REG =[]
        #here chn0 to chn15 
        #for i in range(16):
        #    CHIP_REG.append(self.FE_CHN[i].chn_reg)
        #or chn15 to chn0
        for i in range(16):
            CHIP_REG.append(self.FE_CHN[15-i].chn_reg)
 
        CHIP_REG.append(self.FE_GLOBAL.glbl_reg1)
        CHIP_REG.append(self.FE_GLOBAL.glbl_reg2)
        CHIP_REG.append(0)
        CHIP_REG.append(0) #completion for          
        #CHIP_REG.append(self.FE_GLOBAL.glbl_reg1)
        #CHIP_REG.append(self.FE_GLOBAL.glbl_reg2)        
        return CHIP_REG
    def spi_data(self):
        chip_reg = self.set_fe_reg()
        num = int(len(chip_reg)/4)
        brd_spi_data=[]
        for i in range(num):
            temp = (chip_reg[4*i+3] << 24) + (chip_reg[4*i+2] << 16) + (chip_reg[4*i+1] << 8) + chip_reg[4*i]
            brd_spi_data.append(temp)
        return brd_spi_data #72 32bits or 36 32-bits
        
    def __init__(self):
        self.FE_CHN  = [FE_chn(),FE_chn(),FE_chn(),FE_chn(),FE_chn(),FE_chn(),FE_chn(),FE_chn(),FE_chn(),FE_chn(),FE_chn(),FE_chn(),FE_chn(),FE_chn(),FE_chn(),FE_chn()]
        self.FE_GLOBAL = FE_glbl()
#"""The P1 ADC AISC includes 16 8-bit channel-spefific registers and one 16-bit global register that affects all channels"""
#class ADC_chn:
#    #This function maps the register of only one channel
#    def adc_chn_reg(self,d=0,pcsr=0,pdsr=0,slp=0,tstin=0):
#        #D0 D1 D2 D3 PCSR PDSR SLP TSTIN
#        #LSB-------------------------MSB
#        temp = ((tstin & 0x01) << 7) + ((slp & 0x01) << 6) + ((pdsr & 0x01) << 5) + ((pcsr & 0x01) << 4) + d
#        self.chn_reg = self.reverseBit(temp,8)
#        #return chn_reg
#    def reverseBit(self, dat, n):
#    #n means how many bits you want.
#        res = 0
#        for i in range(n):
#            res = res << 1
#            res = res | (dat & 1)
#            dat = dat >> 1
#        return res
#    def __init__(self):
#        self.chn_reg = 0
#
#class ADC_glbl:
#    #This function maps the 16-bit global register
#    def adc_glbl_reg(self,clk=0,frqc=0,engr=0,f0=0,f1=0,f2=0,f3=0,f4=0,f5=0,slsb=0):
#        #CLK0 CLK1 FRQC EN_GR F0 F1 F2 F3 F4 F5 sLSB RES4 RES3 RES2 RES1 RES0
#        #LSB-------------------------------------------------------------MSB
#        temp1 = (f3 << 7) + (f2 << 6) + (f1 << 5) + (f0 << 4) + (engr << 3) + (frqc << 2) + clk
#        temp2 = (slsb << 2) + (f5 << 1) + f4
#        #return glbl_reg1, glbl_reg2
#        self.glbl_reg1 = self.reverseBit(temp2,8)
#        self.glbl_reg2 = self.reverseBit(temp1,8)
#    def reverseBit(self, dat, n):
#    #n means how many bits you want.
#        res = 0
#        for i in range(n):
#            res = res << 1
#            res = res | (dat & 1)
#            dat = dat >> 1
#        return res
#    def __init__(self):
#        self.glbl_reg1 = 0
#        self.glbl_reg2 = 0

#class ASIC_config(FE_chn,FE_glbl,ADC_chn,ADC_glbl):
#    def set_chip_reg(self,project=None):
#        #IS the order correct?
#        CHIP_REG=[]
#        if project == None: #protodune
#            for i in range(16):
#                CHIP_REG.append(self.ADC_CHN[i].chn_reg)
#            CHIP_REG.append( self.ADC_GLOBAL.glbl_reg1)
#            CHIP_REG.append( self.ADC_GLOBAL.glbl_reg2)
#            for i in range(16):
#                CHIP_REG.append(self.FE_CHN[i].chn_reg)
#            CHIP_REG.append(self.FE_GLOBAL.glbl_reg1)
#            CHIP_REG.append(self.FE_GLOBAL.glbl_reg2)
#        elif project == 'SBND':
#            for i in range(16):
#                CHIP_REG.append(self.FE_CHN[i].chn_reg)
#            CHIP_REG.append(self.FE_GLOBAL.glbl_reg1)
#            CHIP_REG.append(self.FE_GLOBAL.glbl_reg2)
#        else:
#            print("No project found!!!")
#        return CHIP_REG
#    def __init__(self):
#        self.ADC_CHN = [ADC_chn(),ADC_chn(),ADC_chn(),ADC_chn(),ADC_chn(),ADC_chn(),ADC_chn(),ADC_chn(),ADC_chn(),ADC_chn(),ADC_chn(),ADC_chn(),ADC_chn(),ADC_chn(),ADC_chn(),ADC_chn()]
#        self.ADC_GLOBAL = ADC_glbl()
#        self.FE_CHN  = [FE_chn(),FE_chn(),FE_chn(),FE_chn(),FE_chn(),FE_chn(),FE_chn(),FE_chn(),FE_chn(),FE_chn(),FE_chn(),FE_chn(),FE_chn(),FE_chn(),FE_chn(),FE_chn()]
#        self.FE_GLOBAL = FE_glbl()
        #self.chip_reg = [0,0,0,0,0,0,0,0,0]

#class BOARD_config(ASIC_config):
#    def set_brd_reg(self,project=None):
#        chip_reg = []
#        for i in range(len(self.ASIC)):
#            #set the value first
#            chip_reg = chip_reg + self.ASIC[i].set_chip_reg(project)
#            #brd_spi_data = brd_spi_data + self.ASIC[i].chip_reg
#        #rebuid data
#        num = int(len(chip_reg)/4)
#        brd_spi_data=[]
#        for i in range(num):
#            temp = (chip_reg[4*i+3] << 24) + (chip_reg[4*i+2] << 16) + (chip_reg[4*i+1] << 8) + chip_reg[4*i]
#            brd_spi_data.append(temp)
#        return brd_spi_data #72 32bits or 36 32-bits
#    def __init__(self):
#        self.ASIC = [ASIC_config(),ASIC_config(),ASIC_config(),ASIC_config(),ASIC_config(),ASIC_config(),ASIC_config(),ASIC_config()]
