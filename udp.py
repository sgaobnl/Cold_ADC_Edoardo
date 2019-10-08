# -*- coding: utf-8 -*-
"""
Created on Thu Feb 15 14:28:53 2018

@author: JunbinZhang
"""
import struct
import sys 
import socket
import time
import binascii
from bit_op import Bit_Op
from array import array
import numpy as np
#from array import array
#from socket import AF_INET, SOCK_DGRAM
class UDP_frame:
    def info(self):
        print('udp packet cnt=%d'%self.udp_packet_cnt)
    def __init__(self,udp_frame_ptr,raw_data):
        self.udp_frame_length = (128*22)+8 #in words
        self.udp_frame_data = raw_data[int(udp_frame_ptr):int(udp_frame_ptr+self.udp_frame_length)]
        self.udp_packet_cnt = (self.udp_frame_data[0] << 16) + self.udp_frame_data[1]
        #self.udp_header_user_info = 0
        #self.udp_system_status=0
        self.udp_user_data = self.udp_frame_data[8:]
        
class UDP_frames(UDP_frame):
    def user_data_collection(self):
        user_data = []
        packet_cnts=[]
        for i in range(self.cycle):
            ptr = self.udp_frame_length * i
            udp_frame = UDP_frame(ptr,self.raw_data)
            user_data = user_data + udp_frame.udp_user_data
            packet_cnts.append(udp_frame.udp_packet_cnt)
        return [user_data,packet_cnts]
                 
    def __init__(self,cycle,raw_data):
        self.udp_frame_length = (128*22)+8
        self.cycle = cycle
        self.raw_data = raw_data
        
class UDP(UDP_frames):
#judge the reg and data is avalible or not
    def Isavaliable(self, reg, data = None):
        regVal = int(reg)
        dataVal = int(data)
        if(regVal < 0) or (regVal > self.MAX_REG_NUM):
            return None
        elif(dataVal < 0) or (dataVal > self.MAX_REG_VAL):
            return None
        else:
            return [regVal, dataVal]

#Build a massage for a register with its value
    def Msg_gen(self, regVal, dataVal):
        #crazy packet structure require for UDP interface
        dataValMSB = ((dataVal >> 16) & 0xFFFF)
        dataValLSB = dataVal & 0xFFFF
        MESSAGE = struct.pack('HHHHHHHHH',socket.htons( self.KEY1  ), socket.htons( self.KEY2 ),socket.htons(regVal),socket.htons(dataValMSB),
                socket.htons(dataValLSB),socket.htons( self.FOOTER  ), 0x0, 0x0, 0x0  ) #format=unsigned short, convert 16-bit positive integers from host to network byte order
        return MESSAGE

#Build a socket for communication
    def socket_gen(self, socket_type):
        new_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #creat a new socket, IPv4,UDP
        if(socket_type == "Listen"):
            new_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            #new_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 81920000) #open a large buffer for that
            new_socket.settimeout(5) #unit second
        else:
            new_socket.setblocking(0) #non-blocking socket
        return new_socket

#Write register from PC to FPGA ,this is an overloading function for wib and FEMB both
    def write_reg(self, reg, data, femb_addr = None):
        Value = self.Isavaliable(reg,data)
        if(Value == None):
            return None
        else:
            WRITE_MESSAGE = self.Msg_gen(Value[0],Value[1]) # build a message for register
            sock_write = self.socket_gen("Write")
            if femb_addr == None:#wib mode
                # send the UDP socket with the IP address and port parameters necessary to create the correct header
                sock_write.sendto(WRITE_MESSAGE,(self.UDP_IP, self.UDP_PORT_WREG ))      #WIB   WREG UDP port 32000
            elif femb_addr == 0:
                sock_write.sendto(WRITE_MESSAGE,(self.UDP_IP, self.UDPFEMB0_PORT_WREG  ))#FEMB0 WREG UDP port 32016
            elif femb_addr == 1:
                sock_write.sendto(WRITE_MESSAGE,(self.UDP_IP, self.UDPFEMB1_PORT_WREG  ))#FEMB1 WREG UDP port 32032
            elif femb_addr == 2:
                sock_write.sendto(WRITE_MESSAGE,(self.UDP_IP, self.UDPFEMB2_PORT_WREG  ))#FEMB2 WREG UDP port 32048
            elif femb_addr == 3:
                sock_write.sendto(WRITE_MESSAGE,(self.UDP_IP, self.UDPFEMB3_PORT_WREG  ))#FEMB3 WREG UDP port 32064
            # Close the socket
            sock_write.close()
            #print "FEMB_UDP--> Write: reg=%x,value=%x"%(reg,data)

