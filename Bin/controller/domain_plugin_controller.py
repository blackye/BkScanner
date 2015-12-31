#!/usr/bin/evn python
#-*- coding:utf-8 -*-
#*******************************************************
# Copyright (C) 2014 - All Rights Reserved
# Author(s): BlackYe_. <363612366@qq.com>
# Time:2015-01-13
#
# Function: 域名分析插件
#******************************************************

import yaml , Queue, multiprocessing, threading, time
from DomainAnalysis.plugins.dnszonetransfer.work import DnsTransWork
from config.settings import DOMAIN_PLUGINS_PATH
from config.settings import DOMAIN_PLUGINS_YAML_PATH

class DomainPluginController(object):

    def __init__(self,  domain , attack_type = None):
        self.attack_type = attack_type
        self.domain = domain
        self.domain_url = []
        self.domain_ip = []

        self.__init_process_var()


    def __init_process_var(self):
        mgr = multiprocessing.Manager()
        self.domain_url = mgr.list()
        self.domain_ip  = mgr.list()


    def plugin_init(self):
        '''
        初始化插件
        :return:
        '''
        process = []
        for yaml_config in DOMAIN_PLUGINS_YAML_PATH:
            handler = open(yaml_config + '/' + 'config.yaml')
            try:
                result = yaml.load(handler)
            except Exception:
                print 'error!'
                return

            mgr = multiprocessing.Manager()
            domain_list = mgr.list()
            ip_list = mgr.list()
            if result is not None:
                plugin_name = result['plugin_name']
                plugin_enable = result['enable']
                plugin_type = result['type']
                plugin_module = result['module_name']

                if plugin_enable == True and self.attack_type in plugin_type:
                    plugin_process = multiprocessing.Process(target = self.__plugin_resgister, args= (plugin_module, plugin_name))
                    plugin_process.daemon = True
                    process.append(plugin_process)

        for t in process:
            t.start()
        for t in process:
            t.join()

        self.domain_ip = list(set(self.domain_ip))
        self.domain_url = list(set(self.domain_url))
        # print '-----------------------------------'
        # for domain_item in self.domain_url:
        #     print domain_item
        #
        # print '-----------------------------------'
        # for ip_item in self.domain_ip:
        #     print ip_item


    def __plugin_resgister(self, plugin_module, plugin_name):
        '''
        注册插件
        :param plugin_module:
        :param plugin_name:
        :return:
        '''
        module_path = 'DomainAnalysis.plugins.%s.work' % plugin_name
        try:
            _plugin = __import__(module_path, {},{},['work'])
            _plugin_module = getattr(_plugin,plugin_module)(plugin_name)
            dic_ret = self.__plugin_run(_plugin_module)
            if dic_ret['result']['ip'] is not None:
                self.domain_url.extend(dic_ret['result']['domain'])
            if dic_ret['result']['domain'] is not None:
                self.domain_ip.extend(dic_ret['result']['ip'])
        except Exception,e:
            print 'plugin %s register error! error:%s' % (plugin_name, str(e))

    def __plugin_run(self, plugin_module):
        print '##############################'
        print '#    start %s plugin_module  #' % plugin_module
        print '##############################'

        return plugin_module.start(self.domain)
