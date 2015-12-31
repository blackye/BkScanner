#!/usr/bin/env python
#coding:utf-8

from os import path
import os, sys

from config.activemq_config import MASTER_AQ_HOST
from config.activemq_config import MASTER_AQ_HOST_PORT
from config.activemq_config import SUBSCRIBE_DESC
#MASTER_AQ_HOST = '192.168.20.70'
#MASTER_AQ_HOST_PORT = 61613
import stomp
import sys, time
import Queue
import json


class MsgListener():

    def __init__(self, msg_que):
        self.msg_que = msg_que

    def on_error(self, headers, message):
        #logger.error('receive an error %s' % message)
        pass

    def on_message(self, headers, message):
        self.msg_que.put_nowait(message)


class ActiveMQBase(object):
    '''
    消息队列基类
    '''
    def __init__(self , host, port = 61613):
        self.host = host
        self.port = port
        self.conn = None

    def test_connect(self):
        '''
        打开连接
        '''
        self.conn = stomp.Connection([('%s' % self.host, self.port)])

        if self.conn is None:
            #logger.error("can't connect the activemq server!")
            sys.exit()

    def disconnect(self):
        '''
        关闭连接
        '''
        if self.conn is not None:
            self.conn.disconnect()


class ActiveMQConsumerBase(ActiveMQBase):
    '''
    消息消费者基类
    '''
    def __init__(self):
        super(ActiveMQConsumerBase, self).__init__(host = MASTER_AQ_HOST)
        self.msg_que = Queue.Queue(0)
        self.listener = MsgListener(self.msg_que)
        super(ActiveMQConsumerBase, self).test_connect()

    def receivemsg(self):
        self.conn.start()
        self.conn.connect(wait=True)
        #logger.info('connect the host activemq server!')


class ActiveMQProducerBase(ActiveMQBase):
    '''
    消息生产者基类
    '''
    def __init__(self):
        super(ActiveMQProducerBase, self).__init__(host = MASTER_AQ_HOST)


    def send2msg(self):
        pass

class ActiveMQConsumer(ActiveMQConsumerBase):
    '''
    消费者
    '''
    def __init__(self):
        super(ActiveMQConsumer, self).__init__()

    def receivemsg(self, desc):
        super(ActiveMQConsumer, self).receivemsg()
        self.conn.set_listener("", self.listener)
        self.conn.subscribe(destination = desc, id=1, ack='auto')

    def close(self):
        ActiveMQBase(self).disconnect()


class ActiveMQProducer(ActiveMQProducerBase):
    '''
    生产者
    '''
    def __init__(self):
        super(ActiveMQProducer, self).__init__()
        super(ActiveMQProducer, self).test_connect()
        self.conn.start()
        self.conn.connect(wait=True)


    def send2msg(self, msg_json, desc):
        super(ActiveMQProducer, self).send2msg()
        '''
        发送消息
        :return:
        '''
        if self.conn is not None:
            self.conn.send(body='%s' % msg_json, destination=desc, ack='auto')

    def close(self):
        ActiveMQBase(self).disconnect()


#-----------------------------------------------------------
#------ test ---------

def SendMsg(desc):
    que = Queue.Queue(0)
    producer = ActiveMQProducer()
    json_dic = {'ip':'10.15.185.252', 'port':25}
    count = 1

    while True:
        send_dic = json_dic
        send_dic.update({'count':count})
        send_msg = json.dumps(send_dic)
        print send_msg
        producer.send2msg(send_msg, desc)
        print 'send msg:%s' % send_msg
        count = count + 1
        time.sleep(3)


def ReceiveMsg(desc):
    consurm = ActiveMQConsumer()
    consurm.receivemsg(desc)

    while True:
        msg = consurm.listener.msg_que.get(block = True)
        print 'receive count:%s' % json.loads(msg)['count']
        time.sleep(0.4)


if __name__ == '__main__':
    import threading

    product = threading.Thread(target= SendMsg, args=('scan_info',))
    consurm = threading.Thread(target= ReceiveMsg, args=('scan_info',))

    product.start()
    consurm.start()

    product.join()
    consurm.join()
