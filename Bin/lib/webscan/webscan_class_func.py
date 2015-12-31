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
import subprocess
from urlparse import urlparse
from urlparse import urljoin
from exceptions import *
import sys, random, os
from BeautifulSoup import BeautifulSoup

#reload(sys)
#sys.setdefaultencoding('utf8')

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
                self.encoding = self.apparent_encoding  #这里有可能出现异常
            _content = _content.decode(self.encoding, 'replace').encode('utf8', 'replace')
            self._content = _content
        return _content
    requests.models.Response.content = property(content)
#monkey_patch()

bakfile_exts = ['.zip', '.tar','.rar','.tar.gz','.tar.bz2', '.bak', '.swp', '.1']
dir_exts = ['.zip', '.tar','.rar','.tar.gz','.tar.bz2', '.log']

no_exist_path = "not_exist_path_qiyipps/"
#no_exist_file = '%s%s' % (no_exist_path, 'webscan.php')

#字典路径
path_dic = '%s/%s' % ( os.path.abspath('../../../Bin/data/webdic'), "web_dir.dic")
file_dic = '%s/%s' % ( os.path.abspath('../../../Bin/data/webdic'), "web_path.dic")

class CrawlerStatus(object):
    '''
    WEB状态
    '''
    def __init__(self):
        self.status = {'dir':[200,403] , 'file':200}
        self.message = None
        self.info = True


class HtmlRespInfo(object):
    '''
    探测目录、文件对象信息
    '''

    senswords_dic = ['admin', '后台管理', '登陆', '木马', '上传']

    def __init__(self, http_code = None, html_content = None):
        self.http_code = http_code #返回状态吗
        self.html_content = html_content
        self.title = ''
        self.senswords = []  #敏感词语

        self.__get_title()
        #self.__test_sensitive()

    def __test_sensitive(self):
        '''
        探测页面存在敏感关键词
        '''
        if self.html_content is not None and self.html_content != '':
            try:
                for word in HtmlRespInfo.senswords_dic:
                    if self.html_content.find(word) != -1:
                        self.senswords.append(word)
            except:
                pass

    def __get_title(self):
        '''
        获取标题
        '''
        if self.html_content is not None and self.html_content != '':
            try:
                soup = BeautifulSoup(self.html_content)
                self.title = soup.title.string
            except:
                pass

    def trans(self):
        result_dic = {'http_code':self.http_code, 'title':self.title}
        return result_dic


