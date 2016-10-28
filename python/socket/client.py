#!/usr/bin/env python
#  -*- coding: utf-8 -*-

import socket
import datetime

class SocketClient(object):
    def __init__(self, ip, port=8923):
        self.ip = ip
        self.port = port
        self.socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        self.name = ''
        #注册姓名
        self.register()
        try:
            self.socket.connect((self.ip, self.port))
            print '%s已连接服务器 %s:%s' % (self.name, ip, port)
        except Exception, e:
            print 'invaild port:%s  ip:%s' % (ip, port)
            print 'error', e


    #注册姓名
    def register(self):
        while not self.name:
            self.name = raw_input('请输入您的姓名：').strip()


    #客户端socket启动器
    @property
    def run(self):
        while 1:
            try:
                msg = raw_input('发送消息:').strip()
                if msg:
                    now = datetime.datetime.now().strftime('%m-%d %H:%M:%S')
                    msg = '[%s %s]:%s' % (now, self.name, msg)
                    self.send(msg)
                    print self.read()
                else:
                    print self.read()
            except Exception, e:
                print 'error', e
        self.close()

    def send(self, msg):
        self.socket.sendall(msg)

    def read(self):
        msg = self.socket.recv(1024)
        return msg

    def close(self):
        self.socket.close()

if __name__ == '__main__':
    SocketClient('127.0.0.1').run
