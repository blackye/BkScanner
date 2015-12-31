#!/usr/bin/evn python
#-*- coding:utf-8 -*-
#*******************************************************
# Copyright (C) 2014 - All Rights Reserved
# Author(s): BlackYe_. <363612366@qq.com>
# Time:2015-01-13
#
# Function: 域名分析控制器
#******************************************************

import os, time, json
from os import path
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

# add the current path to sys.path
here = path.split(path.abspath(__file__))[0]
if not here:  # if it fails use cwd instead
    here = path.abspath(os.getcwd())
if not here in sys.path:
    sys.path.insert(0, here)
# add parent path
parent = path.abspath(path.join(here, '../../'))
if not parent in sys.path:
    sys.path.insert(0, parent)

from DomainAnalysis.utils.common import get_domain_type
from common.util import getCurTime
from domain_plugin_controller import DomainPluginController
from Bin.module.domain_db import DomainDB
from Bin.lib.activemq.activemq_class import ActiveMQProducer
from Bin.lib.activemq.activemq_class import ActiveMQConsumer
from Bin.lib.rediswork.rediswork_class import RedisWork
from Bin.controller.portscan_plugin_controller import PortScanPluginController
from config.logger import logger
from config.redis_config import WEBSCAN_KEY
from config.db_settings import DOMAIN_URL_TABLE, DOMAIN_IP_TABLE, DOMAIN_SCAN_TABLE
from config.settings import DOMAIN_TYPE



def domain_analyse_start(target):
    '''
    C段查询与子域名收集
    :param target:
    :return:
    '''
    domain = target
    domain_type = get_domain_type(domain)
    domain_plugin_ctrl = DomainPluginController(domain,domain_type)
    domain_plugin_ctrl.plugin_init()

    #发送到各个扫描节点中去并存入数据库
    db_core = DomainDB().getConn()
    producer = ActiveMQProducer()

    domainscan_dic = {}
    domainscan_dic['domain'] = domain
    domainscan_dic['scan_type'] = 'subdomain'
    domainscan_dic['first_time'] = getCurTime()
    taskid = db_core.insert_by_dict(DOMAIN_SCAN_TABLE, domainscan_dic) #获取当前的任务ID
    for domain_item in domain_plugin_ctrl.domain_url:
        domainUrlDic = {}
        domainUrlDic['sid'] = taskid
        domainUrlDic['subdomain'] = domain_item
        domainUrlDic['active'] = 1
        domainUrlDic['first_time'] = getCurTime()
        db_core.insert_by_dict(DOMAIN_URL_TABLE, domainUrlDic)

        #send activemq message
        domain_json = json.dumps({'type':DOMAIN_TYPE[0], 'url':domain_item, 'taskid':taskid})
        producer.send2msg(domain_json, 'scan_info')

    for ip_item in domain_plugin_ctrl.domain_ip:
        ipUrlDic = {}
        ipUrlDic['sid'] = taskid
        ipUrlDic['ips'] = ip_item
        ipUrlDic['first_time'] = getCurTime()
        db_core.insert_by_dict(DOMAIN_IP_TABLE, ipUrlDic)

        cip_json = json.dumps({'type': DOMAIN_TYPE[1], 'ip':ip_item, 'taskid':taskid})
        producer.send2msg(cip_json, 'scan_info')

    logger.info('%s domain analyse done..' % domain)
    #关闭activemq producer
    producer.close()
    db_core.close()
    #发送邮件
    pass


def getDomainByTxt():
    '''
    获取指定domain信息
    :return:
    '''




def run_portscan_plugin():
    '''
    端口扫描插件
    :return:
    '''
    desc = 'scan_info'
    consumer = ActiveMQConsumer()
    consumer.receivemsg(desc)
    #redis
    rediswork = RedisWork()

    portscan_plugin = PortScanPluginController(rediswork)  #端口扫描

    while True:
        try:
            message = consumer.listener.msg_que.get(block = False)
            scan_json = json.loads(message)
            if scan_json['type'] == DOMAIN_TYPE[0]:
                print scan_json['url']
                rediswork.pushvulInfo(keyname = WEBSCAN_KEY, ip = scan_json['url'], port = 80, taskid = scan_json['taskid'], type = DOMAIN_TYPE[0])
            elif scan_json['type'] == DOMAIN_TYPE[1]:
                print scan_json['ip']
                portscan_plugin.push_ip(ip = scan_json['ip'], taskid = scan_json['taskid'])
        except Exception,e:
            if portscan_plugin.get_ip_cnt() > 0:
                break
            #logger.error(str(e))

        time.sleep(0.1)

    logger.info('port scan plugin start working!')
    portscan_plugin.run() #开启端口扫描线程


if __name__ == '__main__':
    url = sys.argv[1]
    type = sys.argv[2]
    if type == '1':
        domain_analyse_start(url)
    else:
        run_portscan_plugin()
