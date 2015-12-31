#!/usr/bin/evn python
#-*- coding:utf-8 -*-

from IPy import IP
import socket , re
from rootdomain import Domain

SCANNER_TYPE = ['ipCrange', 'subdomain', 'rootdomain', 'intradomain']

def is_vaild_ip(ip_str):
    try:
        IP(ip_str)
        return True
    except ValueError:
        return False

def getCrangeIP(ip):
    '''
    获取c段
    :param ip:
    :return:
    '''
    if is_vaild_ip(ip):
        return ip[:ip.rindex('.')+1] + '0'
    else:
        return None

def is_intra_ip(ip_str):
    '''
    判断是否是内网IP
    :param ip_str:
    :return:
    '''
    ip_regx = """
        ^
        (?:
            (?: #10.0.0.0  A
            (?:10)
            \.
            (?:\d{1,2}|1\d\d|2[0-4]\d|25[0-5])
            \.
            (?:\d{1,2}|1\d\d|2[0-4]\d|25[0-5])
            \.
            (?:\d{1,2}|1\d\d|2[0-4]\d|25[0-5])
            )
            |
            (?: #172.16.0.0 -- 172.31.0.0 B
            (?:172)
            \.
            (?:1[6-9]|2[0-9]|3[0-1])
            \.
            (?:\d{1,2}|1\d\d|2[0-4]\d|25[0-5])
            \.
            (?:\d{1,2}|1\d\d|2[0-4]\d|25[0-5])
            )
            |
            (?: #192.168.0.0 C
            (?:192)
            \.
            (?:168)
            \.
            (?:\d{1,2}|1\d\d|2[0-4]\d|25[0-5])
            \.
            (?:\d{1,2}|1\d\d|2[0-4]\d|25[0-5])
            )
            |
            127\.0\.0\.1
        )
        $
        """
    result = True if re.search(ip_regx, ip_str, re.X) else False
    return result

def is_vaild_url(url_str):
    url_regx = """
            ^
           (?:http(?:s)?://)? #protocol
           (?:[\w]+(?::[\w]+)?@)? #user@password
           ([-\w]+\.)+[\w-]+(?:.)? #domain
           (?::\d{2,5})? #port
           (/?[-:\w;\./?%&=#]*)? #params
            $
        """
    result = True if re.search(url_regx, url_str, re.X) else False
    return result

def get_domain_type(domain):
    '''
    type: 1 --- iqiyi.com (subdomain)  #对整个根域名下的域名扫描
           2 ---  210.187.192.1 (ip)  #对C段扫描
           3 --- www.iqiyi.com (rootdomain)  #对单个域名扫描
    '''
    if is_vaild_ip(domain):
        return SCANNER_TYPE[0]
    elif is_vaild_url(domain):
        format_domain = Domain.url_format(domain)
        root_domain = Domain.get_root_domain(format_domain)
        if root_domain == '':   #这里可以判断为内网域名(这里就不能用接口查询子域名了)
            if format_domain != domain:
                return SCANNER_TYPE[2]
            else:
                return SCANNER_TYPE[3]
        if root_domain != domain:
            return SCANNER_TYPE[2]
        else:
            return SCANNER_TYPE[1]

def get_domain_crange(domain):
    '''
     获取对应域名下的C段IP
    :param domain:
    :return:
    '''
    bAliveResult = Domain.is_domain_alive(domain)
    if bAliveResult[0]:
        return getCrangeIP(bAliveResult[1])
    else:
        return None