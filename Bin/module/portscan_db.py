#!/usr/bin/evn python
#-*- coding:utf-8 -*-
#*******************************************************
# Copyright (C) 2014 - All Rights Reserved
# Author(s): BlackYe_. <hswjzhang@gmail.com>
# Time:2015-01-13
#
# Function: 端口扫描数据库
#******************************************************

from base_db import BaseDB


class PortScanDB(BaseDB):

    def __init__(self):
        BaseDB.__init__(self)
