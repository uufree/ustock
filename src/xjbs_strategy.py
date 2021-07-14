#!/usr/bin/env python3
# coding=utf-8

import easyquotation

quotation = easyquotation.use('sina') # 新浪 ['sina'] 腾讯 ['tencent', 'qq']
print(quotation.stocks(['399300'])) # 支持直接指定前缀，如 'sh000001'