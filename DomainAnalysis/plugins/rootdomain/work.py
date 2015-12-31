#!/usr/bin/evn python
#-*- coding:utf-8 -*-
#*******************************************************
# Copyright (C) 2014 - All Rights Reserved
# Author(s): BlackYe_. <hswjzhang@gmail.com>
# Time:2014-04-04
#
# Function: 单个域名到对应C端IP检测
#******************************************************

from DomainAnalysis.domain_plugin import  DomainPlugin
from DomainAnalysis.utils.rootdomain import Domain

class RootDomain(DomainPlugin):

    def __init__(self, plugin_name):
        super(RootDomain, self).__init__(plugin_name)

    def start(self, domain):
        super(RootDomain, self).start(domain)

        result = Domain.get_domain_crange(domain)
        if result is not None:
            self.result.update({'ip':[result[1]], 'domain':[domain]})
        else:
            self.result.update({'ip':None, 'domain':[domain]})
        super(RootDomain, self).complete()
        return self.result
