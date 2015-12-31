#!/usr/bin/evn python
#-*- coding:utf-8 -*-
#*******************************************************
# Copyright (C) 2014 - All Rights Reserved
# Author(s): BlackYe_. <hswjzhang@gmail.com>
# Time:2014-04-04
#
# Function: 域传送漏洞检测
#******************************************************

from DomainAnalysis.domain_plugin import  DomainPlugin
from dnsenum import DnsEnum
from DomainAnalysis.utils.rootdomain import Domain
from config.logger import logger

class DnsTransWork(DomainPlugin):

    def __init__(self, plugin_name):
        super(DnsTransWork, self).__init__(plugin_name)

    def start(self, domain):
        super(DnsTransWork, self).start(domain)
        dnscheck = DnsEnum(domain)
        dnscheck.getEachDnsInfo()
        ip_list = []
        url_list = []
        if dnscheck.getDnsEnumRet().retcode:
            for item in dnscheck.getDnsEnumRet().retlist:
                url_list.append(item['domain'])
                if item['ip'] is not None:
                    ip_list.append(item['ip'])
            logger.info('domain %s exists DNS domain transfer vul!' % domain)
        else:
            logger.info('domain %s Not exists DNS domain transfer vul!' % domain)
        self.result = {'ip':list(set(ip_list)), 'domain': list(set(url_list))}
        super(DnsTransWork, self).complete()
        return self.result