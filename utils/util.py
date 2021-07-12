# -*- coding: UTF-8 -*-
from smtplib import SMTP_SSL
from email.mime.text import MIMEText


# 用法参考：https://www.cnblogs.com/shenh/p/14267345.html
def sendMail(message, Subject, sender_show, recipient_show, to_addrs, cc_show=''):
    '''
    :param message: str 邮件内容
    :param Subject: str 邮件主题描述
    :param sender_show: str 发件人显示，不起实际作用如："xxx"
    :param recipient_show: str 收件人显示，不起实际作用 多个收件人用','隔开如："xxx,xxxx"
    :param to_addrs: str 实际收件人
    :param cc_show: str 抄送人显示，不起实际作用，多个抄送人用','隔开如："xxx,xxxx"
    '''
    # 填写真实的发邮件服务器用户名、密码
    user = ''
    password = ''
    with open("email.conf") as f:
        for line in f.readlines():
            line = line.replace("\n", "")
            if line.startswith("username="):
                user = line.split("=")[1]
            if line.startswith("password="):
                password = line.split("=")[1]
    print(user)
    print(password)
    # 邮件内容
    msg = MIMEText(message, 'plain', _charset="utf-8")
    # 邮件主题描述
    msg["Subject"] = Subject
    # 发件人显示，不起实际作用
    msg["from"] = sender_show
    # 收件人显示，不起实际作用
    msg["to"] = recipient_show
    # 抄送人显示，不起实际作用
    msg["Cc"] = cc_show
    with SMTP_SSL(host="smtp.163.com", port=465) as smtp:
        # 登录发邮件服务器
        smtp.login(user=user, password=password)
        # 实际发送、接收邮件配置
        smtp.sendmail(from_addr=user, to_addrs=to_addrs.split(','), msg=msg.as_string())


def notify(fund_code, signal, price, amount):
    Subject = 'code:%s, signal:%s' % (str(fund_code), str(signal))
    message = 'price:%s, amount:%s' % (str(price), str(amount))
    # 显示发送人
    sender_show = '18940874730@163.com'
    # 显示收件人
    recipient_show = 'chengshanchuan'
    # 实际发给的收件人
    to_addrs = '2248906444@qq.com'
    sendMail(message, Subject, sender_show, recipient_show, to_addrs)


if __name__ == '__main__':
    notify(1111, "buy", 1.4, 500)
