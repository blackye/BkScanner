#!/usr/bin/python
#-*- coding:utf-8 -*-

'''rsync未授权访问'''

import commands
from Plugins.iPluginBase import PluginBase
from Bin.lib.webscan.webscan_class import WebScan
from common.util import make_url
from common.threadpool import ThreadPool
from common.util import getCurTime
from config.db_settings import SYSVUL_TABLE
from config.logger import logger

__all__ = ['RsyncUnauthPlugin']

class RsyncUnauthPlugin(PluginBase):

    name = "RsyncUnauthPlugin"
    version = '1.0'
    description = 'rsync匿名访问'


    def __init__(self):
        PluginBase.__init__(self)
        self.threadpool = ThreadPool(num_of_threads= 10 , num_of_work= 10 , daemon = True)
        self.service = 'rsync'
        self.port_list = ['873']


    def execute_run(self, ip, port, taskid):
        if str(port) in self.port_list:
            logger.info('[rsync] ip:%s, port:%s' % (str(ip), str(port)))
            self.threadpool.add_job(self.run, ip, port)
            self.async_deal_into_db(taskid)


    def run(self, *args, **kwargs):
        (ip, port) = args[0]
        print ip
        if self.__test_rsyncunauth(ip):
            return {'ip':ip, 'port': port , 'status': True}
        else:
            return {'ip':ip, 'port': port , 'status': False}


    def __test_rsyncunauth(self, ip, data = ' '):
        '''
        验证是否存在rsync未授权访问漏洞
        :param url:
        :return:
        '''
        (status, resp) = commands.getstatusoutput('export RSYNC_PASSWORD=;rsync -avz --timeout=5 ' + ip + '::' + data)
        if status == 0: #表示获取# 到敏感信息
            resp_dic = resp.split(' \t\n')
            for item in resp_dic:
                if item != ' ':
                    return True
                self.__test_rsyncunauth(ip, item[:item.find(' ')])

        return False

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
                    sysvul_dic['sid']        = taskid
                    sysvul_dic['ip']         = result_dit['ip']
                    sysvul_dic['port']       = result_dit['port']
                    sysvul_dic['service']    = self.service
                    sysvul_dic['first_time'] = getCurTime()
                    self.plugin_db.insert_by_dict(SYSVUL_TABLE, sysvul_dic)
            except:
                break

    def wait_for_complete(self, taskid):
        #PluginBase.wait_for_complete(self)
        self.async_deal_into_db(taskid)
        self.db_close()