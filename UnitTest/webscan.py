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
from urlparse import urlparse
from urlparse import urljoin
import logging
import sys, random

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


logger = logging.getLogger("webscan")
logger.setLevel(logging.DEBUG)
hd = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
hd.setFormatter(formatter)
logger.addHandler(hd)

bakfile_exts = ['.zip', '.tar','.rar','.tar.gz','.tar.bz2', '.bak', '.swp', '.1']
dir_exts = ['.zip', '.tar','.rar','.tar.gz','.tar.bz2', '.log']

no_exist_path = "not_exist_path_qiYIpps+++/"
#no_exist_file = '%s%s' % (no_exist_path, 'webscan.php')


class CrawlerStatus(object):
    '''
    WEB状态
    '''
    def __init__(self):
        self.status = {'dir':[200,403] , 'file':200}
        self.message = None
        self.info = True


class WebScan(object):
    '''
    web目录扫描
    '''
    def __init__(self, url, webdomain = True, concurrent_num=20, timeout = 3, depth=6, proxy=False):
        self.url = url if url.startswith("http://") or url.startswith("https://") else ("http://%s" % url)
        self.webdomain = webdomain
        self.concurrent_num = concurrent_num
        self.timeout = timeout
        self.depth = depth
        self.exist_dir_que = queue.Queue()
        self.exist_dir_cache_que = queue.Queue() #exist path cache
        self.exist_file_que = queue.Queue()
        self.exist_result_que = queue.Queue()
        self.dir_dic = []  #path dic
        self.file_dic = []  #file dic
        self.proxy = proxy
        self.proxy_url = []
        self.crawler_status = CrawlerStatus()

    def __load_scan_dic(self, path_dic = 'web_dir.dic', file_dic = 'web_path.dic'):
        '''
        加载路径探测字典
        :param path_dic:
        :param file_dic:
        :return:
        '''
        with open(path_dic, 'r') as file:
            self.dir_dic = list(set([each.strip(' \r\n') for each in file.readlines()]))
        file.close()

        with open(file_dic, 'r') as file:
            self.file_dic = list(set([each.strip(' \r\n') for each in file.readlines()]))
            if self.webdomain: #域名形式 www.baidu.com.tar.gz
                self.file_dic.extend(['%s%s' % (urlparse(self.url).netloc, webfile) for webfile in dir_exts])
        file.close()

    def load_proxylist(self, proxy_file='webproxy.txt'):
        '''
        加载代理字典
        :param proxy_file:
        :return:
        '''
        with open(proxy_file, 'r') as file:
            self.proxy_url = list(set([each.strip(' \r\n') for each in file.readlines()]))
        file.close()

    def __burlaccess(self):
        '''
        判断目标URL是否可以访问
        :return:
        '''
        try:
            requests.get(self.url, timeout=4)
            return True
        except:
            return False

    def __request(self, path):
        '''
        http 探测
        :param crawler_url:
        :return:
        '''
        headers = {"User-Agent": "iqiyi&pps security webscan",
                    "Accept" : "*/*"}

        crawler_url = urljoin(self.url, path)
        if self.proxy:
            proxy_url = self.proxy_url[random.randint(0,len(self.proxy_url))]
            proxies = {urlparse(proxy_url).scheme : urlparse(proxy_url).netloc}
            return requests.get(crawler_url, timeout= self.timeout, headers=headers, proxies = proxies, verify=False)
        else:
            return requests.get(crawler_url, timeout= self.timeout, headers=headers)

    def __http_request(self, path, model= True):
        '''
        http 探测结果，model:True (dir) , False (file)
        :param path:
        :param model:
        :return:
        '''
        try:
            request = self.__request(path)
            if model:
                return (request.status_code, request.status_code in self.crawler_status.status['dir'])
            else:
                return (request.status_code, request.status_code == self.crawler_status.status['file'])
        except:
            return (None, False)

    def __crawler_status(self):
        '''
        探测一个不存在的目录和目录文件，观看返回结果
        :return:
        '''
        global no_exist_file, no_exist_path
        try:
            link = self.__request(no_exist_path)
            if len(link.history) != 0:
                #301\302 redirect
                self.crawler_status.message = link.url
            else:
                if link.status_code == 403:
                    #任何目录都是403,这个时候就不用跑了=。=
                    self.crawler_status.info = False
                elif link.status_code == 404:
                    #正常情况
                    pass

        except requests.exceptions.ConnectionError:
            return

    def __init_plugin(self):
        '''
        初始化组件
        :return:
        '''
        if self.__burlaccess():
            self.__load_scan_dic() #加载扫描字典
            if self.proxy:
                self.load_proxylist()  #加载代理字典
            self.__crawler_status() #判断扫描状态（可以继续完善）
            if not self.crawler_status.info:
                print 'stop!'
                return None
            return True
        else:
            print "can't access target url!"
            return None

    def __webdir_crawler_work(self, dir_suffix):
        '''
        目录爆破
        :param dir_suffix:
        :return:
        '''
        http_code, baccess = self.__http_request(dir_suffix)

        if http_code is not None and baccess:
            if http_code != 200: #排除目录遍历的
                self.exist_dir_cache_que.put_nowait(dir_suffix)
                self.exist_dir_que.put_nowait(dir_suffix)

            self.exist_result_que.put_nowait({'code':http_code, 'url':urljoin(self.url,dir_suffix)})


    def webdir_crawler_schedu(self):
        '''
        web目录爆破任务调度
        :return:
        '''
        #根目录字典目录探测
        first_crack_dir_pool = pool.Pool(self.concurrent_num)
        first_crack_dir_pool.map(self.__webdir_crawler_work, self.dir_dic)


        while not self.exist_dir_cache_que.empty() and ( self.exist_dir_cache_que.qsize() < 20 ):
            dir = self.exist_dir_cache_que.get_nowait()
            dir_tmpdic = ['%s/%s' % (dir, dir_dic) for dir_dic in self.dir_dic]

            path_pool = pool.Pool(self.concurrent_num)
            path_pool.map(self.__webdir_crawler_work, dir_tmpdic)


    def webfile_crawler_schedu(self):
        '''
        目录文件爆破任务调度
        :return:
        '''
        #根目录文件爆破
        first_crack_file_pool = pool.Pool(self.concurrent_num)
        first_crack_file_pool.map(self.__webfile_crawler_work, self.file_dic)

        global dir_exts

        while not self.exist_dir_que.empty() and ( self.exist_dir_que.qsize() < 20 ):
            exist_dir = '%s'  % self.exist_dir_que.get_nowait()
            file_tmpdic = ['%s/%s' % (exist_dir, file_dic) for file_dic in self.file_dic]
            #动态字典，如果该目录可以访问，exp(/data),则探测 data.tar.gz....
            try:
                pos = exist_dir.rindex("/")
                for dir_ext in dir_exts:
                    file_tmpdic.append('%s%s%s' % (exist_dir[:pos], exist_dir[pos:], dir_ext))
            except ValueError:
                file_tmpdic.extend(['%s%s' % (exist_dir, dir_ext) for dir_ext in dir_exts])

            path_pool = pool.Pool(self.concurrent_num)
            path_pool.map(self.__webfile_crawler_work, file_tmpdic)

            gevent.sleep(0)

        #所有目录文件都探测结束后，探测文件的后缀名
        #exp
        # http://www.iqiyi.com/1.php ----> http://www.iqiyi.com/1.php.1
        # http://www.iqiyi.com/data/xx.php ----> http://www.iqiyi.com/data/xx.php.swp
        #path_pool = pool.Pool(self.concurrent_num)
        #path_pool.map(self.webfileext_crawler_work)
        file_threads = [gevent.spawn(self.webfileext_crawler_work, i) for i in xrange(self.concurrent_num)]
        gevent.joinall(file_threads)


    def webfileext_crawler_work(self, *args):

        global bakfile_exts
        while not self.exist_file_que.empty():
            exist_file = self.exist_file_que.get_nowait()
            file_tmpbak = []
            try:
                ext_pos = exist_file.rindex(".")
                if exist_file[ext_pos:] in ['.php', '.asp', '.jsp']:
                    for bakfile_ext in bakfile_exts:
                        file_tmpbak.append('%s%s%s' % (exist_file[:ext_pos], exist_file[ext_pos:], bakfile_ext))
                    work_pool = pool.Pool(self.concurrent_num)
                    work_pool.map(self.__webfile_crawler_work, file_tmpbak)
                else:
                    pass
            except ValueError:
                pass


    def __webfile_crawler_work(self, file_suffix):
        '''
        探测完整web文件
        :return:
        '''
        http_code, baccess = self.__http_request(file_suffix, model = False)
        if http_code is not None and baccess:
            if self.exist_file_que.qsize() < 50:
                self.exist_file_que.put_nowait(file_suffix)

                self.exist_result_que.put_nowait({'code':http_code, 'url':urljoin(self.url,file_suffix)})



    def run(self):
        if self.__init_plugin() is not None:

            gevent.joinall([
                                gevent.spawn(self.webdir_crawler_schedu),
                                gevent.spawn(self.webfile_crawler_schedu)
                            ])

            logger.info('[done]..........')

            while not self.exist_result_que.empty():
                result = self.exist_result_que.get_nowait()
                if result['code'] == 200:
                    print result['url']
        else:
            print 'init failed!'

if __name__ == '__main__':
    url = sys.argv[1]
    webscan = WebScan(url, webdomain=False, proxy=False)
    webscan.run()