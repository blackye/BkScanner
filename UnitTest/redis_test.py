#!/usr/bin/python
#coding=utf8
import multiprocessing
#from multiprocessing import Process, Queue
import redis
import requests
import time



class RedisWork():

    def __init__(self, keyname):
        self.host = '10.23.84.112'
        self.port = 6379
        self.db = 1
        self.keyname = keyname
        self.redis_conn = None

        self.createConnect()

    def createConnect(self):
        pool = redis.ConnectionPool(host = self.host, port = self.port, db =self.db)
        self.redis_conn = redis.Redis(connection_pool = pool)

    def consumer(self):
        if self.redis_conn is not None:
            while True:
                if self.redis_conn.llen(self.keyname) != 0:
                    url = self.redis_conn.rpop(self.keyname)
                    print 'url:%s' % url
                time.sleep(4)

    def product(self):
        count = 1
        while True:
            url = 'http://10.121.50.%d' % count
            if self.redis_conn is not None:
                self.redis_conn.lpush(self.keyname, url)
                time.sleep(2)
                count = count + 1


# def consumer():
#     r = redis.Redis(host='10.23.84.112',port=6379,db=1)
#     while True:
#         k, url = r.blpop(['pool',])
#         queue.put(url)
#
# def worker():
#     while True:
#         url = queue.get()
#         print requests.get(url).text

def test_connect(ip):
    try:
        s = time.time()
        r = redis.StrictRedis(host=ip, port=6379, db=0, socket_timeout = 2, socket_connect_timeout = 1)
        print r.lpush('foo', 'bar')
        print r.rpop('foo')
    except Exception,e:
        print e
    print time.time() - s


if __name__ == '__main__':
    #rediswork = RedisWork('webpath')

    #product  = multiprocessing.Process(target = rediswork.product)
    #consumer = multiprocessing.Process(target = rediswork.consumer)

    #product.start()
    #consumer.start()

    #product.join()
    #consumer.join()
    test_connect('10.23.84.112')
    print 'done....'