#!/usr/bin/evn python
#-*- coding:utf-8 -*-
#*******************************************************
# Copyright (C) 2014 - All Rights Reserved
# Author(s): BlackYe_. <hswjzhang@gmail.com>
# Time:2015-01-13
#
# Function: 域名\IP web漏洞db
#******************************************************

from base_db import BaseDB


class WebVulDb(BaseDB):

    def __init__(self):
        super(WebVulDb, self).__init__()
