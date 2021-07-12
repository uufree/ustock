#!/usr/bin/env python3
# coding=utf-8

import json

class OfflineStockPriceManager:
    price_list = []

    def __init__(self, content):
        self.price_list = json.loads(content)
        self.price_list.reverse()

    def get_price(self):
        if len(self.price_list) == 0:
            return -1, ""
        price = self.price_list.pop()
        return float(price["close"]), price["day"]