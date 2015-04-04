#!/usr/bin/env python
# coding=utf-8
__author__ = 'Dean'

"""
一个基于tornado的tcp服务，提供给client上传、文件处理、图片处理的接口
"""
import tornado.ioloop
import tornado.tcpserver
import struct

class Connection(object):
    clients = set()

    def __init__(self, stream, address):
        Connection.clients.add(self)
        self._stream = stream
        self._address = address
        self._stream.set_close_callback(self.on_close)
        self._header_len = 0
        self._body_len = 0
        self.read_header()
        print "A new client connected.", address

    def read_header(self):
        self._stream.read_bytes(8, self.recv_header_size)
        # self._stream.read_until_close(self.recv_header)

    def recv_header_size(self, data):
        self._header_len, self._body_lean = struct.unpack('!2I', data)
        print self._header_len, self._body_lean
        self._stream.read_bytes(self._header_len, self.recv_header)

    def recv_header(self, data):
        print data
        self._stream.read_bytes(self._body_lean, self.recv_body)

    def recv_body(self, data):
        fd = open('/Users/Dean/Pictures/logo1.png', 'wb')
        fd.write(data)
        fd.close
        self.send_message('successfull')

    def send_message(self, data):
        self._stream.write(data)

    def on_close(self):
        print "A client close.", self._address
        Connection.clients.remove(self)


class LightfileServer(tornado.tcpserver.TCPServer):
    def handle_stream(self, stream, address):
        print "New connection :", address
        Connection(stream, address)
        print "connection num is:", len(Connection.clients)

if __name__ == "__main__":
    print("server start.")
    server = LightfileServer()
    server.listen(8000)
    tornado.ioloop.IOLoop.instance().start()

