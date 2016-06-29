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

from threading import Thread
import socket 
from PyOpenIGTLink import *
import time
import sys

class SocketReceiverThread(Thread):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    listeners = set()
    def __init__(self, sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM) ):
        Thread.__init__(self)
        self.sock = sock
    def addListener(self, listener):
        self.listeners.add(listener)
    def removeListener(self, listener):
        self.listeners.remove(listener)
    
    def run(self):
        head = Header()
        #start reading data probably first header size
        while True:
            header_data = self.sock.recv(Header.HEADER_LENGTH)
            if len(header_data) == Header.HEADER_LENGTH:
                head.unpackHeader(header_data)
                head.toString()
                
                body_data = self.readNBytesWithTimeout(head.bodySize)
                print 'bodySize=' , len(body_data)
                if MessageTypes.isStringMessage(head):
                    strMsg = StringMessage();
                    strMsg.unpackBody(head, body_data)
                    #strMsg.toString()
                    for listner in self.listeners:
                        listner.onRxStringMessage(strMsg.deviceName, strMsg.message)
                elif MessageTypes.isTransformMessage(head):
                    transMsg = TransformMessage();
                    transMsg.unpackBody(head, body_data)
                    #transMsg.toString()
                    for listner in self.listeners:
                        listner.onRxTransformMessage(transMsg.deviceName, transMsg.transform)
                elif MessageTypes.isImageMessage(head):
                    imgMsg = ImageMessage();
                    imgMsg.unpackBody(head, body_data)
                    for listner in self.listeners:
                        listner.onRxImageMessage(imgMsg.deviceName, imgMsg)
                elif MessageTypes.isImageMessage(head):
                    print "not a known messagetype", body_data

            if not header_data:
                print '\nDisconnected from chat server\n'
            #time.sleep(0.01)
            #sys.stdout.flush()
            continue
    def readNBytesWithTimeout(self, N):
        data = ''
        #print 'reading ', N, ' bytes'
        while len(data) != N:
            bytesRemaining = N-len(data)
            #print 'bytes remanin=' , bytesRemaining , ' of ' , N 
            buf = self.sock.recv(bytesRemaining)
            #print 'bytes red this iteration=', len(buf)
            data = data + buf
            #print 'total bytes red so far=' , len(data)
        return data