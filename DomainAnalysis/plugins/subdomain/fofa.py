#!/usr/bin/python
#-*- coding:utf-8 -*-

__author__ = 'BlackYe'

import sys
import urllib
import urllib2
import cookielib
import re
from bs4 import BeautifulSoup
from os import path
from DomainAnalysis.utils.common import is_vaild_ip
from DomainAnalysis.utils.common import getCrangeIP

class FofaDomain():
	def __init__(self, domain):
		self.login_url = 'http://fofa.so/users/sign_in'  #登录接口地址
		self.login_username = 'ahaha_321@163.com'
		self.login_password = '1qaz2wsx'
		self.interface_url = 'http://fofa.so/lab/ips'  	#查询接口地址
		self.searchAuth_token = None  #授权cookie
		self.topDomain = domain
		self.retlist = {}

	def bLogin(self):
		'''
		登录fofa 接口, 判断是否登录成功
		'''
		cookiejar = cookielib.CookieJar()
		opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookiejar))
		user_agent = "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; Mozilla/4.0 \
	                    (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 2.0.507"
		opener.addheaders = [('User-Agent', user_agent)]
		urllib2.install_opener(opener)

		auth_token = self.get_auth_token(self.login_url)
		if auth_token is not None:
			#print '[+] Start search interface....'
			values = {'authenticity_token':auth_token,
					  'user[login]':self.login_username,
					  'user[password]':self.login_password,
					  'user[remember_me]':'1',
					  'commit':'登录'
			}
			post_data = urllib.urlencode(values)
			req = urllib2.Request(self.login_url)
			resp = urllib2.urlopen(req, post_data)
			login_result = resp.read()
			blogin = re.search(r'登录成功', login_result)
			if blogin is not None:
				#print '[+] 登录成功!'
				nick_name = re.search(r'</span>-->(.*)<b class="caret">', login_result)
				if nick_name is not None:
					#print '[+] nickname is:%s' % nick_name.group(1)
					return True
				else:
					#print '[-] not found nickname!'
					return False
		else:
			#print '[-] Login auth_token is not Found!'
			return False


	def get_auth_token(self, url):
		'''
		获取fofa token
		'''
		try:
			req = urllib2.urlopen(url, timeout = 10)
			soup = BeautifulSoup(req)
			csrf_token = soup.findAll(attrs={"name":"authenticity_token"})
			if len(csrf_token) == 1:
				m = re.search("value=\"(.*)\"", str(csrf_token[0]))
				if m:
					return m.group(1)
				else:
					#print '[-] search token is error!'
					return None
			else:
				#print '[-] Not Found From Token!'
				return None
		except Exception:
			#print '[-] network is timeout!'  #网络超时
			return None

	def analyse(self):
		'''
		查询对应domain下的节点IP
		'''
		if not self.bLogin():
			return None
		#print '[+] get all list ip and domains:'
		if self.searchAuth_token is None:
			self.searchAuth_token = self.get_auth_token(self.interface_url)
		if self.searchAuth_token is not None:
			try:
				para = {'authenticity_token' : self.searchAuth_token,
						'all' : 'true',
						'domain': self.topDomain}
				post_req = urllib2.Request(self.interface_url)
				post_data = urllib.urlencode(para)
				resp = urllib2.urlopen(post_req, post_data)
				result_soup = BeautifulSoup(resp.read())
				link_list = result_soup.findAll('a', attrs={'target':'_blank'})
				ip_list = []
				url_list = []
				for link in link_list:
					if is_vaild_ip(link.get_text()):
						ip_list.append(getCrangeIP(link.get_text()))
					else:
						url_list.append(link.get_text())
				self.retlist = {'ip':list(set(ip_list)), 'domain':list(set(url_list))}
			except Exception:
				return None
		else:
			return None
		return self.retlist


if __name__ == '__main__':
	if len(sys.argv) < 2:
		#Usage()
		exit()
	else:
		rootDomain = FofaDomain('iqiyi.com')
		rootDomain.analyse()
		print rootDomain.retlist
