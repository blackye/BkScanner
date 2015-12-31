#!/usr/bin/evn python
#-*- coding:utf-8 -*-
#*******************************************************
# Copyright (C) 2014 - All Rights Reserved
# Author(s): BlackYe_. <hswjzhang@gmail.com>
# Time:2014-04-04
#
# Function: 单个IP C端检测
#******************************************************

from DomainAnalysis.domain_plugin import DomainPlugin
from DomainAnalysis.utils.common import getCrangeIP

class IpCrange(DomainPlugin):

    def __init__(self, plugin_name):
        super(IpCrange, self).__init__(plugin_name)

    def start(self, domain):
        super(IpCrange, self).start(domain)
        self.result.update({'ip':[getCrangeIP(domain)]})

        super(IpCrange, self).complete()
        return self.result