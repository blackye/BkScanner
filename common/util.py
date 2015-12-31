#!/usr/bin/evn python
#-*- coding:utf-8 -*-

'''
公共类、函数
'''

import time
import requests

requests.packages.urllib3.disable_warnings()

taskid = 0  #任务ID,数据库主键ID

def getCurTime():
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))  #当前系统时间


def make_url(ip, port):
    '''
    构造URL
    :param ip:
    :param port:
    :return:
    '''
    return '%s://%s:%s' % ('http' if str(port) != '443' else 'https', str(ip), str(port))

def test_webservice(ip, port = 80):
    '''
    是否存在WEB访问
    :param ip:
    :param port:
    :return:
    '''
    url = make_url(ip, port)
    try:
        requests.get(url = url, timeout = 5, verify = False)
        return True
    except:
        return False


def test_private_ip(ip):
    ret = ip.split('.')
    if not len(ret) == 4:
        return True
    if ret[0] == '10':
        return True
    if ret[0] == '172' and 16 <= int(ret[1]) <= 32:
        return True
    if ret[0] == '192' and ret[1] == '168':
        return True
    return False