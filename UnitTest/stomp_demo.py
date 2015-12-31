#!/usr/bin/python
#-*- coding:utf-8 -*-

import stomp
import sys
import time
import random
from stomp import StatsListener, WaitingListener
import Queue

class MyListener():

    def __init__(self):
        self.que = Queue.Queue(0)

    def on_error(self, headers, message):
        print 'receive an error %s' % message

    def on_message(self, headers, message):
        print 'receive a message %s' % message
        self.que.put_nowait(message)


def main():
    desc = 'scan_info'
    conn = stomp.Connection([('10.23.84.112', 61613)])
    if conn is not None:
        print '[+]....connect!'
    else:
        sys.exit()
    listener = MyListener()
    conn.set_listener("", listener)
    conn.start()
    conn.connect(wait=True)
    conn.subscribe(destination=desc, id=1,ack='auto')
    #i = 0
    #while True:
    #message = "192.168.0.%d" % i
    count = 0
    message = "xxxx"
    while True:
        conn.send(body='%s--id:%d' % (message, count), destination=desc ,ack='auto')
        time.sleep(4)
        count = count + 1

    #while True:
    #    time.sleep(1)

    print '[done...]'
    conn.disconnect()

if __name__ == '__main__':main()
