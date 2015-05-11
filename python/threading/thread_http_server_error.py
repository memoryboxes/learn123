#!/usr/bin/env python
#!coding=utf-8

import sys
import time
import socket
import threading
from BaseHTTPServer import HTTPServer ,BaseHTTPRequestHandler
from SocketServer import ThreadingMixIn

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """
        处理get请求
        """
        query=self.path
        print "query: %s thread=%s" % (query, str(threading.current_thread()))

        #ret_str="<html>" + self.path + "<br>" + str(self.server) + "<br>" + str(self.responses) +  "</html>"
        ret_str="<html>" + self.path + "<br>" + str(self.server) +  "</html>"

        time.sleep(5)

        try:
            self.send_response(200)
            self.send_header('Content-type','text/html')
            self.end_headers()
            self.wfile.write(ret_str)
        except socket.error, e:
            print "socket.error : Connection broke. Aborting" + str(e)
            self.wfile._sock.close()  # close socket
            self.wfile._sock=None
            return False

        print "success prod query :%s" % (query)
        return True


#多线程处理
class ThreadingHTTPServer(ThreadingMixIn,HTTPServer):
    pass

if __name__ == '__main__':
    serveraddr = ('',9001)

    ser = ThreadingHTTPServer(serveraddr,RequestHandler)
    ser.serve_forever()
    sys.exit(0)
