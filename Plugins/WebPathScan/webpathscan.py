#!/usr/bin/env python
#-*- coding:utf-8 -*-

'''
web路径扫描
'''
from Plugins.iPluginBase import PluginBase
from Bin.lib.webscan.webscan_class import WebScan
from common.util import make_url
from common.util import getCurTime
from common.threadpool import ThreadPool
from Bin.module.webvul_db import WebVulDb
from config.logger import logger
from config.db_settings import WEBVUL_TABLE, WEBIPVUL_TABLE
from config.settings import DOMAIN_TYPE
import time, Queue


__all__ = ['WebPathScanPlugin']

class WebPathScanPlugin(PluginBase):

    name = "WebPathScanPlugin"
    version = '1.0'


    def __init__(self):
        PluginBase.__init__(self)
        self.threadpool = ThreadPool(num_of_threads= 10 , num_of_work= 10 , daemon = True)

    def execute_run(self, ip, port, bdomain, taskid):
        if bdomain == DOMAIN_TYPE[0]:
            webscan = WebScan(make_url(ip, port), webdomain=True, proxy=False)
        elif bdomain == DOMAIN_TYPE[1]:
            webscan = WebScan(make_url(ip, port), webdomain=False, proxy = False)
        self.threadpool.add_job(webscan.run)
        self.async_deal_into_db(bdomain, taskid)

    def wait_for_complete(self, bdomain, taskid):
        #PluginBase.wait_for_complete(self)
        self.async_deal_into_db(bdomain, taskid)
        self.db_close()

    def async_deal_into_db(self, bdomain, taskid):
        '''
        入库
        :return:
        '''
        while not self.threadpool.resultQueue.empty():
            try:
                result_dit = self.threadpool.resultQueue.get(block = False)
                figerinfo = result_dit['figerinfo']
                exist_result_list = result_dit['result_list']
                for exist_result in exist_result_list:
                    vulurl = {}
                    vulurl['sid'] = taskid
                    vulurl['url'] = exist_result['url']
                    vulurl['title'] = exist_result['title']
                    vulurl['keyword'] = ''
                    vulurl['code'] = exist_result['http_code']
                    vulurl['figerinfo'] = figerinfo
                    vulurl['first_time'] = getCurTime()
                    if bdomain == DOMAIN_TYPE[0]:
                        #sql = "insert into t_web_vulurl(`sid`, `url`, `title`, `keyword`, `code`, `figerinfo`, `first_time`) values('%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (str(taskid), str(exist_result['url']) , str(exist_result['title']), '', str(exist_result['http_code']), figerinfo, getCurTime())
                        self.plugin_db.insert_by_dict(WEBVUL_TABLE , vulurl)
                    elif bdomain == DOMAIN_TYPE[1]:
                        self.plugin_db.insert_by_dict(WEBIPVUL_TABLE, vulurl)
            except Exception,e:
                logger.error(str(e))
                break

