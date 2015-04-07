#!/usr/bin/env python
# coding=utf-8
__author__ = 'Dean'

import pdb, time, logging
from tornado import ioloop, httpclient, gen, stack_context
from tornado.gen import Task
import tornado.ioloop
import tornado.iostream
import socket, struct

def init_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    sh = logging.StreamHandler()

    formatter = logging.Formatter('%(asctime)s -%(module)s:%(filename)s-L%(lineno)d-%(levelname)s: %(message)s')
    sh.setFormatter(formatter)

    logger.addHandler(sh)
    logging.info("Current log level is : %s", logging.getLevelName(logger.getEffectiveLevel()))

HOST = '127.0.0.1'    # The remote host
PORT = 8000           # The same port as used by the server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

header = '{"aa":1, "bb":"cc"}'
fd = open("/Users/Dean/Pictures/logo.png", 'rb')
body = fd.read()
fd.close

ss = struct.pack('!LLHH', len(header), len(body), 1, 0)
s.send(ss)
s.sendall(header)
s.sendall(body)
s.sendall(b' END')
data = s.recv(8)
# data = data.replace(b' END', '')
code, message_len = struct.unpack('!IL', data)
if message_len > 0:
    message = s.recv(message_len)
else:
    message = ""
print 'Received: %d: %s' % (code, message)
time.sleep(10)
s.close()