class WebScan(object):
    '''
    web目录递归扫描
    '''
    def __init__(self, url, webdomain = True, concurrent_num=30, timeout = 5, depth= 5, proxy=False):
        self.url = url if url.startswith("http://") or url.startswith("https://") else ("http://%s" % url)
        self.webdomain = webdomain
        self.concurrent_num = concurrent_num
        self.figerinfo = ''     #web figer info
        self.timeout = timeout
        self.depth = depth  #扫描深度
        self.exist_dir_que = queue.Queue()
        self.exist_dir_cache_que = queue.Queue() #exist path cache
        self.exist_file_que = queue.Queue()
        self.exist_file_cache_list = [] #current path exist file cache
        self.exist_dir_cache_list = [] #current path exist dir cache
        self.exist_result_que = queue.Queue()
        self.dir_dic = []  #path dic
        self.file_dic = []  #file dic
        self.proxy = proxy
        self.proxy_url = []
        self.crawler_status = CrawlerStatus()
        self.vaild_threshold = {'file':20, 'dir':25}  #存在最多文件（夹）阈值

    def __load_scan_dic(self, path_dic = path_dic, file_dic = file_dic):
        '''
        加载路径探测字典
        :param path_dic:
        :param file_dic:/
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
            request = requests.get(url = self.url, timeout = self.timeout, headers=HTTP_HEADERS, allow_redirects = True, verify = False)
            respinfo = HtmlRespInfo(request.status_code, request.text)
            self.exist_result_que.put_nowait({'respinfo':respinfo.trans(), 'url':self.url})
            try:
                self.__whatweb() #获取网站指纹
            except Exception,e:
                print 'error:' % str(e)
            return True
        except Exception,e:
            return False


    def __whatweb(self):
        '''
        获取网站指纹信息
        '''

        whatweb_script = '/usr/bin/whatweb --no-errors --color=never %s' % self.url
        output = subprocess.check_output(whatweb_script, shell = True)
        try:
            output = output.decode('utf-8').encode('utf-8')
        except UnicodeDecodeError:
            output = output.decode('gb2312', 'ignore').encode('utf-8', 'ignore')
        if output is not None:
            self.figerinfo = output.lstrip(self.url)

    def __request(self, path):
        '''
        http 探测
        :param crawler_url:
        :return:
        '''

        crawler_url = urljoin(self.url, path)
        if self.proxy:
            proxy_url = self.proxy_url[random.randint(0,len(self.proxy_url))]
            proxies = {urlparse(proxy_url).scheme : urlparse(proxy_url).netloc}

            try:
                _req = requests.get(crawler_url, timeout= self.timeout, headers=HTTP_HEADERS, allow_redirects = False, proxies = proxies, verify=False)
                return _req
            except:
                return None
        else:
            try:
                _req = requests.get(crawler_url, timeout= self.timeout, headers=HTTP_HEADERS, allow_redirects = False, verify = False)
                return _req
            except Exception, e:
                return None

    def __http_request(self, path, model= True):
        '''
        http 探测结果，model:True (dir) , False (file)
        :param path:
        :param model:
        :return:
        '''
        try:
            request = self.__request(path)
            if request is not None:
                #bug:存在负载均衡，根据返回的状态码得到的结果有时候会存在误差
                if (self.crawler_status.message is not None and request.headers.get("content-length") == self.crawler_status.message) \
                        or request.headers.get("content-length") == "0":  #如果不存在该文件，但是返回状态吗是200
                    return (None, False)

                respinfo = HtmlRespInfo(request.status_code, request.text)

                if model:
                    return (respinfo.trans(), respinfo.http_code in self.crawler_status.status['dir'])
                else:
                    return (respinfo.trans(), respinfo.http_code == self.crawler_status.status['file'])
            else:
                return (None, False)
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
            if link is not None:
                if len(link.history) != 0:
                    #301\302 redirect
                    self.crawler_status.message = link.headers.get("content-length")
                else:
                    if link.status_code == 200 or (link.status_code >= 301 and link.status_code < 400): #不存在的目录、路径200
                        if link.headers.get("content-length") is not None:
                            self.crawler_status.message = link.headers.get("content-length") #比较不存在目录response值
                        else:
                            self.crawler_status.info = False
                    if link.status_code == 403:
                        #任何目录都是403,这个时候就不用跑了=。=
                        self.crawler_status.info = False
                    elif link.status_code == 404:
                        #正常情况
                        pass
                    elif link.status_code == 500:  #网站错误
                        self.crawler_status.info = False
            else:
                self.crawler_status.info = False
        except requests.exceptions.ConnectionError:
            return

    def __subdir_crawler_status(self, dirpath):
        '''
        探测已存在的目录下任意不存在的目录状态
        :param dir:
        :return:
        '''
        global no_exist_path
        try:
            no_exist_subpath = '%s/%s/' % (dirpath, no_exist_path)
            link = self.__request(no_exist_subpath)
            if link is not None:
                if link.status_code == 200: #不存在的目录、路径200
                    return False
                if link.status_code == 403:
                    #任何目录都是403,这个时候就不用跑了=。=
                    return False
                elif link.status_code == 404:
                    #正常情况
                    return True
                else:
                    return True
            else:
                return False

        except requests.exceptions.ConnectionError:
            return False


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
                print "domain url %s scanner stop" % self.url
                return None
            return True
        else:
            print "domain url %s can't access" % self.url
            return None


    def __webdir_crawler_work(self, dir_suffix):
        '''
        目录爆破
        :param dir_suffix:
        :return:

        bug update:
        休正同一个目录下所有文件访问状态一样问题
        '''
        if len(self.exist_dir_cache_list) < self.vaild_threshold['dir']:  #如果该目录任何文件访问都一样，则停止访问

            respinfo_dic, baccess = self.__http_request(dir_suffix)

            if respinfo_dic is not None and baccess:
                self.exist_dir_cache_list.append({'respinfo':respinfo_dic, 'dir_suffix':dir_suffix.strip('/')})


    def webdir_crawler_schedu(self):
        '''
        web目录爆破任务调度
        :return:
        '''
        #根目录字典目录探测
        first_crack_dir_pool = pool.Pool(self.concurrent_num)
        first_crack_dir_pool.map(self.__webdir_crawler_work, ['%s/' % str(dir_dic) for dir_dic in self.dir_dic])
        self.__deal_exist_file(bModel = False)

        while not self.exist_dir_cache_que.empty():
            dir = self.exist_dir_cache_que.get_nowait()
            '''
            判断当前文件路径长度
            '''
            if len(dir.split('/')) <= self.depth:
                #Bug 修改
                #在已存在目录下探测一个绝对不存在的目录，判断状态
                if self.__subdir_crawler_status(dir):
                    dir_tmpdic = ['%s/%s/' % (dir, dir_dic) for dir_dic in self.dir_dic]
                    path_pool = pool.Pool(self.concurrent_num)
                    path_pool.map(self.__webdir_crawler_work, dir_tmpdic)
                    self.__deal_exist_file(bModel = False)


    def webfile_crawler_schedu(self):
        '''
        目录文件爆破任务调度
        :return:
        '''
        #根目录文件爆破
        self.exist_file_cache_list = []
        first_crack_file_pool = pool.Pool(self.concurrent_num)
        first_crack_file_pool.map(self.__webfile_crawler_work, self.file_dic)
        self.__deal_exist_file()

        global dir_exts
        while not self.exist_dir_que.empty() and ( self.exist_dir_que.qsize() < 20 ):
            exist_dir = '%s'  % self.exist_dir_que.get(block=True)
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
            self.__deal_exist_file()

            gevent.sleep(0)

        #所有目录文件都探测结束后，探测文件的后缀名
        #exp
        # http://www.iqiyi.com/1.php ----> http://www.iqiyi.com/1.php.1
        # http://www.iqiyi.com/data/xx.php ----> http://www.iqiyi.com/data/xx.php.swp
        #path_pool = pool.Pool(self.concurrent_num)
        #path_pool.map(self.webfileext_crawler_work, None)
        file_threads = [gevent.spawn(self.webfileext_crawler_work, i) for i in xrange(self.concurrent_num)]
        gevent.joinall(file_threads)


    def webfileext_crawler_work(self, *args):
        '''
        PHP.ASP.JSP文件备份文件自动探测
        :param args:
        :return:
        '''
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
                    self.__deal_exist_file()
                else:
                    pass
            except ValueError:
                pass


    def __webfile_crawler_work(self, file_suffix):
        '''
        探测完整web文件
        :return:
        '''
        if len(self.exist_file_cache_list) != 0:
            print len(self.exist_file_cache_list)

        # bug ---2015-12-23 -- 这里需要一个锁机制
        if len(self.exist_file_cache_list) < self.vaild_threshold['file']:  #如果该目录任何文件访问都一样，则停止访问

            respinfo_dic, baccess = self.__http_request(file_suffix, model = False)
            if respinfo_dic is not None and baccess:
                #bug --- 已解决
                #time 2015-02-28：
                #  ------如果当前目录下所有文件都存在同一特征，这时需要中断后继续下个已存在目录扫描

                #if self.exist_file_que.qsize() < 30:
                #self.exist_file_que.put_nowait(file_suffix)
                self.exist_file_cache_list.append({'respinfo':respinfo_dic, 'file_suffix':file_suffix})

                #self.exist_result_que.put_nowait({'code':http_code, 'url':urljoin(self.url,file_suffix)})


    def __deal_exist_file(self, bModel = True):
        '''
        探测有效文件(夹)放入结果集中
        bModel: true: exist file
                false: exist folder
        bug update:2015-03-03
        :return:
        '''
        if bModel:  #file
            if len(self.exist_file_cache_list) != self.vaild_threshold['file']:  #有效文件数目在阈值内
                for file in self.exist_file_cache_list:
                    self.exist_file_que.put_nowait(file['file_suffix'])
                    self.exist_result_que.put_nowait({'respinfo':file['respinfo'], 'url':urljoin(self.url,file['file_suffix'])})
            self.exist_file_cache_list = []
        else:   #folder
            if len(self.exist_dir_cache_list) != self.vaild_threshold['dir']:
                for dir in self.exist_dir_cache_list:
                    #if dir['respinfo']['http_code'] != 200: #排除目录遍历
                    self.exist_dir_cache_que.put_nowait(dir['dir_suffix'].strip('/'))
                    self.exist_dir_que.put_nowait(dir['dir_suffix'].strip('/'))
                    self.exist_result_que.put_nowait({'respinfo':dir['respinfo'], 'url':urljoin(self.url,dir['dir_suffix'].strip('/'))})
            self.exist_dir_cache_list = []  #clear list


    def run(self, *args, **kwargs):

        if self.__init_plugin() is not None:

            gevent.joinall([
                                gevent.spawn(self.webdir_crawler_schedu),
                                gevent.spawn(self.webfile_crawler_schedu)
                            ])

            result_list = []


            while not self.exist_result_que.empty():
                result = self.exist_result_que.get_nowait()
                #print 'code:%s,url:%s,title:%s' % (result['respinfo']['http_code'], result['url'], result['respinfo']['title'])
                result_list.append({'http_code':result['respinfo']['http_code'], 'url':result['url'], 'title':result['respinfo']['title']})

            return {'url':self.url, 'figerinfo':self.figerinfo, 'result_list':result_list}

            print '[done]domain url %s webscan over!' % self.url
        else:
            print "domain url %s webscanner init failed!" % self.url

            return None




if __name__ == '__main__':
    import os
    from os import path

    here = path.split(path.abspath(__file__))[0]
    if not here:  # if it fails use cwd instead
        here = path.abspath(os.getcwd())
    if not here in sys.path:
        sys.path.insert(0, here)
    # add parent path
    parent = path.abspath(path.join(here, '../../../'))
    if not parent in sys.path:
        sys.path.insert(0, parent)

    from config.settings import HTTP_HEADERS

    webscan = WebScan(sys.argv[1], webdomain=True, proxy=False)
    result = webscan.run()
    print result