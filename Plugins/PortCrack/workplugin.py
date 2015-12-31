#!/usr/bin/python
#coding:utf-8

'''端口爆破插件管理'''

import sys, random, os, time
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
from config.redis_config import PORTCRACK_KEY
from config.logger import logger

class PortCrackPlugin(DirectoryPluginManager):

    name = "PortCrackPlugin"

    def __init__(self, dirplugin = 'PortCrack',plugins=(), config={}):
        DirectoryPluginManager.__init__(self, dirplugin, plugins, config)


def Work():
    redis = RedisWork()
    portcrackplugin_manager = PortCrackPlugin()
    portcrackplugin_manager.loadPlugins()
    portcrackplugins = portcrackplugin_manager.getPlugins()
    taskid = 0

    while True:
        print '------   port crack -------'
        port_json = redis.getvulInfo(PORTCRACK_KEY)
        if port_json is not None:
            try:
                portinfo = eval(port_json)
                print portinfo
                taskid = portinfo['taskid']
                for portcrackplugin in portcrackplugins:
                    portcrackplugin.execute_run(portinfo['ip'], portinfo['port'], taskid)
                time.sleep(0.5)
            except Exception,e:
                print e
                continue
        else:
            time.sleep(300) #等待5分钟后结束所有线程
            for portcrackplugin in portcrackplugins:
                portcrackplugin.async_deal_into_db(taskid)
            break

    logger.info('[done] port crack done!')
    sys.exit()

if __name__ == '__main__':
    # if len(sys.argv) == 2:
    #     taskid = str(sys.argv[1])
    #     Work(taskid)
    Work()