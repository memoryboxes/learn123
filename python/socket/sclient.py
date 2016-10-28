#!/usr/bin/env python
#  -*- coding: utf-8 -*-

import socket
import struct

HOST = '127.0.0.1'
PORT = 8001

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

cmd = raw_input("Please input msg:")
s.send(cmd)
data = s.recv(1024)
print data

print struct.unpack('4s7s50s', data[0:61])

s.close()
