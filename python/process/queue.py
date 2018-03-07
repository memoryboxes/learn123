#!/usr/bin/env python
#  -*- coding: utf-8 -*-

from multiprocessing.dummy import Pool,Queue
import time

class test:
    def __init__(self):
        self.a = range(10)
    def run(self):
        in_queue, out_queue = Queue(), Queue()
        for i in self.a:
            in_queue.put(i)
        def f(in_queue, out_queue):
            while not in_queue.empty():
                time.sleep(1)
                out_queue.put(in_queue.get()+1)
        pool = Pool(4, f, (in_queue, out_queue))
        self.b = []
        while len(self.b) < len(self.a):
            if not out_queue.empty():
                self.b.append(out_queue.get())
        pool.terminate()

t = test()
t.run()
print t.b
