#!/usr/bin/env python3
# coding=utf-8

import json
import requests
import logging
import time

class OfflineStockPriceManager:
    price_list = []

    def __init__(self, content, low = 0, high = 0):
        self.price_list = json.loads(content)
        if low < high:
            self.price_list = self.price_list[low:high]
        self.price_list.reverse()

    def get_price(self):
        if len(self.price_list) == 0:
            return -1, ""
        price = self.price_list.pop()
        return float(price["close"]), price["day"]

class OnlineStockPriceManager:
    price_list = []

    def __init__(self, url, aim_minute, save_path=""):
        while True:
            try:
                response = requests.get(url, timeout=5)
            except requests.exceptions.RequestException as e:
                logging.error(e)
                continue

            if response.status_code != 200:
                logging.error("get data from sina failed, status code: %d", response.status_code)
                continue

            if save_path != "":
                with open(save_path, "w") as f:
                    f.write(response.text)

            self.price_list = json.loads(response.text)
            break

        # 丢弃不完整的数据
        while True:
            minute = time.strptime(self.price_list[-1]["day"], "%Y-%m-%d %H:%M:%S").tm_min
            if minute == aim_minute:
                break
            logging.info("drop imcomplete record: %s", self.price_list.pop()["day"])

        self.price_list.pop()
        self.price_list.reverse()

    def get_price(self):
        if len(self.price_list) == 0:
            return -1, ""
        price = self.price_list.pop()
        return float(price["close"]), price["day"]

