#!/usr/bin/env python
#-*- coding:utf-8 -*-

import subprocess, time, re, sys, re, os, signal, datetime
from os import path
import threading

class PortCrackBase(object):

    def __init__(self, user_dict = "ftpuser.txt", pass_dict = "password.txt"):
        self.command = None
        self.user_dict = user_dict
        self.pass_dict = pass_dict
        self.timeout = 300
        self.medusa_script = "hydra"
        self.result_dic = None

    def __get_crack_dic_path(self):
        return path.abspath('../../Bin/data/portdic')

    def crack(self, *args, **kwargs):
        ip = args[0]
        port = args[1]
        service = args[2]
        print ip

        if not ip or not port or not service:
            return None

        userpath = '%s/%s' %  (self.__get_crack_dic_path(), self.user_dict)
        passpath = '%s/%s' % (self.__get_crack_dic_path(), self.pass_dict)
        self.command = "%s %s -L %s -P %s -e ns %s -v 4 -t 10" % (self.medusa_script, ip, userpath, passpath, service)

        print self.command
        start = datetime.datetime.now()
        process = subprocess.Popen(self.command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print process.pid
        while process.poll() is None:
            time.sleep(0.1)
            now = datetime.datetime.now()
            if (now - start).seconds > self.timeout:
                try:
                    process.terminate()
                    print("medusa will be stopped because of crack [%s] time out." % ip)
                except Exception,e:
                    print 'Exception:%s' % str(e)
                    return None
                return None
        stdmsg = process.communicate()[0]
        retmsg = stdmsg.strip(' \r\n')
        print retmsg
        if "SUCCESS" in retmsg:
            m = re.findall(r'Host: (\S*).*User: (\S*).*Password: (\S*)', retmsg)
            if m and m[0] and len(m[0]) > 2:
                self.result_dic = {'ip':m[0][0], 'port':port, 'username':m[0][1], 'password':m[0][2]}
                print self.result_dic
        if process.stdout:
            process.stdout.close()
        if process.stderr:
            process.stderr.close()
        try:
            process.terminate()
            process.kill()
        except OSError,e:
            pass
        return self.result_dic


    def ontimeout(self, host):
        if self.proc is not None:
            self.timer.cancel()
            self.lock.acquire()
            print("medusa will be stopped because of crack [%s] time out." % host)
            self.lock.release()
            if self.proc.poll() != None:
                try:
                    self.proc.terminate()
                    self.proc.kill()
                    self.proc.wait()
                except Exception,e:
                    os.kill(self.pid, signal.SIGKILL)
                    print str(e)



if __name__ == '__main__':
    s = PortCrackBase()
    print s.crack('10.1.22.175', '21', 'ftp')