#!/usr/bin/evn python
#-*- coding:utf-8 -*-

import os,sys
from os import path
# add the current path to sys.path
here = path.split(path.abspath(__file__))[0]
if not here:  # if it fails use cwd instead
    here = path.abspath(os.getcwd())
if not here in sys.path:
    sys.path.insert(0, here)
# add parent path
parent = path.abspath(path.join(here, '../'))
if not parent in sys.path:
    sys.path.insert(0, parent)


from Bin.module.core.mysql_core import MySqldb

mysqldb = MySqldb(host = 'sh.scaner.w.qiyi.db', user = 'scaner', passwd = 'scaner@qiyi.com', db = 'sec_qiyi' ,port = 8379)


def get_vipcard():
    with open('/home/vipcard/year_vip.txt') as f:
        for line in f.readlines():
            info =  line.strip(' \r\n').split("\t")
            serialnum = info[0]
            key =  info[1]
            sql = "insert into qiyi_vipcard(`serialnum`, `key`, `status`, `type`) values('%s', '%s', '%d', '%s')" % (serialnum, key, 1, u'年卡')
            mysqldb.executeUpdate(sql)
            #print 'serialnum:%s key:%s' % (serialnum, key)



if __name__ == '__main__':
    get_vipcard()


