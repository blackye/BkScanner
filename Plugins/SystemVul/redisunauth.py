#!/usr/bin/python
#-*- coding:utf-8 -*-

'''redis未授权访问'''

import commands
import redis
from Plugins.iPluginBase import PluginBase
from Bin.lib.webscan.webscan_class import WebScan
from common.util import make_url
from common.threadpool import ThreadPool
from common.util import getCurTime
from config.db_settings import SYSVUL_TABLE
from config.logger import logger

__all__ = ['RedisUnauthPlugin']

class RedisUnauthPlugin(PluginBase):

    name = "RedisUnauthPlugin"
    version = '1.0'
    description = 'redis匿名访问'


    def __init__(self):
        PluginBase.__init__(self)
        self.threadpool = ThreadPool(num_of_threads= 10 , num_of_work= 10 , daemon = True)
        self.service = 'redis'
        self.port_list = ['6379']

    def execute_run(self, ip, port, taskid):
        if str(port) in self.port_list:
            logger.info('[redis] ip:%s, port:%s' % (str(ip), str(port)))
            self.threadpool.add_job(self.__test_redisunauth, ip, port)
            self.async_deal_into_db(taskid)


    def __test_redisunauth(self, *args, **kwargs):
        '''
        验证是否存在redis未授权访问漏洞
        :param url:
        :return:
        '''
        (ip, port) = args[0]
        bunauth = False
        try:
            r = redis.StrictRedis(host=ip, port = int(port), db=0, socket_timeout = 2, socket_connect_timeout = 1)
            r.lpush('foo', 'bar')
            if r.rpop('foo') == 'bar':
                bunauth = True
        except Exception,e:
            pass
        return {'ip' : ip, 'port' : port, 'status' : bunauth}

    def async_deal_into_db(self, taskid):
        '''
        异步入库
        :return:
        '''
        while not self.threadpool.resultQueue.empty():
            try:
                result_dit = self.threadpool.resultQueue.get_nowait()
                print result_dit
                if result_dit['status']:
                    sysvul_dic = {}
                    sysvul_dic['sid'] = taskid
                    sysvul_dic['ip']  = result_dit['ip']
                    sysvul_dic['port'] = result_dit['port']
                    sysvul_dic['service'] = self.service
                    sysvul_dic['first_time'] = getCurTime()
                    self.plugin_db.insert_by_dict(SYSVUL_TABLE, sysvul_dic)
            except:
                break

    def wait_for_complete(self, taskid):
        #PluginBase.wait_for_complete(self)
        self.async_deal_into_db(taskid)
        self.db_close()