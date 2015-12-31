#!/usr/bin/evn python
#-*- coding:utf-8 -*-

import smtplib,sys
from email.mime.text import MIMEText
from config.mail_config import MAIL_HOST, MAIL_PORT, MAIL_USER, MAIL_PASS, MAIL_POSTFIX, MAILTO_LIST
from config.logger import logger

class Mail(object):

    @classmethod
    def send(cls, sub, content):
        '''''
        send_mail("aaa@126.com","sub","content")
        '''

        me = MAIL_USER+"<"+MAIL_USER+"@"+MAIL_POSTFIX+">"
        msg = MIMEText(content,_charset='gbk')
        msg['Subject'] = sub
        msg['From'] = me
        msg['To'] = ";".join(MAILTO_LIST)
        try:
            s = smtplib.SMTP()
            s.connect(MAIL_HOST)
            s.login(MAIL_USER,MAIL_PASS)
            s.sendmail(me, MAILTO_LIST, msg.as_string())
            s.close()
            return True
        except Exception, e:
            logger.error(str(e))
            return False

if __name__ == '__main__':
    if Mail.send(u'端口扫描结果',u'aahahahahahha'):
        print u'发送成功'
    else:
        print u'发送失败!'