#!/usr/bin/env python
#-*- coding:utf-8 -*-

import gevent
from gevent import monkey
from gevent import Greenlet
from gevent import pool
from gevent import queue
from gevent import event
from gevent import Timeout
from gevent import threadpool


monkey.patch_all()
import requests
import logging
import sys

def monkey_patch():
    '''
    requests库中文乱码补丁
    '''
    prop = requests.models.Response.content
    def content(self):
        _content = prop.fget(self)
        if self.encoding == 'ISO-8859-1':
            encodings = requests.utils.get_encodings_from_content(_content)
            if encodings:
                self.encoding = encodings[0]
            else:
                self.encoding = self.apparent_encoding
            _content = _content.decode(self.encoding, 'replace').encode('utf8', 'replace')
            self._content = _content
        return _content
    requests.models.Response.content = property(content)

file_suffix_dic = []
menu_prefix_dic = []

exist_menu = queue.Queue()
exist_menu_cache = queue.Queue()
exist_file = queue.Queue()
exist_file_cache = queue.Queue()

b30xSign = False
error_url = None

logger = logging.getLogger("webscan")
logger.setLevel(logging.DEBUG)
hd = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
hd.setFormatter(formatter)
logger.addHandler(hd)

def get_dic():
    global file_suffix_dic, menu_prefix_dic
    with open('web_dir.dic', 'r') as file:
        menu_prefix_dic = [each.strip(' \r\n') for each in file.readlines()]
        #print menu_prefix_dic
    file.close()
    with open('web_path.dic', 'r') as file:
        file_suffix_dic = [each.strip(' \r\n') for each in file.readlines()]
        #print file_suffix_dic
    file.close()

def crack_file(url):
    '''
    爆破完整文件路径
    :return:
    '''
    try:
        s = requests.get(url, timeout = 3)
        #print url
        if b30xSign:
            try:
                if s.url != error_url:
                    exist_file.put_nowait(url)
                    #print url
            except:
                logger.error('crack error!')
        else:
            if s.status_code == 403 or s.status_code == 200:
                exist_file.put_nowait(url)
                #print url
    except:
        return None
    pass

def crack_path_type(url):
    try:
        s = requests.get(url, timeout = 3)
        #print url
        if b30xSign:
            try:
                if s.url != error_url:
                    exist_menu.put_nowait(url)
                    exist_menu_cache.put_nowait(url)
                    #print url
            except:
                logger.error('crack error!')
        else:
            if s.status_code == 403 or s.status_code == 200:
                exist_menu.put_nowait(url)
                exist_menu_cache.put_nowait(url)
                #print url
    except:
        return None

def crack_path(url):

    while not exist_menu.empty():
        menu_url = exist_menu.get_nowait()
        target_url_menu = ['%s/%s' % (menu_url, menu) for menu in menu_prefix_dic]

        concurrent_num = 20
        path_pool = pool.Pool(concurrent_num)
        path_pool.map(crack_path_type, target_url_menu)

        #-------- 同时开启爆破路径文件-------
        target_url_file = ['%s/%s' % (menu_url, file_path) for file_path in file_suffix_dic]
        file_pool = pool.Pool(concurrent_num)
        file_pool.map(crack_file, target_url_file)

def get_robots(url):
    '''
    先获取robots
    :param url:
    :return:
    '''
    s = requests.get('%s/robots.txt' % url, timeout = 3)
    if s.status_code != 200:
        return
    else:
        print s.content


def no_exist_test(url):
    '''
    爆破目录
    :return:
    '''
    try:
        no_exist_url_path = '%s/%s' % (url, 'not_exist_path_qiYIpps+++')
        link = requests.get(no_exist_url_path, allow_redirects = True, timeout=3)
        if len(link.history) != 0:
            #301\302 redirect
            error_url = link.url
            return [True, error_url]
        else:
            return [False, None]
    except requests.exceptions.ConnectionError:
        logger.error("can't  connect the target url")
        return [False, None]

def main(url):

    global menu_prefix_dic, b30xSign, error_url
    get_dic()
    result = no_exist_test(url)
    if result[0]:
        error_url = result[1]
        b30xSign = True

    urls = ['%s/%s' % (url , menu) for menu in menu_prefix_dic]

    concurrent_num = 20
    work_pool = pool.Pool(concurrent_num)
    work_pool.map(crack_path_type, urls)

    logger.info('[done]..........')
    #while not exist_menu.empty():
    #    print exist_menu.get_nowait()


    crack_path_pool = pool.Pool()
    for x in xrange(20):
        crack_path_pool.spawn(crack_path, url)


    crack_path_pool.join()
    logger.info('--------exist path----------')
    while not exist_menu_cache.empty():
        print exist_menu_cache.get_nowait()

    logger.info('--------exist file----------')
    while not exist_file.empty():
        print exist_file.get_nowait()


if __name__ == '__main__':
    main(sys.argv[1])
