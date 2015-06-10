#!/usr/bin/env python
#  -*- coding: utf-8 -*-

import zmq

context = zmq.Context()

print 'connecting to hello zmq server...'
socket = context.socket(zmq.REQ)
socket.connect("tcp://127.0.0.1:5555")

for request in range(10):
    print "sending request {} ....".format(request)
    socket.send(b'hello')

    message = socket.recv()
    print "received replay {}, {}".format(request, message)
