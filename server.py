#!/usr/bin/env python
# coding=utf-8
__author__ = 'Dean'

"""
一个基于tornado的tcp服务，提供给client上传、文件处理、图片处理的接口
协议内容:12字节头+config+body
头格式：LLHH
"""
import logging
import tornado.ioloop
import tornado.tcpserver
import struct

def init_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    sh = logging.StreamHandler()

    formatter = logging.Formatter('%(asctime)s -%(module)s:%(filename)s-L%(lineno)d-%(levelname)s: %(message)s')
    sh.setFormatter(formatter)

    logger.addHandler(sh)
    logging.info("Current log level is : %s", logging.getLevelName(logger.getEffectiveLevel()))

class Connection(object):
    """
    用来处理客户端连接的类
    """
    clients = set()
    header_len = 12
    header_format = '!LLHH'
    EOF = b' END'

    def __init__(self, stream, address):
        Connection.clients.add(self)
        self._stream = stream
        self._address = address
        self._stream.set_close_callback(self.on_close)
        self.read_header()

    def clear_connection_stat(self):
        self._config_len = None
        self._body_len = None
        self._orther_code = None
        self._command = None
        self._config = None
        self._read_loop = False
        self._body = None
        self._temp_body_fd = None
        self.log(20, 'clear connection stat.')

    def read_header(self):
        """
        首先读取出协议头
        读取之前先将清除所有变量的值
        """
        self.clear_connection_stat()
        self.log(logging.INFO, 'read header.')
        self._stream.read_bytes(self.header_len, self.recv_header)

    def recv_header(self, data):

        try:
            self._config_len, self._body_len, self._command, self._orther_code = struct.unpack(self.header_format, data)
        except:
            self.log(logging.ERROR, 'header parse error.')
            # 如果无法解析header，则认为是噪音，重新等待接收数据
            self.finish_reuqest(300)
            return
        self.log(logging.INFO, 'header: config_len-%d, body_len-%d, command-%d, orther-%d.' % (self._config_len, self._body_len, self._command, self._orther_code))
        if self._config_len >= 0:
            self.log(logging.INFO, 'read config.')
            self._stream.read_bytes(self._config_len, self.recv_config)
        else:
            # 没有发送config，直接读取body
            self.read_body()

    def recv_config(self, data):
        """
        接收config数据
        """
        self.log(logging.INFO, 'config: %s.' % data)
        self._config = data
        if self._body_len > 0:
            self.log(logging.INFO, 'read body.')
            return self._stream.read_bytes(self._body_len, self.recv_body)
        else:
            # 没有发送文件
            self.log(logging.WARNING, 'body not found.')
            self.finish_request('404')
            return

    def recv_body(self, data):
        """
        处理body数据
        """
        self._body = data
        # 检查请求是否完成传输
        self.log(logging.INFO, 'check request end.')
        self._stream.read_until(self.EOF, self.check_request_end)

    def check_request_end(self, data):
        """
        检查请求是否完成
        """
        if data is not self.EOF:
            # 如果没有以EOF结尾，则不算完成
            pass
        else:
            pass
        # 触发处理流程
        self.finish_request(200)


    def write(self, data):
        """
        向客户端发送消息
        """
        self._stream.write(data)

    def finish_request(self, code=200, message=""):
        """
        完成本次请求，等待接受新的请求
        """
        ss = struct.pack('!IL', code, len(message))
        self.write(ss + message + self.EOF)
        self.read_header()
        return True

    def on_close(self):
        """
        客户端断开连接
        """
        self.log(logging.INFO, "client closed")
        Connection.clients.remove(self)

    def log(self, level, log):
        logging.log(level, "(%s:%d) %s" % (self._address[0], self._address[1], log))
        return


class LightfileServer(tornado.tcpserver.TCPServer):
    def handle_stream(self, stream, address):
        logging.info("New connection: %s:%d" % address)
        Connection(stream, address)
        logging.info("connection num is: %d" % len(Connection.clients))

if __name__ == "__main__":
    init_logging()
    logging.info("server start.")
    server = LightfileServer()
    server.listen(8000)
    tornado.ioloop.IOLoop.instance().start()