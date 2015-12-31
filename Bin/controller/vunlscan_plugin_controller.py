#!/usr/bin/env python
#coding:utf-8

'''
漏洞插件扫描
'''

import subprocess
from os import path

here = path.split(path.abspath(__file__))[0]
project_path = path.abspath(path.join(here, '../../'))
#plugin path
plugin_script_path = path.abspath(path.join(project_path, 'Plugins'))

def portcrack_dispath():
	portcark_plugin_path = path.abspath(path.join(plugin_script_path, 'PortCrack','workplugin.py'))
	cmdline = 'python %s' % (portcark_plugin_path)
	portcrack_proc = subprocess.Popen(cmdline, shell=True)

def webpathscan_dispath():
	webpathscan_plugin_path = path.abspath(path.join(plugin_script_path, 'WebPathScan','workplugin.py'))
	cmdline = 'python %s' % (webpathscan_plugin_path)
	webpathscan_proc = subprocess.Popen(cmdline, shell=True)

def systemvul_dispath():
	systemvul_plugin_path = path.abspath(path.join(plugin_script_path, 'SystemVul','workplugin.py'))
	cmdline = 'python %s' % (systemvul_plugin_path)
	systemvul_proc = subprocess.Popen(cmdline, shell=True)

def webapp_dispath():
	webapp_plugin_path = path.abspath(path.join(plugin_script_path, 'WebApplication','workplugin.py'))
	cmdline = 'python %s' % (webapp_plugin_path)
	webapp_proc = subprocess.Popen(cmdline, shell=True)


