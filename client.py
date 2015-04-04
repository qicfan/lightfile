#!/usr/bin/env python
# coding=utf-8
__author__ = 'Dean'

import socket
import struct
import time

HOST = '127.0.0.1'    # The remote host
PORT = 8000           # The same port as used by the server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

header = 'hello world'
fd = open("/Users/Dean/Pictures/logo.png", 'rb')
body = fd.read()
fd.close

ss = struct.pack('!2I', len(header), len(body))
s.send(ss)
s.sendall(header)
s.sendall(body)
data = s.recv(1024)
print 'Received', repr(data)
time.sleep(10)
s.close()
