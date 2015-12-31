#!/usr/bin/evn python
#-*- coding:utf-8 -*-
#author by:lijiejie
#https://github.com/lijiejie/subDomainsBrute/blob/master/subDomainsBrute.py

import optparse
import Queue
import sys
import dns.resolver
import threading
import time
import optparse


DNS_SERVER = ['114.114.114.114', '114.114.115.115','180.76.76.76','223.5.5.5','223.6.6.6']
NEXT_SUBS = []

class DNSBrute:
    def __init__(self, target, names_file = "domain_dic_large.txt", next_sub_file = "next_sub.txt", threads_num = 30):
        self.target = target.strip()
        self.names_file = names_file
        self.next_sub_file = next_sub_file
        self.thread_count = self.threads_num = threads_num
        self.scan_count = self.found_count = 0
        self.lock = threading.Lock()
        self.dns_servers = DNS_SERVER
        self.dns_count = len(DNS_SERVER)
        self.resolvers = [dns.resolver.Resolver() for _ in range(threads_num)]
        self._load_sub_names()
        self._load_next_sub()
        self.ip_dict = {}
        self.domain_list = {}

    def _load_sub_names(self):
        self.queue = Queue.Queue()
        with open(self.names_file) as f:
            for line in f:
                sub = line.strip()
                if sub: self.queue.put(sub)

    def _load_next_sub(self):
        next_subs = []
        with open(self.next_sub_file) as f:
            for line in f:
                sub = line.strip()
                if sub and sub not in next_subs:
                    next_subs.append(sub)
        self.next_subs = next_subs

    def _update_scan_count(self):
        self.lock.acquire()
        self.scan_count += 1
        self.lock.release()

    def _scan(self):
        thread_id = int( threading.currentThread().getName() )
        self.resolvers[thread_id].nameservers = [self.dns_servers[thread_id % self.dns_count]]    # must be a list object
        self.resolvers[thread_id].lifetime = self.resolvers[thread_id].timeout = 1.0
        while self.queue.qsize() > 0 and self.found_count < 3000:    # limit found count to 3000
            sub = self.queue.get(timeout=1.0)
            try:
                cur_sub_domain = sub + '.' + self.target
                #print cur_sub_domain
                answers = self.resolvers[thread_id].query(cur_sub_domain)
                is_wildcard_record = False
                if answers:
                    for answer in answers:
                        self.lock.acquire()
                        if answer.address not in self.ip_dict:
                            self.ip_dict[answer.address] = 1
                        else:
                            self.ip_dict[answer.address] += 1
                            if self.ip_dict[answer.address] > 6:    # a wildcard DNS record 泛解析
                                is_wildcard_record = True
                        self.lock.release()
                    if is_wildcard_record:
                        self._update_scan_count()
                        continue
                    self.lock.acquire()
                    self.found_count += 1
                    ips = [answer.address for answer in answers]
                    self.domain_list[cur_sub_domain] = ips
                    self.lock.release()
                    for i in self.next_subs:
                        self.queue.put(i + '.' + sub)
            except Exception, e:
                pass
            self._update_scan_count()

        self.lock.acquire()
        self.thread_count -= 1
        self.lock.release()

    def run(self):
        self.start_time = time.time()
        for i in range(self.threads_num):
            t = threading.Thread(target=self._scan, name=str(i))
            t.setDaemon(True)
            t.start()
        while self.thread_count > 0:
            time.sleep(0.01)

        # print self.domain_list
        # print "count:%d" % len(self.domain_list)
        # for (url, ips) in self.domain_list.items():
        #     print url


    def getAvailDomain(self):
        return self.domain_list

# if __name__ == '__main__':
#
#     if len(sys.argv) < 1:
#         sys.exit(0)
#
#     d = DNSBrute(target=sys.argv[1],threads_num= 10)
#     d.run()