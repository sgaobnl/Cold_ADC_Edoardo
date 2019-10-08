# -*- coding: utf-8 -*-
"""
Created on Mon Apr 23 22:51:48 2018

@author: JunbinZhang
"""
class Bit_Op:
    def mask(self,value):
        if value == 0:
            print("Bit operation error, Value shouldn't be zero")
        index = 0
        size = 0
        while value:
            if value & 0x1 == 0:
                index = index +1
            else:
                size = size +1
            value = value >> 1
        return index, size    
    def mask_bits(self,index,size):
        return (((1 << size) -1) << index)
    def get_bits(self,data,index,size):
        return (data & self.mask_bits(index,size)) >> index
    def set_bits(self,data,index,size,value):
        return (data & (~self.mask_bits(index,size))) | (value << index)
    def reverseBit(self,dat,n):
        #n means how many bits you want
        res = 0
        for i in range(n):
            res = res << 1
            res = res | (dat & 1)
            dat = dat >> 1
        return res
    #def __init__(self): 
    #    a = 0b10111011
    #    print bin(get_mask(0,3))
    #    print bin(a)
    #    print bin(readfrom(a,0,3))
    #    print bin(writeto(a,0,3,0b011))
    #---------end of bit operation
#bit_op = Bit_Op()
#a = 0x5a5b4c4d
#index,size = bit_op.mask(0xFFFFFFFF)
#d = bit_op.get_bits(a,index,size)
#print(hex(d))
#t = bit_op.set_bits(a,index,size,0x66666666)
#print(hex(t))
