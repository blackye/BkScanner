#!/usr/bin/python
#-*- coding:utf-8 -*-

'''rsync未授权访问'''

import commands,re
from os import path
from Plugins.iPluginBase import PluginBase
from Bin.lib.webscan.webscan_class import WebScan
from common.util import make_url
from common.threadpool import ThreadPool
from common.util import getCurTime
from config.db_settings import SYSVUL_TABLE
from config.logger import logger
from config.settings import DATA_DIC_PATH

__all__ = ['RsyncUnauthPlugin']

UNAUTH = False

class RsyncUnauthPlugin(PluginBase):

    name = "RsyncUnauthPlugin"
    version = '1.0'
    description = 'rsync匿名访问'


    def __init__(self):
        PluginBase.__init__(self)
        self.threadpool = ThreadPool(num_of_threads= 10 , num_of_work= 10 , daemon = True)
        self.service = 'rsync'
        self.rsync_dic_path = '%s/%s' % (DATA_DIC_PATH, 'rsync_dic/rsync.dic') #chmod 600 rsync.dic
        print self.rsync_dic_path
        self.port_list = ['873']




    def execute_run(self, ip, port, taskid):
        if str(port) in self.port_list:
            logger.info('[rsync] ip:%s, port:%s' % (str(ip), str(port)))
            self.threadpool.add_job(self.run, ip, port)
            self.async_deal_into_db(taskid)


    def run(self, *args, **kwargs):
        global UNAUTH
        UNAUTH = False
        (ip, port) = args[0]
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
        global UNAUTH
        cmd = 'rsync -v --password-file=' + self.rsync_dic_path + '--timeout=5 ' + ip + '::' + data
        print cmd
        (status, resp) = commands.getstatusoutput('rsync -v --password-file=' + self.rsync_dic_path + '  --timeout=5 ' + ip + '::' + data)
        if status == 0: #表示获取# 到敏感信息
            if resp == '':
                return UNAUTH
            resp_dic = resp.split(' \t\n')
            for item in resp_dic:
                re_result = re.search(r'[dwrx-]{10}\s+[\d]+\s+[\d]{4}\/[\d]{1,2}\/[\d]{1,2}\s+[0-5]\d:[0-5]\d:[0-5]\d\s+(.*)', item)
                if re_result is not None:
                    UNAUTH = True
                    break
                if item != ' ':
                    self.__test_rsyncunauth(ip, item[:item.find(' ')])
            return UNAUTH
        else:
            return UNAUTH

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
                    sysvul_dic['sid']        = taskid
                    sysvul_dic['ip']         = result_dit['ip']
                    sysvul_dic['port']       = result_dit['port']
                    sysvul_dic['service']    = self.service
                    sysvul_dic['first_time'] = getCurTime()
                    print sysvul_dic['ip'] + "  success!!!"
                    #self.plugin_db.insert_by_dict(SYSVUL_TABLE, sysvul_dic)
            except:
                break

    def wait_for_complete(self, taskid):
        #PluginBase.wait_for_complete(self)
        self.async_deal_into_db(taskid)
        self.db_close()