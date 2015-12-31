#!/usr/bin/evn python
#-*- coding:utf-8 -*-


import gevent
from gevent import Greenlet
from gevent import pool
import random


class MyGreenlet(Greenlet):

    def __init__(self, message, threadnum , n):
        Greenlet.__init__(self)
        self.message = message
        self.threadnum = threadnum
        self.n = n

    def _run(self):
        print('message:%s ---- thread:%s' % (self.message, self.threadnum))
        gevent.sleep(self.n)
        print('just test ---- thread:%s' % (self.threadnum))


def test(message):
    print 'message:%s' % message
    print 'sleep.......'
    gevent.sleep(3)

# gevents = []
# for x in xrange(20):
#     g = MyGreenlet("Hi there!", x, random.randint(0,10))
#     gevents.append(g)

# for x in gevents:
#     x.start()
# #g.start()
# for x in gevents:
#     x.join()

# crack_dir_pool = pool.Pool(5)
# messages = ['haha','1213','345234']
# crack_dir_pool.map(test, messages)
# print 'hahaha'


import time
import threading

class A():

    def __init__(self):
        #threading.Thread(target= self.run).start()
        pass

    def exec_run(self):
        print 'no'

    def run(self, *args, **kwargs):
        (ip, port) = args
        print ip
        print port

import commands

def __test_rsyncunauth(ip, data = ' '):
    '''
    验证是否存在rsync未授权访问漏洞
    :param url:
    :return:
    '''
    (status, resp) = commands.getstatusoutput('rsync -av --timeout=5 ' + ip + '::' + data)
    if status == 0: #表示获取# 到敏感信息
        resp_dic = resp.split(' \t\n')
        for item in resp_dic:
            if data != ' ':
                return True
            __test_rsyncunauth(ip, item[:item.find(' ')])

    return False

import subprocess

if __name__ == '__main__':
    # script = '/usr/bin/whatweb --no-errors --color=never %s' % ('http://aq.qiyi.domain')
    # output = subprocess.check_output(script, shell = True)
    # s = str(output)
    # print '%s' % s.lstrip('http://aq.qiyi.domain')

    if 3 > 2:
        print 'hahhaa'
    elif 4 > 3:
        print 'lalal'
    elif 5 > 4:
        print 'ccac'
    elif 4 < 1:
        print 'xxxx'
    else:
        pass