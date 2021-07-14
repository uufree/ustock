#!/usr/bin/env python3
# coding=utf-8

import requests
html = requests.get('http://market.finance.sina.com.cn/pricehis.php?symbol=sh512690&startdate=2021-07-05&enddate=2021-07-13')
print(html.text)
