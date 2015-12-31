#!/usr/bin/python
#-*- coding:utf-8 -*-

'''
web iis put vulnerable
'''

import requests
import urlparse
from Plugins.iPluginBase import PluginBase
from Bin.lib.webscan.webscan_class import WebScan
from common.util import make_url
from common.util import getCurTime
from common.threadpool import ThreadPool
from config.db_settings import IISPUTVUL_TABLE


__all__ = ['WebIISPutPlugin']

class WebIISPutPlugin(PluginBase):

    name = "WebIISPutPlugin"
    version = '1.0'


    def __init__(self):
        PluginBase.__init__(self)
        self.threadpool = ThreadPool(num_of_threads= 20 , num_of_work= 10 , daemon = True)

    def execute_run(self, ip, port, bdomain, taskid):
        self.threadpool.add_job(self.__test_iisput, ip, port)
        self.async_deal_into_db(bdomain, taskid)

    def __test_iisput(self, *args, **kwargs):
        '''
        验证是否存在iis PUT 漏洞
        :param url:
        :return:
        '''
        (ip, port) = args
        url = make_url(ip, port)
        txt_url = urlparse.urljoin(url, '1.txt')
        try:
            req = requests.put('%s' % txt_url, data = "test!", timeout=2)
            if req.status_code == 201:  #201 created
                return {'url':url, 'status': True}
            else:
                return {'url':url, 'status': False}
        except:
            return {'url':url, 'status': False}

    def async_deal_into_db(self, bdomain, taskid):
        '''
        入库
        :return:
        '''
        while not self.threadpool.resultQueue.empty():
            try:
                result_dit = self.threadpool.resultQueue.get_nowait()
                if result_dit['status']:
                    iis_vulurl = {}
                    iis_vulurl['sid'] = taskid
                    iis_vulurl['url'] = result_dit['url']
                    iis_vulurl['first_time'] = getCurTime()
                    self.plugin_db.insert_by_dict(IISPUTVUL_TABLE, iis_vulurl)
            except:
                break

    def wait_for_complete(self, bdomain, taskid):
        #PluginBase.wait_for_complete(self)
        self.async_deal_into_db(bdomain, taskid)
        self.db_close()