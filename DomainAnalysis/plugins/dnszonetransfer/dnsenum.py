#!/usr/bin/evn python
#-*- coding:utf-8 -*-
#*******************************************************
# Copyright (C) 2014 - All Rights Reserved
# Author(s): BlackYe_. <hswjzhang@gmail.com>
# Time:2014-04-04
#
# Function: 域传送漏洞检测
#******************************************************


import subprocess, Queue, threading, time
from DomainAnalysis.utils.common import getCrangeIP
from DomainAnalysis.utils.common import is_vaild_ip
from DomainAnalysis.utils.common import get_domain_crange
from DomainAnalysis.utils.rootdomain import Domain


class DnsEnum():

    def __init__(self, domain):
        '''
        :param domain: 格式：qiyi.domain
        :return:
        '''
        self.suffix_domain = domain
        self.dns_que = Queue.Queue(0)
        self.dns_enum = DnsEnumData()
        self.__threads = 5

    def __getDnsInfo(self):
        '''
        获取DNS信息(linux下的检测)
        :return:
        '''
        bTag = False
        process = subprocess.Popen(['dig ns %s' % self.suffix_domain], shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        for line in process.stdout.readlines():
            line = line.strip('\r\n')
            if line == '':
                continue
            if 'Query time' in line:
                bTag = False
            if bTag:
                #self.dns_list[]
                try:
                    dns_item = line.split()
                    dns_item_name = dns_item[0].rstrip('.')
                    dns_item_ip = dns_item[4]
                    #self.dns_enum.setDnsList(dns_item_name, dns_item_ip)
                    self.dns_que.put(dns_item_name)
                except IndexError:
                    print "[-] can't find dns info!"
            if  ';; ADDITIONAL SECTION:' == line:
                bTag = True
        process.wait()

    def getEachDnsInfo(self):
        '''
        获取每个DNS节点信息
        :return:
        '''
        self.__getDnsInfo()
        threads = []
        for x in range(self.__threads):
            t = threading.Thread(target=self.__checkDnsTransThread)
            threads.append(t)

        for t in threads:
            t.start()

        for t in threads:
            t.join()

    def __checkDnsTransThread(self):
        '''
        线程类，探测是否存在域传送漏洞
        '''
        while True:
            if self.dns_que.qsize() > 0:
                try:
                    dns_name = self.dns_que.get(block=False)
                    bStart = False
                    process = subprocess.Popen(['dig axfr @%s %s' % (dns_name, self.suffix_domain)], shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
                    for info in process.stdout.readlines():
                        info = info.strip('\r\n')
                        if info == '':
                            continue

                        if 'Query time' in info:
                            break

                        if 'global options: +cmd' in info:
                            bStart = True
                            continue

                        if 'Transfer failed' in info:
                            break

                        if 'connection timed out' in info:
                            break

                        if bStart:
                            try:
                                each_domain = info.split()
                                self.dns_enum.retcode = True
                                if each_domain[3] != 'SOA' or each_domain[3] != 'NS':
                                    domain_name = each_domain[0].rstrip('.')
                                    domain_ip = each_domain[4]
                                    if not self.dns_enum.checkRetInList({'domain': domain_name, 'ip':domain_ip}):
                                        if not is_vaild_ip(domain_ip):
                                            ip_range = get_domain_crange(domain_name)
                                            if ip_range is not None:
                                                domain_ip = ip_range
                                            else:
                                                domain_ip = None
                                        self.dns_enum.retlist.append({'domain': domain_name, 'ip':domain_ip})
                            except IndexError:
                                continue
                    process.wait()
                except Queue.Empty:
                    break
                time.sleep(0.1)
            else:
                break

    def getDnsEnumRet(self):
        return self.dns_enum


'''
DNS域传送结果集
'''
class DnsEnumData(object):

    def __init__(self, retcode= False):
        self.retcode = retcode  #是否存在漏洞
        self.retlist = []    #存在漏洞，返回结果集
        self.dnslist = []    #dns列表

    def checkRetInList(self, retdic):
        '''
        判断是否已经存在结果集中
        '''
        return retdic in self.retlist
