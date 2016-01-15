#!/usr/bin/env python
# coding=utf-8

import sys, os

VERSION = 'v1.0'


#env setting
dirname_path_func = os.path.dirname
abspath_path_func = os.path.abspath
join_path_func    = os.path.join

ROOT_PATH  = dirname_path_func(dirname_path_func(abspath_path_func(__file__)))
#-----------------------------------------------------------------------
# domain analysis
DOMAIN_PATH = join_path_func(ROOT_PATH, 'DomainAnalysis')
DOMAIN_PLUGINS_PATH = join_path_func(DOMAIN_PATH, 'plugins')
DOMAIN_PLUGINS_YAML_PATH = [join_path_func(DOMAIN_PLUGINS_PATH,'dnszonetransfer'),
                            join_path_func(DOMAIN_PLUGINS_PATH,'subdomain'),
                            join_path_func(DOMAIN_PLUGINS_PATH,'subdomainByenum'),
                            join_path_func(DOMAIN_PLUGINS_PATH,'rootdomain'),
                            join_path_func(DOMAIN_PLUGINS_PATH,'ipCrange')]

DOMAIN_DIC_PATH = join_path_func(DOMAIN_PLUGINS_PATH, 'subdomainByenum')

DATA_DIC_PATH = join_path_func(ROOT_PATH, 'Bin/data')

#-------------------------------------------------------------------------

CACHE_PATH = join_path_func(ROOT_PATH, 'cache')

LOG_PATH   = join_path_func(CACHE_PATH, 'log') #日志文件目录

PORTCRACK_CACHE = join_path_func(CACHE_PATH, 'portcrack')



#------------------------------------------------------------------------

#确定不存在WEB服务的端口
NOWEB_PORT = [
        21,
        21212,
        22,
        2200,
        23,
        25,
        69,
        79,
        110,
        135,
        137,
        138,
        139,
        143,
        389,
        445,
        873,
        1080,
        1433,
        1434,
        1723,
        1521,
        2024,
        2100,
        3306,
        3307,
        3389,
        4899,
        5000,
        5432,
        5631,
        5900,
        5901,
        5902,
        5903,
        6080,
        6379,
        27017,
        27018
]

#端口爆破
CRACK_PORT = {21  :'ftp',
              22  :'ssh',
              23  :'telnet',
              445 :'samba',
              1433:'mssql',
              1434:'mssql',
              3306:'mysql',
              3307:'mysql',
              3389:'rdp'  #medusa can't brute
              }

#系统检测
SYSVUL_PORT = {873 : 'rsync',
               443 : 'openssl',
               6379: 'redis',
               8443: 'https-alt', #ssl
               9443: 'tungsten-https', #ssl check
               9000: 'fastcgi',
               11211:'Memcached',
               27017:'Mongodb',
               27018:'Mongodb'
              }


#------------------------------------------------------------------------
#request http header 设置
HTTP_HEADERS = {"User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.8.0.11) Gecko/20070312 Firefox/1.5.0.11; BkScanner.Security",
                "Accept" : "*/*",
                "Referer": "",
                "Cookie": ' bdshare_firstime=1418272043781; mr_97113_1TJ_key=3_1418398208619;',
                "Connection":"close"}  #断开连接


#区分域名和C段IP设置
DOMAIN_TYPE = ['DOMAIN', 'IP']
