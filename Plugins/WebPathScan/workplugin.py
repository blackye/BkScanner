#!/usr/bin/python
#coding:utf-8

'''webscan插件管理'''

import sys, random, os
from BeautifulSoup import BeautifulSoup
from os import path

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


from Plugins.pluginManagerBase import DirectoryPluginManager
from Bin.lib.rediswork.rediswork_class import RedisWork
from config.redis_config import WEBSCAN_KEY
import time

class WebPathPlugin(DirectoryPluginManager):

    name = "webpathscan"

    def __init__(self, dirplugin = 'WebPathScan',plugins=(), config={}):
        DirectoryPluginManager.__init__(self,dirplugin, plugins, config)


def Work():
    redis = RedisWork()
    webplugin_manager = WebPathPlugin()
    webplugin_manager.loadPlugins()
    webplugins = webplugin_manager.getPlugins()
    taskid = 0

    while True:
        web_json = redis.getvulInfo(WEBSCAN_KEY)
        print web_json
        if web_json is not None:
            try:
                webinfo = eval(web_json)
                print webinfo
                taskid = webinfo['taskid']
                for webplugin in webplugins:
                    webplugin.execute_run(ip = webinfo['ip'], port = webinfo['port'], bdomain = webinfo['type'], taskid = taskid)
            except Exception,e:
                print str(e)
                continue
        else:
            time.sleep(300)
            for webplugin in webplugins:
                webplugin.wait_for_complete(0, taskid)
            break

    #send email webpath scan over!
    sys.exit()

if __name__ == '__main__':
    # if len(sys.argv) == 2:
    #     taskid = str(sys.argv[1])
    #     Work(taskid)
    Work()