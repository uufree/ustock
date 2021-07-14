#!/usr/bin/env python3
# coding=utf-8

from smtplib import SMTP_SSL
from email.mime.text import MIMEText

def send_mail(host, port, user, password, to_address, subject, message, from_show="369470777", to_show="uuchen", cc_show="uuchen"):
    # 邮件内容
    msg = MIMEText(message, 'plain', _charset="utf-8")
    # 邮件主题描述
    msg["Subject"] = subject
    # 发件人显示
    msg["from"] = from_show
    # 收件人显示
    msg["to"] = to_show
    # 抄送人显示
    msg["Cc"] = cc_show
    with SMTP_SSL(host="smtp.163.com", port=465) as smtp:
        # 登录发邮件服务器
        smtp.login(user=user, password=password)
        # 实际发送、接收邮件配置
        smtp.sendmail(from_addr=user, to_addrs=to_address.split(','), msg=msg.as_string())
