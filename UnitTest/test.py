__author__ = 'BlackYe_Mac'


import threading, subprocess, datetime
import multiprocessing
import time

timeout = 2

def subprocess_t():

    start = datetime.datetime.now()
    process = subprocess.Popen('ping -c 10 www.baidu.com', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    while process.poll() is None:
        time.sleep(0.1)
        now = datetime.datetime.now()
        if (now - start).seconds > timeout:
            try:
                process.terminate()
                #process.kill()
                print '111111111111'
                break
            except Exception,e:
                print 'Exception:%s' % str(e)
            #return 3

    stdmsg = process.communicate()[0]
    retmsg = stdmsg.strip(' \r\n')
    #return 2



def thread_test(index, cnt):
    print subprocess_t()
    print 'xxxxxxxxxx'

    while cnt < 1000:
        print "index:%d,cnt:%d" % (index, cnt)
        cnt = cnt + 1
        time.sleep(2)

def test1():
    if 1 > 2:
        return 4

def test():

    threads = []
    for i in range(3):
        t = threading.Thread(target = thread_test, args= (i, 1))
        #t = multiprocessing.Process(target = thread_test, args=(i, 1))
        threads.append(t)

    for t in threads:
        t.start()

    for t in threads:
        t.join()

test()