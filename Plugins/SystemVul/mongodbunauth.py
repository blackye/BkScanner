#!/usr/bin/python
#-*- coding:utf-8 -*-

'''Mongodb未授权访问'''

import pymongo
from Plugins.iPluginBase import PluginBase
from Bin.lib.webscan.webscan_class import WebScan
from common.util import make_url
from common.threadpool import ThreadPool
from common.util import getCurTime
from config.logger import logger
from config.db_settings import SYSVUL_TABLE

__all__ = ['MongodbUnauthPlugin']

class MongodbUnauthPlugin(PluginBase):

    name = "MongodbUnauthPlugin"
    version = '1.0'
    description = 'mongodb匿名访问'


    def __init__(self):
        PluginBase.__init__(self)
        self.threadpool = ThreadPool(num_of_threads= 10 , num_of_work= 10 , daemon = True)
        self.service = 'mongodb'
        self.port_list = ['27017', '28017']

    def execute_run(self, ip, port, taskid):
        if str(port) in self.port_list:
            logger.info('[Mongodb] ip:%s, port:%s' % (str(ip), str(port)))
            self.threadpool.add_job(self.__test_mongodbunauth, ip, port)
            self.async_deal_into_db(taskid)


    def __test_mongodbunauth(self, *args, **kwargs):
        '''
        验证是否存在mongodb未授权访问漏洞
        :param url:
        :return:
        '''
        (ip, port) = args[0]
        bunauth = False
        try:
            connection = pymongo.MongoClient(ip, port, socketTimeoutMS=3000)
            dbname = connection.database_names()
            connection.close()
            #101.227.21.94:27017/[u'Log', u'db', u'config', u'admin']
            #logger.info(ip + ":" + str(port) + '/' + str(dbname))
            bunauth = True
        except Exception,e:
            pass
        return {'ip' : ip, 'status' : bunauth, 'port' : str(port)}


    def async_deal_into_db(self, taskid):
        '''
        异步入库
        :return:
        '''
        while not self.threadpool.resultQueue.empty():
            try:
                result_dit = self.threadpool.resultQueue.get_nowait()
                if result_dit['status']:
                    sysvul_dic = {}
                    sysvul_dic['sid'] = taskid
                    sysvul_dic['ip']  = result_dit['ip']
                    sysvul_dic['port'] = result_dit['port']
                    sysvul_dic['service'] = self.service
                    sysvul_dic['first_time'] = getCurTime()
                    self.plugin_db.insert_by_dict(SYSVUL_TABLE, sysvul_dic)
                    #self.plugin_db.executeUpdate("insert into t_sys_vul(`sid`, `ip`, `port`, `first_time`, `service`) "
                    #                            "values('%s', '%s', '%s', '%s', '%s')" % (taskid, result_dit['ip'] , result_dit['port'], getCurTime(), self.service))
            except:
                break

    def wait_for_complete(self, taskid):
        #PluginBase.wait_for_complete(self)
        self.async_deal_into_db(taskid)
        self.db_close()