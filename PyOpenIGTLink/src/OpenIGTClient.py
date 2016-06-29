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

#Sample OpenIGTLink client sending STRING message
#create an INET, STREAMing socket
import socket 
from PyOpenIGTLink import *
from SocketReceiverThread import SocketReceiverThread

class OpenIGTClient:
    serverIp = '127.0.0.1'
    serverPort = 18944
    clientResponseHandler = SocketReceiverThread()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    
    def __init__(self, serverIp="127.0.0.1", serverPort=18944):
        self.socks = socket.socket(socket.AF_INET, socket.SOCK_STREAM)         # Create a socket object
        #s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.serverIp = serverIp
        self.serverPort = serverPort
        
        self.sock.connect((self.serverIp, self.serverPort))
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, struct.pack('ii', 1, 1))
        
        clientResponseHandler = SocketReceiverThread(self.sock)
        clientResponseHandler.setDaemon(True)
        clientResponseHandler.start()
        #while True:
         #   time.sleep(0.1)
          #  pass
        #clientResponseHandler.join()
        
    def sendMessage(self, msg):
        """
        @type msg:OpenIGTMessageBase
        """
        print 'Sending Message:' , msg.toString()
        self.sock.send(msg.getHeader())
        self.sock.send(msg.packBody())
        print 'Message Sent'
        
    def addOpenIGTListener(self , Listener):
        self.clientResponseHandler.addListener(Listener)
