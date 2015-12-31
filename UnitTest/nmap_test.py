#!/usr/bin/env python
#coding:utf-8

import nmap, sys
import gevent
from gevent import pool
import threading
import Queue

ip_que = Queue.Queue(0)
nm = nmap.PortScanner()
import time

def main(host_ip):
    #nm = nmap.PortScanner()

    #ips = ['%s%s' % ('58.83.190.', str(ip)) for ip in range(1,255)]

    start_time = time.time()
    for ip in range(1,255):
        ip_que.put_nowait('%s%s' % ('58.83.190.', ip))

    #crack_pool = pool.Pool(50)
    #crack_pool.map(scan, ips)
    threads = []

    for x in range(100):
        thread = threading.Thread(target=scan)
        threads.append(thread)

    for x in threads:
        x.start()

    for x in threads:
        x.join()

    print 'done.....'
    print time.time() - start_time
        # nm.scan(hosts=host_ip,arguments='-sS -P0 -v -p 21,22,23,80,1433,3306,3389,8080')
        # #print nm['10.1.14.145'].state()
        # #print nm.scaninfo()
        # if nm.all_hosts is not None:
        #     for s in nm[host_ip]['tcp'].items():
        #         if s[1]['state'] == 'open' and s[0] == 80:
        #             print 'IP:%s  PORT:%s  service:%s' % (host_ip, s[0], s[1]['name'])


    print 'done'
    #print nm.all_hosts()

def scan():
    while not ip_que.empty():
        ips = ip_que.get_nowait()
        nm.scan(hosts=ips,arguments='-sS -P0 -v -p 21,22,23,80,873,1433,3306,3389,6379,8080,28017')
        #print nm['10.1.14.145'].state()
        #print nm.scaninfo()
        if nm.all_hosts is not None:
            for s in nm[ips]['tcp'].items():
                if s[1]['state'] == 'open':
                    print 'IP:%s  PORT:%s  service:%s' % (ips, s[0], s[1]['name'])




if __name__ == '__main__':main(sys.argv[1])