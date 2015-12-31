#!/usr/bin/env python
#coding:utf-8

import threading
import Queue
import sys
import subprocess

class MedusaWork(threading.Thread):

    def __init__(self, host_queue):
        super(MedusaWork, self).__init__()
        self.medusa_script = "/usr/bin/medusa"
        self.user_dict = "/home/python/CloudScanner/Plugins/PortCrack/dic/user.txt"
        self.pass_dict = "/home/python/CloudScanner/Plugins/PortCrack/dic/password.txt"
        self.host_queue = host_queue
        self.timeout = 300
        self.lock = threading.Lock()

    def run(self):
        while True:
            if self.host_queue.qsize() > 0:
                self.host = self.host_queue.get()
                self.crack(self.host)
            else:
                break

    def crack(self, host):
        #self.host, self.port, self.module = host.split(":")
        self.host = host
        self.port = '22'
        self.module = 'ssh'
        self.command = [self.medusa_script, "-h", self.host, "-n", self.port, "-U", self.user_dict, "-P", self.pass_dict, "-e", "ns" ,"-M", self.module, "-f", "-v", "4"]

        self.proc = subprocess.Popen(self.command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.pid = self.proc.pid

        if self.timeout:
            self.timer = threading.Timer(self.timeout, self.ontimeout, (host,))
            self.timer.start()

        self.ret = self.proc.stdout.readlines()
        if len(self.ret) == 3:
            if "SUCCESS" in self.ret[2]:
                self.lock.acquire()
                print self.host, self.port, self.ret[2]
                self.lock.release()
        stdmsg, errmsg = self.proc.communicate()
        self.timer.cancel()

    def ontimeout(self, host):
        if self.proc is not None:
            self.timer.cancel()
            self.lock.acquire()
            print "medusa will be stopped because of crack [%s] time out." % host
            self.lock.release()
            self.proc.terminate()
            self.proc.kill()
            self.proc.wait()

if __name__=='__main__':

    if len(sys.argv) != 3:
        print "error"
        sys.exit(1)

    host_file = sys.argv[1]
    num_works = int(sys.argv[2])
    host_queue = Queue.Queue(0)

    hosts = ['10.121.36.137','10.121.36.140','10.121.36.138',
             '10.121.36.139','10.121.36.129','10.121.36.132',
             '10.121.36.130','10.1.14.165', '10.15.184.189',
             '10.1.31.201', '10.15.140.80']

    for host in hosts:
        host = host.strip()
        if host != "":
            host_queue.put(host)

    medusa_threads = []
    for x in range(num_works):
        medusa_threads.append(MedusaWork(host_queue))

    for medusa_thread in medusa_threads:
        medusa_thread.start()

    for medusa_thread in medusa_threads:
        medusa_thread.join()
