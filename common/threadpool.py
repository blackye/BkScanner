#!/usr/bin/evn python
#-*- coding:utf-8 -*-

'''
工作线程池
'''

import Queue
import threading
from config.logger import logger
import sys, time


class WorkThread(threading.Thread):
    def __init__(self, workQueue, resultQueue, timeout = 10, daemon = False, **kwargs):
        threading.Thread.__init__(self, kwargs = kwargs)
        self.timeout = timeout #线程在结束前等待任务队列多长时间
        self.setDaemon(True)
        self.workQueue = workQueue
        self.resultQueue = resultQueue
        self.daemon = daemon
        if self.daemon:
            self.setDaemon(True) #主线程结束，子线程也结束
        self.start()

    def run(self):
        while True:
            try:
                if self.daemon:
                    callbackfunc, args,  kwargs = self.workQueue.get(block = True) #如果主线程退出，子线程也退出。这里设置阻塞
                else:
                    callbackfunc, args,  kwargs = self.workQueue.get(block = True, timeout = self.timeout)

                res = callbackfunc(args, kwargs)
                #执行结果加入到结果队列中
                if res is not None:
                    self.resultQueue.put_nowait(res)
            except Queue.Empty:
                logger.info('work queue empty!')
                break
            except:
                logger.error(sys.exc_info())
                raise
            time.sleep(0.3)


class ThreadPool(object):
    '''
    线程池
    '''
    def __init__(self, num_of_threads = 20, num_of_work = 10, timeout = 10, daemon = False):
        self.workQueue  = Queue.Queue(num_of_work)
        self.resultQueue = Queue.Queue(0)
        self.wait_timeout = timeout
        self.daemon = daemon
        self.threads = []
        self.__create_threadpool(num_of_threads)


    def __create_threadpool(self, num_of_threads):
        for i in range(num_of_threads):
            thread = WorkThread(self.workQueue, self.resultQueue, timeout = self.wait_timeout , daemon = self.daemon)
            self.threads.append(thread)

    def wait_for_complete(self):
        #等待线程结束
        while len(self.threads):
            thread = self.threads.pop()
            if thread.isAlive():
                thread.join()

    def add_job(self, callbackfunc, *args, **kwargs):
        self.workQueue.put((callbackfunc, args, kwargs))
