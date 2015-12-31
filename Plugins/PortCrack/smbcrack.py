#!/usr/bin/env python
#-*- coding:utf-8 -*-

from Bin.lib.portcrack.portcrackbase import PortCrackBase
from Plugins.iPluginBase import PluginBase
from common.util import getCurTime


__all__ = ['SmbCrackPlugin']

class SmbCrackPlugin(PluginBase):

    name = "SmbCrackPlugin"
    version = '1.0'

    def __init__(self):
        PluginBase.__init__(self)

        self.user_dict = 'smbuser.txt'
        self.pass_dict = 'password.txt'
        self.service = 'samba'


    def execute_run(self, ip, port, taskid):
        pass


    def async_deal_into_db(self, taskid):
        '''
        异步入库
        :return:
        '''
        pass
        #
        # while not self.threadpool.resultQueue.empty():
        #     try:
        #         result_dit = self.threadpool.resultQueue.get_nowait()
        #         if result_dit['status']:
        #             self.plugin_db.executeUpdate("insert into t_iisput_vul(`sid`, `url`, `first_time`)"
        #                                         "values('%s', '%s', '%s')" % (taskid, result_dit['ip'] , getCurTime()))
        #     except:
        #         break

    def wait_for_complete(self):
        PluginBase.wait_for_complete(self)
        self.db_close()