#!/usr/bin/env python
#coding:utf-8

'''
多进程通信
'''


import multiprocessing
import time

class Porduct(multiprocessing.Process):

    def __init__(self, task_que):
        multiprocessing.Process.__init__(self)
        self.task_que = task_que

    def run(self):
        i = 0
        while True:
            self.task_que.put_nowait(i)
            print 'product num : %d' % i
            i = i + 1
            print 'product sleep.....'
            time.sleep(30)


class Consumer(multiprocessing.Process):

    def __init__(self, result_que):
        multiprocessing.Process.__init__(self)
        self.result_que = result_que

    def run(self):
        while True:
            num = self.result_que.get(block = True)
            print 'get num : %d' % num
            self.result_que.task_done
            print 'consumer sleep.....'
            time.sleep(2)

if __name__ == "__main__":
    tasks = multiprocessing.JoinableQueue()

    products = Porduct(tasks)
    consumer = Consumer(tasks)

    products.start()
    consumer.start()

    tasks.join()

    print 'done....'
    #p = Process(target = test_product())
    #for i in range(100):

