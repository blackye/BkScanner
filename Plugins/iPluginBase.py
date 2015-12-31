#!/usr/bin/python
#coding:utf-8

import Queue
from Bin.module.base_db import BaseDB

class PluginBase(object):
     """ 定义一个接口，其他 插件必须实现这个接口，name 属性必须赋值 """


     name = ''
     description = ''
     version = '1.0'


     def __init__(self):
        self.threadpool = None
        self.plugin_db = BaseDB().getConn()

     def execute_run(self):
        pass

     def async_deal_into_db(self):
        '''
        数据异步入库
        :return:
        '''
        pass

     def db_close(self):
        self.plugin_db.close()


     def wait_for_complete(self):
        if self.threadpool is not None:
            self.threadpool.wait_for_complete()

