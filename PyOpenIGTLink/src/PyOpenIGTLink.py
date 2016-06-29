# -*- coding: utf-8 -*-
"""

This file is part of Python implementation of OpenIGTLink 
protocol(http://openigtlink.org/) 

====
MIT License

Copyright (c) [2016] [Nirav Patel]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

"""

import struct 
from numpy.f2py.auxfuncs import throw_error
from abc import ABCMeta, abstractmethod

class Header:
    verison =1
    msgType=''
    deviceName=''
    timeStamp=0
    bodySize=0
    CRC_64=0
    body=''
    HEADER_LENGTH = 58
    def __init__(self, msgType="", deviceName="", body=""):
        self.msgType = msgType
        self.deviceName = deviceName
        self.body = body
        self.CRC_64 = 0
        
    def packHeader(self):
        return struct.pack('>H12s20sQQQ', self.verison, self.msgType, self.deviceName, self.timeStamp,len(self.body),self.CRC_64)
    def unpackHeader(self, data):
        (self.verison, self.msgType, self.deviceName, self.timeStamp, self.bodySize, self.CRC_64) = struct.unpack('>H12s20sQQQ', data)
    def toString(self):
        print 'IGTL Header ', self.verison, self.msgType, self.deviceName, self.timeStamp, self.bodySize, self.CRC_64
class MessageTypes:
    messageTypes = ['STRING', 'TRANSFORM', 'IMAGE']
    @staticmethod
    def isStringMessage(head):
        if head.msgType.strip('\x00').encode('utf-8') == 'STRING'.encode('utf-8'):
            return True
        else:
            return False
    @staticmethod
    def isTransformMessage(head):
        if head.msgType.strip('\x00').encode('utf-8') == 'TRANSFORM'.encode('utf-8'):
            return True
        else:
            return False
    @staticmethod
    def isImageMessage(head):
        if head.msgType.strip('\x00').encode('utf-8') == 'IMAGE'.encode('utf-8'):
            return True
        else:
            return False
        
class OpenIGTMessageBase:
    __metaclass__ = ABCMeta
    def __init__(self):
        pass
    def getHeader(self):
        pass
    @abstractmethod
    def packBody(self):
        pass
    @abstractmethod
    def unpackBody(self):
        pass
    def toString(self):
        pass
    
class StringMessage(OpenIGTMessageBase):
    deviceName = ''
    encoding = 3 #ASCII by default
    length = 0
    message = ''
    h = Header()
    def __init__(self, deviceName="", message=""):
        self.deviceName = deviceName
        self.message = message
    def getHeader(self):
        self.h = Header("STRING", self.deviceName, self.packBody())
        return self.h.packHeader()        
    def packBody(self):
            return (struct.pack(">HH%ds" %(len(self.message)), self.encoding, (len(self.message)), self.message))
    def unpackBody(self, header, data):
        self.h = header
        self.deviceName = header.deviceName
        (self.encoding, self.length, self.message) = struct.unpack(">HH%ds" %(self.h.bodySize-4), data)
        if self.encoding == 3:
            self.message = self.message.encode('ascii') 
        else:
            raise Exception('Unknown encoding', 'can not decode string message')
    def toString(self):
        print self.deviceName, self.encoding, self.length, self.message
        
class TransformMessage(OpenIGTMessageBase):
    deviceName=''
    transform=() #this is for now going to be 9 elements in same orrder as specified on OpenIGTLink specs
    h = Header()
    def __init__(self, deviceName="", transform=()):
        self.deviceName = deviceName
        self.transform = transform
    def getHeader(self):
        self.h = Header("TRANSFORM", self.deviceName, self.packBody())
        return self.h.packHeader()        
    def packBody(self):
        packer = struct.Struct('>f f f f f f f f f f f f' )
        return (packer.pack(*self.transform))
    def unpackBody(self, header, data):
        self.h = header
        self.deviceName =  header.deviceName
        (self.transform) = struct.unpack('>f f f f f f f f f f f f', data)
    def toString(self):
        print self.deviceName, self.transform
