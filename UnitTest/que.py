#!/usr/bin/env python
#coding:utf-8

import threading
import Queue
import time
import json
que = Queue.Queue(0)

def main():

    t1 = threading.Thread(target= consurm)
    t2 = threading.Thread(target= product)

    t1.start()
    t2.start()

    t1.join()
    t2.join()

def product():
    count = 1
    while True:
        print 'product : %d' % count
        que.put_nowait(count)
        count = count + 1
        print 'product sleep!'
        time.sleep(30)

def consurm():
    while True:
        num = que.get(block = True)
        print 'consurm:%d' % num
        print 'consurm sleep!'
        time.sleep(1)

def test_kwargs(**kwargs):
    print type(json.dumps(kwargs))


import requests

def test_webservice(ip, port = 80):
    url = '%s://%s:%s' % ('http' if str(port) != '443' else 'https', str(ip), str(port))

    try:
        requests.get(url = url, timeout = 2, verify = False)
        return True
    except:
        return False

def test_args(port, **kwargs):
    print 'haha'
    print kwargs

if __name__ == '__main__':
    # str = "<html>我是一个好学生，adfafda,后台管理，登录111，木马啊啊admin啊啊啊,<html>afdsfdasf<title>"
    # senswords_dic = ['admin', '后台管理', '登陆', '木马', '上传']
    # senswords = []
    # for word in senswords_dic:
    #     if str.find(word) != -1:
    #         senswords.append(word)
    #
    # for s in senswords:
    #     print s

    #test_kwargs(url = 'http://www.baidu.com', port = 8080)

    import urllib2
    #print test_webservice('10.23.84.12')
    print test_args(port = 80, url='http://10.23', port1='80')