#!/usr/bin/env python
# coding=utf-8

#describe database table
DOMAIN_IP_TABLE     = 't_domain_ip'
DOMAIN_PORT_TABLE   = 't_domain_port'
DOMAIN_SCAN_TABLE   = 't_domain_scan'
DOMAIN_URL_TABLE    = 't_domain_url'
IISPUTVUL_TABLE     = 't_iisput_vul'
PORTCRACK_TABLE     = 't_portcrack'
SYSVUL_TABLE        = 't_sys_vul'
WEBVUL_TABLE        = 't_web_vulurl'
WEBIPVUL_TABLE      = 't_webip_vulurl'

class MYSQL_DB_SETTING():
    def __init__(self):
        self.HOST = '127.0.0.1'
        self.PORT = '3306'
        self.USER = 'root'
        self.PWD  = ''
        self.DATABASE = 'BkScanner'