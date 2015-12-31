#!/usr/bin/evn python
#-*- coding:utf-8 -*-
#*******************************************************
# Copyright (C) 2014 - All Rights Reserved
# Author(s): BlackYe_. <hswjzhang@gmail.com>
# Time:2015-01-13
#
# Function: 域名分析数据库
#******************************************************

from base_db import BaseDB


class DomainDB(BaseDB):

    def __init__(self):
        #super(DomainDB, self).__init__()
        BaseDB.__init__(self)