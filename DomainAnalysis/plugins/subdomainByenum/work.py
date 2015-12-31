#!/usr/bin/evn python
#-*- coding:utf-8 -*-
#*******************************************************
# Copyright (C) 2014 - All Rights Reserved
# Author(s): BlackYe_. <hswjzhang@gmail.com>
# Time:2014-04-04
#
# Function: 子域名枚举
#******************************************************

from DomainAnalysis.domain_plugin import DomainPlugin
from dnsdic import DNSBrute
from DomainAnalysis.utils.rootdomain import Domain
from DomainAnalysis.utils.common import getCrangeIP
from config.logger import logger
from config.settings import DOMAIN_DIC_PATH

class SubDomainFindByDit(DomainPlugin):
    def __init__(self, plugin_name):
        super(SubDomainFindByDit, self).__init__(plugin_name)

    def start(self, domain):
        super(SubDomainFindByDit, self).start(domain)
        dnsBrute = DNSBrute(domain, names_file = DOMAIN_DIC_PATH + '/domain_dic_large.txt', next_sub_file = DOMAIN_DIC_PATH + '/next_sub.txt')
        dnsBrute.run()
        ip_list = []
        url_list = []
        for (url, ips) in dnsBrute.getAvailDomain().items():
            url_list.append(url)
            for ip in ips:
                ip_list.append(getCrangeIP(ip))

        self.result = {'ip':list(set(ip_list)), 'domain': list(set(url_list))}
        logger.info('subdomain by dic found domain count:%d' % len(url_list))

        super(SubDomainFindByDit, self).complete()
        return self.result
