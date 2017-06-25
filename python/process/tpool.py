#!/usr/bin/env python
#  -*- coding: utf-8 -*-

from multiprocessing import Pool
import os, time
import logging

logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S')

def long_time_task(name):
    logging.info('Run task %s (%s)...' % (name, os.getpid()))
    start = time.time()
    time.sleep(10)
    end = time.time()
    logging.info('Task %s runs %0.2f seconds.' % (name, (end - start)))

if __name__=='__main__':
    logging.info('Parent process %s.' % os.getpid())
    while True:
        time.sleep(10)
        p = Pool()
        for i in range(4):
            p.apply_async(long_time_task, args=(i,))
        logging.info('Waiting for all subprocesses done...')
        p.close()
        p.join()
        logging.info('All subprocesses done.')
