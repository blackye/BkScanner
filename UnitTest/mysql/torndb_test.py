#!/usr/bin/python
#-*- conding:utf-8 -*-



import torndb

db = torndb.Connection(host = "127.0.0.1:3306", database= "CloudScanner", user="root", password="xxxxxx")

sysvul = {}
sysvul['sid'] = 0
sysvul['ip'] = '127.0.0.1'
sysvul['port'] = 9200

ret = db.insert_by_dict("t_sys_vul", sysvul)
print ret

#sql = "select * from t_sys_vul where sid = '%s'"
#print db.query(sql, 0)

