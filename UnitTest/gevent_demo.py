#!/usr/bin/env python
#-*- coding:utf-8 -*-

import gevent
from gevent import monkey
from gevent import Greenlet
from gevent import pool
from gevent import queue
from gevent import event
from gevent import Timeout
from gevent import threadpool



monkey.patch_all()
import requests
import logging

def monkey_patch():
    '''
    requests库中文乱码补丁
    '''
    prop = requests.models.Response.content
    def content(self):
        _content = prop.fget(self)
        if self.encoding == 'ISO-8859-1':
            encodings = requests.utils.get_encodings_from_content(_content)
            if encodings:
                self.encoding = encodings[0]
            else:
                self.encoding = self.apparent_encoding
            _content = _content.decode(self.encoding, 'replace').encode('utf8', 'replace')
            self._content = _content
        return _content
    requests.models.Response.content = property(content)


def exec_url(url):
    try:
        s = requests.get(url, timeout=2)
        print url + '-------------- status:%d' % s.status_code
    except requests.exceptions.ConnectionError:
        print url + '-------------- status: failed!'


def main1():
    #monkey_patch()
    logger = logging.getLogger("spider")
    logger.setLevel(logging.DEBUG)
    hd = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    hd.setFormatter(formatter)
    logger.addHandler(hd)

    concurrent_num = 20

    urls = ['http://10.15.185.%d' % url for url in range(255)]
    work_pool = pool.Pool(concurrent_num)
    work_pool.map(exec_url, urls)


evt = event.Event()

def setter():
    '''After 3 seconds, wake all threads waiting on the value of evt'''
    print('A: Hey wait for me, I have to do something')
    gevent.sleep(10)
    print("Ok, I'm done")
    evt.set()

def waiter():
    '''After 3 seconds the get call will unblock'''
    print("I'll wait for you")
    evt.wait()  # blocking
    print("It's about time")

def main():
    gevent.joinall([
        gevent.spawn(setter),
        gevent.spawn(waiter),
        gevent.spawn(waiter),
        gevent.spawn(waiter),
        gevent.spawn(waiter),
        gevent.spawn(waiter)
    ])

if __name__ == '__main__':main()







