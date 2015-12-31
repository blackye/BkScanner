#!/usr/bin/python
#coding:utf-8

'''SystemVul插件管理'''

import sys, random, os
from BeautifulSoup import BeautifulSoup
from os import path
import sys

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
from config.redis_config import SYSVUL_KEY
import time

class SystemVulPlugin(DirectoryPluginManager):

    name = "sysvulplugin"

    def __init__(self, dirplugin = 'SystemVul',plugins=(), config={}):
        DirectoryPluginManager.__init__(self, dirplugin, plugins, config)


def Work():
    redis = RedisWork()
    sysvulplugin_manager = SystemVulPlugin()
    sysvulplugin_manager.loadPlugins()
    sysvulplugins = sysvulplugin_manager.getPlugins()
    taskid = 0

    while True:
        sysvul_json = redis.getvulInfo(SYSVUL_KEY)
        if sysvul_json is not None:
            try:
                sysvulinfo = eval(sysvul_json)
                taskid = sysvulinfo['taskid']
                for sysvulplugin in sysvulplugins:
                    sysvulplugin.execute_run(sysvulinfo['ip'], sysvulinfo['port'], taskid)
            except:
                continue
        else:
            time.sleep(300)
            for sysvulplugin in sysvulplugins:
                sysvulplugin.wait_for_complete(taskid)
            break

    #扫描完成
    sys.exit()

if __name__ == '__main__':
    # if len(sys.argv) == 2:
    #     taskid = str(sys.argv[1])
    #     Work(taskid)
    Work()
