#!/usr/bin/python
#-*- coding:utf-8 -*-

import os, time

class DomainPlugin(object):

    def __init__(self, plugin_name):
        self.plugin_name = plugin_name
        self.result = {}

    def start(self, domain):
        self.domain = domain
        self.start_time = time.time()

    def complete(self):
        self.end_time = time.time()
        update_dic = {'plugin' : self.plugin_name,
                      'args': self.domain,
                      'start_time' : self.start_time,
                      'end_time' : self.end_time}
        if type(self.result) == dict:
            self.result = {'result' : self.result}
            self.result.update(update_dic)


