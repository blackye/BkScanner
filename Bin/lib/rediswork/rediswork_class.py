#!/usr/bin/python
#coding=utf8

import redis
import time
import json
from config.redis_config import REDIS_HOST, REDIS_HOST_PORT, REDIS_DB

class RedisWork(object):
    '''
    域名、IP、端口扫描结果任务
    '''

    def __init__(self):
        self.host = REDIS_HOST
        self.port = REDIS_HOST_PORT
        self.db = REDIS_DB
        self.redis_conn = None

        self.createConnect()

    def createConnect(self):
        pool = redis.ConnectionPool(host = self.host, port = self.port, db =self.db)
        self.redis_conn = redis.Redis(connection_pool = pool)

    def pushvulInfo(self, keyname, **kwargs):
        '''
        消息入库
        '''
        if self.redis_conn is not None:
            self.redis_conn.lpush(keyname, json.dumps(kwargs))

    def getvulInfo(self, keyname):
        '''
        获取消息信息
        '''
        if self.redis_conn is not None:
            if self.redis_conn.llen(keyname) != 0:
                return self.redis_conn.rpop(keyname)
            else:
                return None


    def disconnect(self):
        '''
        关闭连接
        '''
        pass