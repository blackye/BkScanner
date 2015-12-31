#!/usr/bin/evn python
#-*- coding:utf-8 -*-


import smtplib,sys
from email.mime.text import MIMEText
def send_mail(sub,content):
    #############
    mailto_list=["363612366@qq.com"]
    #####################

    mail_host="mail.iqiyi.com"
    mail_user="zhangqiang"
    mail_pass="P@ssw0rd1163"
    mail_postfix="qiyi.com"
    ######################
    '''''
    send_mail("aaa@126.com","sub","content")
    '''
    me = mail_user+"<"+mail_user+"@"+mail_postfix+">"
    msg = MIMEText(content,_charset='gbk')
    msg['Subject'] = sub
    msg['From'] = me
    msg['To'] = ";".join(mailto_list)
    try:
        s = smtplib.SMTP()
        s.connect(mail_host)
        s.login(mail_user,mail_pass)
        s.sendmail(me, mailto_list, msg.as_string())
        s.close()
        return True
    except Exception, e:
        print str(e)
        return False

if __name__ == '__main__':
    if send_mail(u'端口扫描结果',u'aahahahahahha'):
        print u'发送成功'
    else:
        print u'发送失败!'