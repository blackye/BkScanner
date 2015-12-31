#!/usr/bin/env python
#coding:utf-8


from Bin.lib.portscan.nmap_scan_class import NmapScan
from Bin.module.portscan_db import PortScanDB
from common.threadpool import ThreadPool
import threading, Queue, time

from config.logger import logger
from config.settings import CRACK_PORT, NOWEB_PORT, SYSVUL_PORT, DOMAIN_TYPE
from config.redis_config import WEBSCAN_KEY
from config.redis_config import PORTCRACK_KEY
from config.redis_config import SYSVUL_KEY
from config.db_settings import DOMAIN_PORT_TABLE

from common.util import taskid
from common.util import getCurTime
from common.util import test_webservice
from common.util import test_private_ip

from vunlscan_plugin_controller import webapp_dispath, webpathscan_dispath, portcrack_dispath, systemvul_dispath


class PortScanPluginController():
    '''
    端口扫描控制器
    '''
    def __init__(self, rediswork = None):
        self.cip_que = Queue.Queue(0)
        self.threadpool = None
        self.threadpool_count = 5  #线程池数
        self.ps_db = PortScanDB().db
        self.rediswork = rediswork
        self.taskid = 0

    def push_ip(self, ip, taskid):
        self.cip_que.put_nowait({'ip':ip,'taskid':taskid})

    def get_ip_cnt(self):
        return self.cip_que.qsize()

    def run(self):

        self.threadpool = ThreadPool(num_of_threads= self.threadpool_count , num_of_work= 0 , daemon = False, timeout = 30)
        while self.cip_que.qsize() > 0:
            cip_dic = self.cip_que.get_nowait()
            self.taskid = cip_dic['taskid']
            #判断是否是内网IP
            if not test_private_ip(cip_dic['ip']):
                logger.info('current scan ip %s' % cip_dic['ip'])
                nmap = NmapScan(ip = cip_dic['ip'], threads_num = 30)
                self.threadpool.add_job(nmap.run)
            else:
                logger.info('skip private ip:%s!' % cip_dic['ip'])
            time.sleep(0.5)

        if self.threadpool is not None:
            self.threadpool.wait_for_complete() #等待线程结束
            self.insert_db()
            self.threadpool = None

            logger.info('port scan over!')
            self.vulplugin_dispatch() #开启扫描插件
            logger.info('plugin start running......')

    def insert_db(self):
        '''
        结果导入数据库
        '''
        while self.threadpool.resultQueue.qsize() > 0:
            result = self.threadpool.resultQueue.get_nowait()
            for item in result:
                for port, service in item['scan_result'].iteritems():
                    if service is None or service == '':
                        service = 'unknown'
                    domainPortDic = {}
                    domainPortDic['sid'] = self.taskid
                    domainPortDic['ip']   = item['ip']
                    domainPortDic['port'] = port
                    domainPortDic['service'] = service
                    domainPortDic['first_time'] = getCurTime()
                    self.ps_db.insert_by_dict(DOMAIN_PORT_TABLE, domainPortDic)

                    #存入redis 队列
                    self.portScanDispatch(item['ip'], port)


    def portScanDispatch(self, ip, port):
        '''
        端口任务调度
        '''
        #判断当前端口是否存在Web访问
        if port not in NOWEB_PORT:
            if test_webservice(ip, port):
                self.rediswork.pushvulInfo(keyname = WEBSCAN_KEY, ip = ip, port = port, taskid = self.taskid, type = DOMAIN_TYPE[1])
        #bug修改 -----这里不能用elif啊 每个流程都需要走完才行
        if CRACK_PORT.has_key(int(port)):
            self.rediswork.pushvulInfo(keyname = PORTCRACK_KEY, ip = ip, port = port, taskid = self.taskid)
        if SYSVUL_PORT.has_key(int(port)):
            self.rediswork.pushvulInfo(keyname = SYSVUL_KEY, ip = ip, port = port, taskid = self.taskid)


    def vulplugin_dispatch(self):
        webpathscan_dispath()
        portcrack_dispath()
        systemvul_dispath()