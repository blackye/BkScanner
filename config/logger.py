#!/usr/bin/env python
# coding=utf-8

import logging
import logging.handlers
from settings import LOG_PATH
from os import path
import datetime

class LogInfo(object):

    def __init__(self, logfile , bconsole = True):

        self.logger = logging.getLogger('bkscanner')
        self.logger.setLevel(logging.DEBUG)

        # 创建一个handler，用于写入日志文件
        filehandler = logging.handlers.TimedRotatingFileHandler(path.join(LOG_PATH, logfile), 'D', 7, 0)
        #filehandler.suffix = "%Y_%m_%d.log" # 设置后缀名称，跟strftime的格式一样
        formatter  = logging.Formatter('%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s');
        filehandler.setFormatter(formatter)
        filehandler.setLevel(logging.INFO)

        '''
           modified by BlackYe. 2014-03-17
           重定位了标准输入输出流,因此控制台日志显示没有意义。
        '''
        if bconsole:
            # 再创建一个handler，用于输出到控制台
            console = logging.StreamHandler()
            # 定义console的输出格式
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            console.setFormatter(formatter)
            console.setLevel(logging.DEBUG)
            #给logger添加handler
            self.logger.addHandler(console)

        self.logger.addHandler(filehandler)


    def debug(self, message):
        '''
        debug 调试
        :param message:
        :return:
        '''
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)


logger = LogInfo('%s.log' % datetime.date.today())