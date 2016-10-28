#!/usr/bin/env python
#  -*- coding: utf-8 -*-

import socket
import threading

conn_list = []  # 所有的已连接的TCP列表
conn_list_msg = []  # tcp msg列表
#所有已连接的TCP消息分发
def TaskHandler():
    while conn_list_msg:
        for i in conn_list_msg:
            for c in conn_list:
                c.sendall(i)
            conn_list_msg.remove(i)



#Socket服务
class SocketServer(object):
    conn = None

    def __init__(self, ip, port=8923):  #Use a port number larger than 1024 (recommended)
        self.ip = ip
        self.port = port

        self.socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        try:
            self.socket.bind((self.ip, self.port))
            print 'IP:%s,  PORT:%s' % (ip, port)
            self.socket.listen(10)

        except Exception, e:
            print 'invaild ip&port', e
            pass


    @staticmethod
    def dataHandler(conn):
        #接受TCP套接字的数据
        while 1:
            rec_msg = conn.recv(1024)
            print rec_msg
            #完整发送TCP数据
            conn_list_msg.append(rec_msg)

            # conn.sendall(rec_msg)
            TaskHandler()
        conn.close()


    #socket运行器
    @property
    def run(self):
        while 1:
            conn, addr = self.socket.accept()
            print '已连接客户端:', addr
            if conn:
                #添加连接列表中
                conn_list.append(conn)
                #多线程启动单个TCP连接
                ThreadServer(SocketServer.dataHandler, conn).start()

        self.socket.close()


#多线程处理socket连接
class ThreadServer(threading.Thread):
    def __init__(self, func, *args):
        self.func = func
        self.args = args
        threading.Thread.__init__(self)

    def run(self):
        apply(self.func, self.args)



if __name__ == '__main__':
    server = SocketServer('127.0.0.1').run
