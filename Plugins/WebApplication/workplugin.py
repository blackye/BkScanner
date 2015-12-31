#!/usr/bin/python
#coding:utf-8

'''webapplication vul插件管理'''

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
from config.redis_config import WEBAPP_KEY
import time


class WebPathPlugin(DirectoryPluginManager):

    name = "webapplication"

    def __init__(self, dirplugin = 'WebApplication',plugins=(), config={}):
        DirectoryPluginManager.__init__(self,dirplugin, plugins, config)


def Work(taskid):
    redis = RedisWork()
    webappplugin_manager = WebPathPlugin()
    webappplugin_manager.loadPlugins()
    webappplugins = webappplugin_manager.getPlugins()

    while True:
        webapp_json = redis.getvulInfo(WEBAPP_KEY)
        if webapp_json is not None:
            try:
                webappinfo = eval(webapp_json)
                for webappplugin in webappplugins:
                    webappplugin.execute_run(webappinfo['ip'], webappinfo['port'], taskid)
            except:
                continue
        else:
            time.sleep(300)
            for webappplugin in webappplugins:
                webappplugin.wait_for_complete(taskid)
            break

    #send email webpath scan over!
    #扫描完成
    sys.exit()



if __name__ == '__main__':
    if len(sys.argv) == 2:
        taskid = str(sys.argv[1])
        Work(taskid)
