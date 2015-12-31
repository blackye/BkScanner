#!/usr/bin/env python
#-*- coding:utf-8 -*-

import threading
import Queue
import gevent
from gevent import monkey
from gevent import Greenlet
from gevent import pool
from gevent import queue
from gevent import event
from gevent import Timeout
from gevent import threadpool
from gevent.local import local
from gevent.coros import Semaphore

import sys

plist = local()
semaphore = Semaphore()

def work(alist):
    semaphore.acquire()
    print alist.pop()
    semaphore.release()

def thread_test(v):
    alist = []

    for x in range(11, 20):
        alist.append(x)

    #first_crack_dir_pool = pool.Pool(2)
    #first_crack_dir_pool.map(work, alist)

    thread_list = []
    for x in range(10):
        thread = gevent.spawn(work,alist)
        thread_list.append(thread)

    gevent.joinall(thread_list)

    #while plist.que.qsize() > 0:
    #    print 'thread:%s num:%d' % (v, plist.get_nowait())

'''
工作线程池
'''

import Queue
import threading
import sys, time


class WorkThread(threading.Thread):
    def __init__(self, workQueue, resultQueue, timeout = 5, **kwargs):
        threading.Thread.__init__(self, kwargs = kwargs)
        self.timeout = timeout #线程在结束前等待任务队列多长时间
        self.setDaemon(True)
        self.workQueue = workQueue
        self.resultQueue = resultQueue
        self.start()

    def run(self):
        while True:
            try:
                callbackfunc, args,  kwargs = self.workQueue.get(block = True, timeout = self.timeout)
                res = callbackfunc(args, kwargs)
                print 'ccccc'
                #执行结果加入到结果队列中
                self.resultQueue.put_nowait(res)
                self.workQueue.task_done()
            except Queue.Empty:
                print 'aaaa'
                break
            except:
                print sys.exc_info()
                raise
            time.sleep(0.3)


class ThreadPool:
    '''
    线程池
    '''
    def __init__(self, num_of_threads = 20):
        self.workQueue  = Queue.Queue(maxsize= 3)
        self.resultQueue = Queue.Queue(0)
        self.threads = []
        self.__create_threadpool(num_of_threads)


    def __create_threadpool(self, num_of_threads):
        for i in range(num_of_threads):
            thread = WorkThread(self.workQueue, self.resultQueue)
            self.threads.append(thread)

    def wait_for_complete(self):
        #等待线程结束
        while len(self.threads):
            thread = self.threads.pop()
            if thread.isAlive():
                thread.join()

    def add_job(self, callbackfunc, *args, **kwargs):
        print self.workQueue.qsize()
        self.workQueue.put((callbackfunc, args, kwargs))


def work(*args, **kwargs):
    time.sleep(2)

if __name__ == '__main__':
    threadpool = ThreadPool(20)

    for x in range(100):
        threadpool.add_job(work, x, '')
        print '1111'
        #time.sleep(2)

    if threadpool is not None:
        threadpool.wait_for_complete() #等待线程结束
        threadpool = None
    print 'over!'