#!/usr/bin/env python
#  -*- coding: utf-8 -*-

import socket
import struct

HOST = '0.0.0.0'
PORT = 8001

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(5)

print 'Server start at: %s:%s' %(HOST, PORT)
print 'wait for connection...'

while True:
    conn, addr = s.accept()
    print 'Connected by ', addr

    while True:
        data = conn.recv(1024)
        print data

        conn.send(struct.pack("4s7s50s", '0037', '1234567', '0'*50))

conn.close()


