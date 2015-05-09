# -*- coding: utf-8 -*-

import httplib
import time
import datetime
import threading

class SimThreadClass(threading.Thread):
    """simplest exp"""

    def run(self):
        now = datetime.datetime.now()
        print "%s says Hello World at time: %s" % (self.getName(), now)

class FuncThreadClass(threading.Thread):
    """custom func and args"""

    def __init__(self, func, args, name=''):
        threading.Thread.__init__(self)
        self.name = name
        self.func = func
        self.args = args

    def run(self):
        apply(self.func, self.args)
        time.sleep(1)

if __name__ == '__main__':
    # test start simple exp
    for i in range(2):
      t = SimThreadClass()
      t.start()

    # test for custom custom func and args
    def now(who):
        now = datetime.datetime.now()
        conn = httplib.HTTPConnection("www.baidu.com")
        conn.request("GET", "/index.html")
        r1 = conn.getresponse()
        print r1.status, r1.reason
        print "%s says Hello World at time: %s" % (who, now)

    for i in range(200):
        t = FuncThreadClass(now, ("memorybox%d" % i,))
        t.start()
        print threading.active_count()
