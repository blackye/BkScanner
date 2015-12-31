#!/usr/bin/evn python
#-*- coding:utf-8 -*-
#*******************************************************
# Copyright (C) 2014 - All Rights Reserved
# Author(s): BlackYe_. <hswjzhang@gmail.com>
# Time:2015-01-13
#
# Function: dao 数据库基类
#******************************************************

from Bin.module.core.mysql_core import MySqldb
from config.db_settings import MYSQL_DB_SETTING
from Bin.module.core import torndb

class BaseDB():

    def __init__(self):
        db_setting = MYSQL_DB_SETTING()
        #super(BaseDB, self).__init__(db_setting.HOST, db_setting.USER, db_setting.PWD, db_setting.DATA)
        #self.createConnection()
        self.db = torndb.Connection(host = '%s:%s' % (db_setting.HOST, db_setting.PORT), database= db_setting.DATABASE, user=db_setting.USER, password= db_setting.PWD)

    def getConn(self):
        return self.db