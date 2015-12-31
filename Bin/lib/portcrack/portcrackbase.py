#!/usr/bin/env python
#-*- coding:utf-8 -*-

import subprocess, time, re, sys, re, os, signal, datetime
from os import path
from config.logger import logger
import threading

class PortCrackBase(object):

    def __init__(self, user_dict = "user.txt", pass_dict = "password.txt"):
        self.command = None
        self.user_dict = user_dict
        self.pass_dict = pass_dict
        self.timeout = 300
        self.medusa_script = "/usr/bin/medusa"
        self.result_dic = None
        self.normal_exit = True

    def __get_crack_dic_path(self):
        return path.abspath('../../Bin/data/portdic')

    def crack(self, *args, **kwargs):
        ip = args[1]['ip']
        port = args[1]['port']
        service = args[1]['service']

        if not ip or not port or not service:
            return None

        userpath = '%s/%s' %  (self.__get_crack_dic_path(), self.user_dict)
        passpath = '%s/%s' % (self.__get_crack_dic_path(), self.pass_dict)
        self.command = "%s -h %s -n %s -U %s -P %s -e ns -M %s -f -v 4 -t 16 -R 0" % (self.medusa_script, ip, str(port), userpath, passpath, service)

        print self.command

        start = datetime.datetime.now()
        process = subprocess.Popen(self.command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        while process.poll() is None:
            time.sleep(0.5)
            now = datetime.datetime.now()
            if (now - start).seconds > self.timeout:
                try:
                    print process.pid
                    self.normal_exit = False
                    #process.terminate() #这里就不能在return 了
                    logger.info("medusa will be stopped because of crack [%s:%s] time out." % (ip, str(port)))
                except Exception,e:
                    logger.error('Exception:%s' % str(e))
                process.terminate() #这里就不能在return 了
                process.kill()
                time.sleep(2)
                #return None   #这里就不能在return 了,不然就成了僵尸进程

        if self.normal_exit:
            stdmsg = process.communicate()[0]
            retmsg = stdmsg.strip(' \r\n')
            if "SUCCESS" in retmsg:
                m = re.findall(r'Host: (\S*).*User: (\S*).*Password: (\S*)', retmsg)
                if m and m[0] and len(m[0]) > 2:
                    self.result_dic = {'ip':m[0][0], 'port':port, 'username':m[0][1], 'password':m[0][2]}
                    logger.info(self.result_dic)
            else:
                logger.info("Host:%s, Service:%s crack failed!" % (ip, service))
            if process.stdout:
                process.stdout.close()
            if process.stderr:
                process.stderr.close()
            # try:
            #     process.terminate()
            #     process.kill()
            # except OSError,e:
            #     pass
            return self.result_dic


    def ontimeout(self, host):
        if self.proc is not None:
            self.timer.cancel()
            self.lock.acquire()
            logger.info("medusa will be stopped because of crack [%s] time out." % host)
            self.lock.release()
            if self.proc.poll() != None:
                try:
                    self.proc.terminate()
                    self.proc.kill()
                    self.proc.wait()
                except Exception,e:
                    os.kill(self.pid, signal.SIGKILL)
                    print str(e)

