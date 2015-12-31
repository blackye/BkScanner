#!/usr/bin/env python
#coding:utf-8


import nmap, sys
import threading
import Queue
from config.logger import logger

portList = [
        (21,'Ftp'),
        (21212,'Ftp'),
        (22,'SSH'),
        (2200,'SSH'),
        (23,'Telnet'),
        (25,'Smtp'),
        (69,'TFtp'),
        (79,'Finger'),
        (80,'Http'),
        (81,'unknown'),
        (110,'Pop3'),
        (135,'Location Service'),
        (137,'Netbios-NS'),
        (138,'Netbios-DGM'),
        (139,'Netbios-SSN'),
        (143,'IMAP'),
        (389,'LDAP'),
        (443,'Https'),
        (445,'Microsoft-DS'),
        (873,'Rsync'),
        (999,'unknown'),
        (1080,'QQ'),
        (1158,'ORACLE EMCTL'),
        (1433,'MSSQL'),
        (1434,'MSSQL'),
        (1723,'PPTP'),
        (1521,'Oracle'),
        (2024,'maybe FTP'),
        (2100,'Oracle XDB / FTP'),
        (3128,'squid-http'),
        (3306,'MYSQL'),
        (3307,'Maybe MYSQL'),
        (3389,'Terminal Services'),
        (4440,'rundeck'),
        (4848,'GlassFish Server Administration Console'),
        (4899,'RAdmin'),
        (5000,'synology DSM'),
        (5432,'PostGreSql'),
        (5631,'Pcanywhere'),
        (5900,'VNC'),
        (5901,'VNC'),
        (5902,'VNC'),
        (5903,'VNC'),
        (6080,'VNC'),
        (6082,'varnish'),
        (6379,'Redis'),
        (7001,'WebLogic'),
        (7071,'Zimbra Mail'),
        (8000,'JBOSS/TOMCAT/Oracle XDB'),
        (8001,'JBOSS/TOMCAT/Oracle XDB'),
        (8002,'JBOSS/TOMCAT/Oracle XDB'),
        (8008,'JBOSS/TOMCAT/Oracle XDB'),
        (8012,'RTX'),
        (8080,'JBOSS/TOMCAT/Oracle XDB'),
        (8081,'Symantec AV/Filter for MSE'),
        (8082,'Redmine'),
        (8083,'Unknow'),
        (8088,'Apache Tomcat/Coyote JSP engine'),
        (8090,'Tomcat (maybe)'),
        (8091,'Couchbase (maybe)'),
        (8092,'Couchbase (maybe)'),
        (8161,'activemq'),
        (8181,'Unknow'),
        (8443,'Tomcat SSL or Plesk or SonicWall'),
        (8649,'Ganglia'),
        (8888,'Unknow'),
        (9000,'JOnAS'),
        (9003,'Unknow'),
        (9009,'Apache Tomcat/Coyote JSP engine'),
        (9043,'WebSphere Application'),
        (9080,'WebSphere Application'),
        (9090,'WebSphere ManageTool'),
        (9188,'Unknown'),
        (9200,'Elasticsearch'),
        (9443,'websphere ssl'),
        (9990,'Jboss'),
        (10000,'Webmin'),
        (11211,'Memcached'),
        (11212,'Memcached'),
        (27017,'Mongodb (maybe)'),
        (28017,'Mongodb Web'),
        (27018,'Mongodb (maybe)'),
        (28018,'Mongodb Web'),
        (49152,'PSBlock')
        ]


def ip_format(ip):
    '''
    IP解析C段
    :param ip:
    :return:
    '''
    return ip[:ip.rfind('.') + 1]


class NmapScan(object):

    def __init__(self, ip, bCrange = True, threads_num = 20, ports = portList, argument = '-sS -Pn -v'):
        self.ip = ['%s' % ip] if not bCrange else ['%s%s' % (ip_format(ip), ip_each) for ip_each in range(1,255)]
        self.argument = '%s -p %s' % (argument, ','.join(str(port) for port in [port[0] for port in portList]))
        self.threads_num = threads_num
        self.ip_que = Queue.Queue(0)
        self.nm = nmap.PortScanner()
        self.result = []

    def run(self, *args, **kwargs):
        for ip in self.ip:
            self.ip_que.put_nowait(ip)

        threads = []
        for num in range(self.threads_num):
            thread = threading.Thread(target=self.__scan_thread)
            threads.append(thread)

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        logger.info('%s crange ip scan over!' % ip)
        return self.result


    def __scan_thread(self):
        while not self.ip_que.empty():
            ip = self.ip_que.get_nowait()
            try:
                self.nm.scan(hosts=ip, arguments=self.argument)
                port_info = {}
                if self.nm.all_hosts is not None:
                    for s in self.nm[ip]['tcp'].items():
                        if s[1]['state'] == 'open':
                            if s[1]['name'] == '' or s[1]['name'] is None:
                                port_info[s[0]] = self.__getPortService(s[0])
                            else:
                                port_info[s[0]] = s[1]['name']
                    if len(port_info) and len(port_info) != len(portList):
                        self.result.append({'ip' : ip, 'scan_result':port_info})
            except Exception,e:
                #print e
                pass  #not alive ip

    def __getPortService(self, port):
        '''
        获取端口服务类型
        :param port:
        :return:
        '''
        for item in portList:
            if str(item[0]) == str(port):
                return item[1]
        return 'Unknown'

if __name__ == '__main__':
    nm = NmapScan('123.58.167.1')
    print nm.run()
    #nm.getPortService('27017');
