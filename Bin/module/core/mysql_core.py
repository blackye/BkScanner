#!/usr/bin/evn python
#-*- coding:utf-8 -*-
#*******************************************************
# Copyright (C) 2014 - All Rights Reserved
# Author(s): BlackYe_Sec. <hswjzhang@gmail.com>
# Time:2014-04-04
#
# Function: Encapsulation python MySQLdb action class
#******************************************************

import sys
import MySQLdb
from config.logger import logger

class MySqldb(object):
	def __init__(self, host, user, passwd, db ,port = 3306):
		self.__host  	= host
		self.__port 	= port
		self.__user 	= user
		self.__passwd 	= passwd
		self.__db       = db
		self.__conn     = None
		self.__cursor   = None

	def __isMysqlDb(self):
		'''
		判断mysqldb模块是否被载入
		'''
		module_name = 'MySQLdb'
		if module_name not in sys.modules:		
			try:
				__import__(module_name)
			except ImportError:   #导入模块失败，请检查是否安装
				return False
		return True

	def createConnection(self):
		'''
		创建数据库连接
		'''	
		if not self.__isMysqlDb():
			return False
		try:
			self.__conn = MySQLdb.connect(host=self.__host,port=self.__port,user=self.__user,passwd=self.__passwd,charset='utf8')
			self.__conn.select_db(self.__db)
		except MySQLdb.Error,e:
			logger.error('[-]......Mysql Error:%s' % e)
			#self.__del__()
			return False
		return True
	
	def cursor(self):
		try:
			return self.__conn.cursor()
		except (AttributeError, MySQLdb.OperationalError):
			self.createConnection()
			return self.__conn.cursor()
	
	def executeUpdate(self, sql):
		'''
		对数据库进行添加，修改和删除的操作
		'''
		if sql is None:
			return False
		if self.__conn is None:
			self.createConnection()
		self.__cursor = self.cursor()
		try:
			self.__cursor.execute(sql)
			self.__conn.commit()
			return int(self.__cursor.lastrowid)
		except MySQLdb.Error, e:
			logger.error('[-].....Mysql update/insert Error:%s' % e)
			return False
	
	def executeQuery(self, sql):
		'''
		对数据库进行查询操作
		'''
		if sql is None:
			return None
		if self.__conn is None:
			self.createConnection()

		self.__cursor = self.cursor()
		try:
			self.__cursor.execute(sql)
			result = self.__cursor.fetchall()
			return result
		except MySQLdb.Error, e:
			logger.error('[-]......Mysql Error:%s' % e)
			return None

	def close(self):
		try:
			self.__conn.close()
		except MySQLdb.Error,e:
			logger.error('[-]....Mysql Error:%s' % e)


	def __del__(self):
		'''
		析构函数，关闭数据库的连接
		'''
		try:
			self.__conn.close()
		except MySQLdb.Error,e:
			logger.error('[-]....Mysql Error:%s' % e)
			
