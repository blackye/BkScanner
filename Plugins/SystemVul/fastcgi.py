#!/usr/bin/python
#-*- coding:utf-8 -*-

'''Fastcgi 命令执行'''

import commands
from Plugins.iPluginBase import PluginBase
from Bin.lib.fastcgi.fpm import FPM
from common.threadpool import ThreadPool
from common.util import getCurTime
from config.db_settings import SYSVUL_TABLE
from config.logger import logger

__all__ = ['FastcgiPlugin']

class FastcgiPlugin(PluginBase):

    name = "FastcgiPlugin"
    version = '1.0'
    description = 'fastcgi remote exec'


    def __init__(self):
        PluginBase.__init__(self)
        self.threadpool = ThreadPool(num_of_threads= 10 , num_of_work= 10 , daemon = True)
        self.service = 'fastcgi'
        self.port_list = ['9000']

    def execute_run(self, ip, port, taskid):
        if str(port) in self.port_list:
            logger.info('[fastcgi] ip:%s, port:%s' % (str(ip), str(port)))
            self.threadpool.add_job(self.__test_fastcgi, ip, port)
            self.async_deal_into_db(taskid)


    def __test_fastcgi(self, *args, **kwargs):
        '''
        :param url:
        :return:
        '''
        (ip, port) = args[0]
        try:
            phpfpm = FPM(
                host= ip,
                port= int(port),
                document_root='/'
            )

            post_string = 'title=Hello&body=World!'

            status_header, headers, output, error_message = phpfpm.load_url(
                url='/index.php?a=b',
                content=post_string,
                remote_addr='127.0.0.1',
                cookies='c=d;e=f;'
            )
            return {'ip':ip, 'port': port, 'status':True}
        except:
            return {'ip':ip, 'port': port, 'status':False}


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
            except:
                break


    def wait_for_complete(self, taskid):
        #PluginBase.wait_for_complete(self)
        self.async_deal_into_db(taskid)
        self.db_close()