class ImageMessage(OpenIGTMessageBase):
    deviceName=''
    Version = 1
    T_numComponents=1
    S_scalarType=5
    E_endian=1
    O_imageCoords=2
    R_numPixels=[]
    T_vect=[]
    S_vect=[]
    N_vect=[]
    P_centerPosition=[]
    D_subVolumeStartIndex=[]
    DR_numSubVolumePixels=[]
    Image_Data=[]
    h = Header()
    IGTL_IMAGE_HEADER_SIZE = 72
    def __init__(self, deviceName='', T_numComponents=1, S_scalarType=5, E_endian=1, O_imageCoords=2, R_numPixels=[0,0,0], T_vect=[0,0,0], 
                 S_vect=[0,0,0], N_vect=[0,0,0], P_centerPosition=[0,0,0], D_subVolumeStartIndex=[0,0,0], DR_numSubVolumePixels=[0,0,0], Image_Data=[]):
        self.deviceName = deviceName
        self.T_numComponents = T_numComponents
        self.S_scalarType = S_scalarType
        self.E_endian = E_endian
        self.O_imageCoords = O_imageCoords
        self.R_numPixels = R_numPixels
        self.T_vect = T_vect
        self.S_vect = S_vect
        self.N_vect = N_vect
        self.P_centerPosition = P_centerPosition
        self.D_subVolumeStartIndex = D_subVolumeStartIndex
        self.DR_numSubVolumePixels = DR_numSubVolumePixels
        self.Image_Data = Image_Data
    def getHeader(self):
        self.h = Header("IMAGE", self.deviceName, self.packBody())
        return self.h.packHeader()        
    def packBody(self):
        packer = struct.Struct('>H4B3H12f6H%dH' %(len(self.Image_Data))) #thats it this will pack everything for us
        return(packer.pack(self.Version, self.T_numComponents, self.S_scalarType, self.E_endian, self.O_imageCoords,
                    self.R_numPixels[0], self.R_numPixels[1], self.R_numPixels[2], 
                    self.T_vect[0], self.T_vect[1], self.T_vect[2],
                    self.S_vect[0], self.S_vect[1], self.S_vect[2], 
                    self.N_vect[0],  self.N_vect[1], self.N_vect[2],  
                    self.P_centerPosition[0], self.P_centerPosition[1], self.P_centerPosition[2], 
                    self.D_subVolumeStartIndex[0], self.D_subVolumeStartIndex[1], self.D_subVolumeStartIndex[2], 
                    self.DR_numSubVolumePixels[0], self.DR_numSubVolumePixels[1], self.DR_numSubVolumePixels[2],
                    *self.Image_Data))
    def unpackBody(self, header, data):
        self.h = header
        self.deviceName =  header.deviceName
        (self.Version, self.T_numComponents, self.S_scalarType, self.E_endian, self.O_imageCoords,
                    self.R_numPixels[0], self.R_numPixels[1], self.R_numPixels[2], 
                    self.T_vect[0], self.T_vect[1], self.T_vect[2],
                    self.S_vect[0], self.S_vect[1], self.S_vect[2], 
                    self.N_vect[0],  self.N_vect[1], self.N_vect[2],  
                    self.P_centerPosition[0], self.P_centerPosition[1], self.P_centerPosition[2], 
                    self.D_subVolumeStartIndex[0], self.D_subVolumeStartIndex[1], self.D_subVolumeStartIndex[2], 
                    self.DR_numSubVolumePixels[0], self.DR_numSubVolumePixels[1], self.DR_numSubVolumePixels[2] ,)= struct.unpack('>H4B3H12f6H', data[0:self.IGTL_IMAGE_HEADER_SIZE]) #first unpack the image header as we need information from it to interpret the image
        #now we have all information we need to unpack the image
        numOfTotalPixels = self.R_numPixels[0]*self.R_numPixels[1]*self.R_numPixels[2]
        if self.S_scalarType==2: #int 8
            self.Image_Data = struct.unpack('%db' %numOfTotalPixels, data[self.IGTL_IMAGE_HEADER_SIZE:])
        if self.S_scalarType==3: #uint8
            self.Image_Data = struct.unpack('%dB' %numOfTotalPixels, data[self.IGTL_IMAGE_HEADER_SIZE:])
        if self.S_scalarType==4: #int16
            self.Image_Data = struct.unpack('%dh' %numOfTotalPixels, data[self.IGTL_IMAGE_HEADER_SIZE:])
        if self.S_scalarType==5: #uint16
            self.Image_Data = struct.unpack('%dH' %numOfTotalPixels, data[self.IGTL_IMAGE_HEADER_SIZE:])
        if self.S_scalarType==6: #int32
            self.Image_Data = struct.unpack('%di' %numOfTotalPixels, data[self.IGTL_IMAGE_HEADER_SIZE:])
        if self.S_scalarType==7: #uint32
            self.Image_Data = struct.unpack('%dI' %numOfTotalPixels, data[self.IGTL_IMAGE_HEADER_SIZE:])
        if self.S_scalarType==10: #float32
            self.Image_Data = struct.unpack('%df' %numOfTotalPixels, data[self.IGTL_IMAGE_HEADER_SIZE:])
        if self.S_scalarType==11: #float64
            self.Image_Data = struct.unpack('%dd' %numOfTotalPixels, data[self.IGTL_IMAGE_HEADER_SIZE:])
            
    def toString(self):
            print self.deviceName, self.Version, self.T_numComponents, self.S_scalarType, self.E_endian, self.O_imageCoords
            print self.R_numPixels[0], self.R_numPixels[1], self.R_numPixels[2]
            print self.T_vect[0], self.T_vect[1], self.T_vect[2]
            print self.S_vect[0], self.S_vect[1], self.S_vect[2]
            print self.N_vect[0],  self.N_vect[1], self.N_vect[2]
            print self.P_centerPosition[0], self.P_centerPosition[1], self.P_centerPosition[2]
            print self.D_subVolumeStartIndex[0], self.D_subVolumeStartIndex[1], self.D_subVolumeStartIndex[2]
            print self.DR_numSubVolumePixels[0], self.DR_numSubVolumePixels[1], self.DR_numSubVolumePixels[2]
