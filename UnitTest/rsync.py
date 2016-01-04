#!/usr/bin/python
#-*- coding:utf-8 -*-

'''rsync未授权访问'''

import os,sys,re
import commands
import MySQLdb

UNAUTH = False

def __test_rsyncunauth(ip, data = ' '):
    '''
    验证是否存在rsync未授权访问漏洞
    :param url:
    :return:
    '''
    global UNAUTH
    (status, resp) = commands.getstatusoutput('rsync -v --password-file=rsync_dic --timeout=5 ' + ip + '::' + data)
    if status == 0: #表示获取# 到敏感信息
        if resp == '':
            return UNAUTH
        resp_dic = resp.split(' \t\n')
        for item in resp_dic:
            re_result = re.search(r'[dwrx-]{10}\s+[\d]+\s+[\d]{4}\/[\d]{1,2}\/[\d]{1,2}\s+[0-5]\d:[0-5]\d:[0-5]\d\s+(.*)', item)
            if re_result is not None:
                UNAUTH = True
                break
            if item != ' ':
                __test_rsyncunauth(ip, item[:item.find(' ')])
        return UNAUTH
    else:
        return UNAUTH

def test():
    try:
        conn=MySQLdb.connect(host='localhost',user='root',passwd='',db='BkScanner',port=3306)
        cur=conn.cursor()
        cur.execute("select ip from t_domain_port where port = '873'")
        result = cur.fetchall()
        for ip in result:
            print ip
            print 'ip:%s , result:%d' % (ip[0], __test_rsyncunauth(ip[0]))
        cur.close()
        conn.close()
    except MySQLdb.Error,e:
     print "Mysql Error %d: %s" % (e.args[0], e.args[1])


if __name__ == '__main__':
    #print __test_rsyncunauth('112.124.12.124')
    #print __test_rsyncunauth(sys.argv[1])
    test()
