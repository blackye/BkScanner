#!/usr/bin/env python
#coding:utf-8
import os, sys, socket, struct, select, time
import Queue
import threading
import random
# From /usr/include/linux/icmp.h; your milage may vary.
'''
 ICMP , check ip is alive
'''
class IPIcmp(object):

    def __init__(self, timeout = 3):
        self.timeout = timeout
        self.ICMP_ECHO_REQUEST = 8

    def checksum(self, source_string):
        """
        I'm not too confident that this is right but testing seems
        to suggest that it gives the same answers as in_cksum in ping.c
        """
        sum = 0
        countTo = (len(source_string)/2)*2
        count = 0
        while count<countTo:
            thisVal = ord(source_string[count + 1])*256 + ord(source_string[count])
            sum = sum + thisVal
            sum = sum & 0xffffffff # Necessary?
            count = count + 2

        if countTo<len(source_string):
            sum = sum + ord(source_string[len(source_string) - 1])
            sum = sum & 0xffffffff # Necessary?

        sum = (sum >> 16)  +  (sum & 0xffff)
        sum = sum + (sum >> 16)
        answer = ~sum
        answer = answer & 0xffff

        # Swap bytes. Bugger me if I know why.
        answer = answer >> 8 | (answer << 8 & 0xff00)

        return answer

    def receive_one_ping(self, my_socket, ID):
        """
        receive the ping from the socket.
        """
        timeLeft = self.timeout
        while True:
            startedSelect = time.time()
            whatReady = select.select([my_socket], [], [], timeLeft)
            howLongInSelect = (time.time() - startedSelect)
            if whatReady[0] == []: # Timeout
                return

            timeReceived = time.time()
            recPacket, addr = my_socket.recvfrom(1024)
            icmpHeader = recPacket[20:28]
            type, code, checksum, packetID, sequence = struct.unpack(
                "bbHHh", icmpHeader
            )
            if packetID == ID:
                bytesInDouble = struct.calcsize("d")
                timeSent = struct.unpack("d", recPacket[28:28 + bytesInDouble])[0]
                return timeReceived - timeSent

            timeLeft = timeLeft - howLongInSelect
            if timeLeft <= 0:
                return

    def send_one_ping(self, my_socket, dest_addr, ID):
        """
        Send one ping to the given >dest_addr<.
        """
        dest_addr  =  socket.gethostbyname(dest_addr)

        # Header is type (8), code (8), checksum (16), id (16), sequence (16)
        my_checksum = 0

        # Make a dummy heder with a 0 checksum.
        header = struct.pack("bbHHh", self.ICMP_ECHO_REQUEST, 0, my_checksum, ID, 1)  #压包
        #a1 = struct.unpack("bbHHh",header)    #my test
        bytesInDouble = struct.calcsize("d")
        data = (192 - bytesInDouble) * "Q"
        data = struct.pack("d", time.time()) + data

        # Calculate the checksum on the data and the dummy header.
        my_checksum = self.checksum(header + data)

        # Now that we have the right checksum, we put that in. It's just easier
        # to make up a new header than to stuff it into the dummy.
        header = struct.pack("bbHHh", self.ICMP_ECHO_REQUEST, 0, socket.htons(my_checksum), ID, 1)
        packet = header + data
        my_socket.sendto(packet, (dest_addr, 1)) # Don't know about the 1

    def do_one(self, dest_addr):
        """
        Returns either the delay (in seconds) or none on timeout.
        """
        icmp = socket.getprotobyname("icmp")
        try:
            my_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
        except socket.error, (errno, msg):
            if errno == 1:
                # Operation not permitted
                msg = msg + (
                    " - Note that ICMP messages can only be sent from processes"
                    " running as root."
                )
                raise socket.error(msg)
            raise # raise the original error

        #my_ID = os.getpid() & 0xFFFF
        my_ID = random.randint(0, 10000) #这里采用随机PID替代

        self.send_one_ping(my_socket, dest_addr, my_ID)
        delay = self.receive_one_ping(my_socket, my_ID)

        my_socket.close()
        return delay

    def verbose_ping(self, dest_addr):
        """
        Send >count< ping to >dest_addr< with the given >timeout< and display
        the result.
        """
        #print "ping %s..." % dest_addr,
        try:
            delay  =  self.do_one(dest_addr)
        except socket.error:
            #print "failed. (socket error: '%s')" % e[1]
            return False

        if delay  ==  None:
            #print "failed. (timeout within %ssec.)" % timeout
            return False
        else:
            delay  =  delay * 1000
            return True
            #print "get ping in %0.4fms" % delay

    def checkAlive(self, ip):
        return self.verbose_ping(ip)


class DetectIPAlive(IPIcmp):

    def __init__(self, ip):
        super(DetectIPAlive, self).__init__()
        self.ip = ip
        self.ip_que = Queue.Queue(0)
        self.threads = 30
        self.alive_ip = []

    def single_ip_alive(self, ip = None):
        return super(DetectIPAlive, self).checkAlive(self.ip) if ip is None else super(DetectIPAlive, self).checkAlive(ip)

    def range_ip_alive(self, ipstart = 1, ipend = 255):
        '''
        C端IP扫描
        ip:127.0.0.1
        '''
        ip_prefix = self.ip[:self.ip.rfind('.')+1]
        thread_list = []
        for item in range(ipstart, ipend):
            self.ip_que.put_nowait(ip_prefix + str(item))
        for x in range(self.threads):
            t = threading.Thread(target=self.__detectIPThread)
            thread_list.append(t)

        for x in thread_list:
            x.start()

        for x in thread_list:
            x.join()

        return self.alive_ip

    def __detectIPThread(self):
        while True:
            if self.ip_que.qsize() != 0:
                try:
                    ip = self.ip_que.get(True,timeout=3)
                    if self.single_ip_alive(ip):
                        self.alive_ip.append(ip)
                    self.ip_que.task_done()
                except Queue.Empty:
                    return
                #time.sleep(0.05)
            else:
                return

if __name__ == '__main__':
    #for i in range(1,255):
    #    verbose_ping("10.1.14.%d" % i,2,1)
    #verbose_ping('167.88.114.120',2)
    s = time.time()
    ipIcmp = DetectIPAlive('167.88.114.120')
    #for item, ip in enumerate(range(0, 255)):
    #    if not ipIcmp.checkAlive('10.1.14.%d' % ip):
    #        print '10.1.14.%d' % ip
    #ipIcmp.single_ip_alive()
    result = ipIcmp.range_ip_alive(ipstart=1, ipend=255)
    print time.time() - s
    for ip in result:
        print ip
    #ipIcmp.checkAlive('167.88.114.14')