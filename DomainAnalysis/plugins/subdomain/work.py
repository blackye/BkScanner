#!/usr/bin/evn python
#-*- coding:utf-8 -*-
#*******************************************************
# Copyright (C) 2014 - All Rights Reserved
# Author(s): BlackYe_. <hswjzhang@gmail.com>
# Time:2014-04-04
#
# Function: 子域名查询接口
#******************************************************

from DomainAnalysis.domain_plugin import DomainPlugin
from fofa import FofaDomain
from ilinks import LinksDomain
from config.logger import logger

class SubDomainFindByInterface(DomainPlugin):

    def __init__(self, plugin_name):
        super(SubDomainFindByInterface, self).__init__(plugin_name)

    def start(self, domain):
        super(SubDomainFindByInterface, self).start(domain)
        #调用两个域名查询接口
        ip_list = []
        url_list = []
        #------- fofa 接口已死 ----------
        #fofa_result = FofaDomain(domain).analyse()
        #if fofa_result is not None and type(fofa_result) == dict:
        #    ip_list.extend(fofa_result['ip'])
        #    url_list.extend(fofa_result['domain'])

        ilink_result = LinksDomain(domain).analyse()
        ip_list.extend(ilink_result['ip'])
        url_list.extend(ilink_result['domain'])
        self.result = {'ip':list(set(ip_list)), 'domain':list(set(url_list))}
        logger.info('subdomain by interface found domain count:%d' % len(url_list))

        super(SubDomainFindByInterface,self).complete()
        return self.result