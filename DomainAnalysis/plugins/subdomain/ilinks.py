#!/usr/bin/evn python
#-*- coding:utf-8 -*-
#*******************************************************
# Copyright (C) 2014 - All Rights Reserved
# Author(s): BlackYe_Sec. <hswjzhang@gmail.com>
# Time:2014-04-04
#
# Function: 批量获取子域名
#******************************************************

'''
    二级域名获取插件(i.links.com)
'''

import urllib2
import sys
from BeautifulSoup import BeautifulSoup
import socket
import time
from DomainAnalysis.utils.common import get_domain_crange

class LinksDomain():

    def __init__(self, domain):
		self.interface_url = 'http://i.links.cn/subdomain/' + domain + '.html'  #查询接口地址
		self.retlist = {}


    def analyse(self):
		try:
			req = urllib2.urlopen(self.interface_url, timeout = 20)
			soup = BeautifulSoup(req, fromEncoding="GBK")
			data = soup.findAll("div",{"class":"domain"})
			url_list = []
			ip_list = []
			for index in range(len(data)):
				soup1 = BeautifulSoup(str(data[index]));
				data1 = soup1.find('a').text
				url = data1[7:]
				ip = get_domain_crange(url)
				url_list.append(url)
				if ip is not None:
					ip_list.append(ip)

			self.retlist = {'ip':list(set(ip_list)), 'domain':list(set(url_list))}
		except Exception,e:
			self.retlist = {'ip':[], 'domain':[]}

		return self.retlist


if __name__ == '__main__':
	if len(sys.argv) < 2:
		print 'please input url!'
		sys.exit()
	else:
		domain = sys.argv[1]
		ilink = LinksDomain(domain)
		ilink.analyse()