# Read register from FPGA to PC, this is an overloading function for wib and FEMB both
    def read_reg(self, reg, femb_addr = None ):
        time.sleep(0.001)
        regVal = int(reg)
        if (regVal < 0) or (regVal > self.MAX_REG_NUM):
           #print "FEMB_UDP--> Error read_reg: Invalid register number"
           return None
        else:
            #set up listening socket, do before sending read request
            sock_readresp = self.socket_gen("Listen")
            READ_MESSAGE = self.Msg_gen(regVal,0)
            #set up a read request socket
            sock_read = self.socket_gen("Write")
            if femb_addr == None:
                sock_readresp.bind(('', self.UDP_PORT_RREGRESP ))      #WIB Response UDP port 32002
                sock_read.sendto(READ_MESSAGE,(self.UDP_IP,self.UDP_PORT_RREG))#Read request UDP port 32001
            elif femb_addr == 0:
                sock_readresp.bind(('', self.UDPFEMB0_PORT_RREGRESP )) #FEMB0 Response UDP port 32018
                sock_read.sendto(READ_MESSAGE,(self.UDP_IP,self.UDPFEMB0_PORT_RREG)) #FEMB0 Read request UDP port 32017
            elif femb_addr == 1:
                sock_readresp.bind(('', self.UDPFEMB1_PORT_RREGRESP )) #FEMB1 Response UDP port 32034
                sock_read.sendto(READ_MESSAGE,(self.UDP_IP,self.UDPFEMB1_PORT_RREG)) #FEMB1 Read request UDP port 32033
            elif femb_addr == 2:
                sock_readresp.bind(('', self.UDPFEMB2_PORT_RREGRESP )) #FEMB2 Response UDP port 32050
                sock_read.sendto(READ_MESSAGE,(self.UDP_IP,self.UDPFEMB2_PORT_RREG)) #FEMB2 Read request UDP port 32049
            elif femb_addr == 3:
                sock_readresp.bind(('', self.UDPFEMB3_PORT_RREGRESP )) #FEMB3 Response UDP port 32066
                sock_read.sendto(READ_MESSAGE,(self.UDP_IP,self.UDPFEMB3_PORT_RREG)) #FEMB3 Read request UDP port 32065

            sock_read.close()
            #try to receive response packet from board, store in hex
            data = []
            try:
                data = sock_readresp.recv(4*1024)
            except socket.timeout:
                self.udp_timeout_cnt = self.udp_timeout_cnt  + 1
                #print "FEMB_UDP--> Error read_reg: No read packet received from board, quitting"
                sock_readresp.close()
                return -1                 
            #dataHex = data.encode('hex') #can not be used in python3
            dataHex = binascii.hexlify(data) #change it to fit in python3
            sock_readresp.close()
            if int(dataHex[0:4],16) != regVal :
                #print "FEMB_UDP--> Error read_reg: Invalid response packet"
                return None
            else: 
                dataHexVal = int(dataHex[4:12],16)
                #print "FEMB_UDP--> Write: reg=%x,value=%x"%(reg,dataHexVal)
                return dataHexVal

#Check the register if it has been written correctly, this is an overloading function for wib and FEMB both         
    def write_reg_checked (self,reg, data, femb_addr = None):
        for i in range(10):
            self.write_reg(reg, data, femb_addr)
            time.sleep(0.001)
            rdata = self.read_reg(reg, femb_addr)
            rdata = self.read_reg(reg, femb_addr)#twice
            if data == rdata:
                break
            else:
                time.sleep(i+0.001)
        else: #the else clause executes if the loop iteration completes normally
            print ("readback value is different from written data, %d, %x, %x"%(reg, data, rdata))
            sys.exit()

#Write register with bit mask
    def write(self,reg,data,femb_addr = None):
        regNum = reg[0] #register number
        mask = reg[1]   #mask bits
        if mask == 0xFFFFFFFF:
            self.write_reg(regNum,data,femb_addr)
        else:
            #read the register and get original value
            temp = self.read_reg(regNum,femb_addr)
            #get mask bits
            index,size = self.bitop.mask(mask)
            #generate a new value
            val = self.bitop.set_bits(temp,index,size,data)
            #write
            self.write_reg(regNum,val,femb_addr)
#Read register with bit mask
    def read(self,reg,femb_addr = None):
        regNum = reg[0]
        mask   = reg[1]
        #read the register and get original value
        temp = self.read_reg(regNum,femb_addr)
        if mask == 0xFFFFFFFF:
            return temp
        else:
            #get mask bits
            index,size = self.bitop.mask(mask)
            return self.bitop.get_bits(temp,index,size)

#Get high-speed data
    def get_rawdata(self,PktNum,checkflg,Jumbo=None):
        #set up listening socket
        sock_data = self.socket_gen("Listen")
        sock_data.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 81920000) #open a large buffer for that
        sock_data.bind(('', self.UDP_PORT_HSDATA))                          #high-speed data UDP port 32003
        
        if Jumbo == 'None':
            recvbuf = 8192      
        else:
            recvbuf = 9014 #match to 0xefc
        
        if (PktNum < self.PKT_MAX) or (PktNum == self.PKT_MAX):
            cycle = 1
        else:
            cycle = (PktNum // self.PKT_MAX) + 1
        #print('cycle=%d'%cycle)
        recv_raw=[]
        for i in range(cycle):    
            data = None
            try:
                data = sock_data.recv(recvbuf) 
            except socket.timeout:
                print ("UDP--> Error get_data: No data packet received from board, quitting")
                sock_data.close()
                return None
            if data != None:
               recv_raw.append(data)
        sock_data.close()
        rawdata = array('H',b''.join(recv_raw))#array.array 
        rawdata.byteswap()                     #byte swapping
        rawdata = rawdata.tolist()             #change it to list       
        udp_frames_inst = UDP_frames(cycle,rawdata)
        user_data,packet_cnts = udp_frames_inst.user_data_collection()
        if checkflg == True:
            self.check_packets(packet_cnts)
        return user_data
        
    def get_pure_rawdata(self,PktNum,Jumbo=None):
        #set up listening socket
        sock_data = self.socket_gen("Listen")
        sock_data.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 81920000) #open a large buffer for that
        sock_data.bind(('', self.UDP_PORT_HSDATA))                          #high-speed data UDP port 32003
        
        if Jumbo == 'None':
            recvbuf = 8192      
        else:
            recvbuf = 9014 #match to 0xefc      
        if (PktNum < self.PKT_MAX) or (PktNum == self.PKT_MAX):
            cycle = 1
        else:
            cycle = (PktNum // self.PKT_MAX) + 1
#        print('cycle=%d'%cycle)
#        recv_raw=b""
        recv_raw=[]
        for i in range(cycle):    
#            if (i%1000==0):
#                print (i)
            data = None
            try:
                data = sock_data.recv(recvbuf) 
            except socket.timeout:
                print ("UDP--> Error get_data: No data packet received from board, quitting")
                sock_data.close()
                return None
            if data != None:
               recv_raw.append(data)
#                recv_raw += data
        sock_data.close()
        return recv_raw
    
    def clr_server_buf(self, en = False):
        if (en):
            #set up listening socket
            sock_data = self.socket_gen("Listen")
            sock_data.settimeout(1)
            sock_data.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 81920000) #open a large buffer for that
            sock_data.bind(('', self.UDP_PORT_HSDATA))                          #high-speed data UDP port 32003
            recvbuf = 9014 #match to 0xefc
            buflen = 0
            while(1):
                try:
                    buflen = buflen + len(sock_data.recv(recvbuf))    
                except socket.timeout:
                    print ("Server Buffer (%d bytes) is cleared"%buflen)
                    sock_data.close()
                    break
        else:
            pass
      
    def check_packets(self,data):
        num = len(data)
        if (num == 2 or num > 2):
            for i in range(num-1):
                if(data[i+1] - data[i] == 1):
                    continue
                else:
                    print("noncontinuous udp packet found!!! %d"%(i+1))
                #break
#            else:
#                print("continuous packets")       
    #__INIT__#
    def __init__(self):
        self.bitop = Bit_Op()
        self.UDP_IP = "192.168.121.1"
        #self.udp_frame = UDP_frame()
        #self.UDP_IP = "10.73.136.36"
        #self.UDP_HEADER_LEN = 16 #bytes
        #self.PKT_MAX = 174
        
        self.PKT_MAX = 128
        
        self.udp_timeout_cnt = 0
        self.KEY1 = 0xDEAD
        self.KEY2 = 0xBEEF
        self.FOOTER = 0xFFFF
        self.UDP_PORT_WREG = 32000
        self.UDP_PORT_RREG = 32001
        self.UDP_PORT_RREGRESP = 32002
        self.UDP_PORT_HSDATA = 32003
        
        self.MAX_REG_NUM = 0x666
        self.MAX_REG_VAL = 0xFFFFFFFF
        self.MAX_NUM_PACKETS = 1000000
        #---------------------------------#
        self.PKT_LEN = 44 #44 bytes per pkt
        self.PKT_HEADER = 0xBC3C
        self.PKT_HEADER1 = 0x3CBC
        #---------------------------------#
        self.UDPFEMB0_PORT_WREG =     32016
        self.UDPFEMB0_PORT_RREG =     32017
        self.UDPFEMB0_PORT_RREGRESP = 32018

        self.UDPFEMB1_PORT_WREG =     32032
        self.UDPFEMB1_PORT_RREG =     32033
        self.UDPFEMB1_PORT_RREGRESP = 32034

        self.UDPFEMB2_PORT_WREG =     32048
        self.UDPFEMB2_PORT_RREG =     32049
        self.UDPFEMB2_PORT_RREGRESP = 32050

        self.UDPFEMB3_PORT_WREG =     32064
        self.UDPFEMB3_PORT_RREG =     32065
        self.UDPFEMB3_PORT_RREGRESP = 32066
        
#        self.sock_data = self.socket_gen("Listen")
#        self.sock_data.bind(('', self.UDP_PORT_HSDATA)) #high-speed data UDP port 32003
if __name__ == '__main__':
    udp = UDP()
    #print(brd_config.check_board())
    #print(type(brd_config.read_fpga_reg(0x101)))
    
#    udp.write_reg(0x4,0x09520200)
#    time.sleep(0.001)
#    udp.write_reg(0x4,0x0952020100)
#    time.sleep(1)
#    udp.write_reg(0x4,0x09520200)
#    result = udp.read_reg(0x4)
#    print(hex(result))
