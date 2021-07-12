#!/usr/bin/env python3
# coding=utf-8

import os
import yaml
import time
import json
import logging
import requests


class StockMarket:
    day = ""
    open = 0
    close = 0
    high = 0
    low = 0

    def __init__(self, day, open_price, close, high, low):
        self.day = day
        self.open = open_price
        self.close = close
        self.high = high
        self.low = low


class OfflineStockMarketManager(object):
    config = {}
    code = ""
    scale = 0
    datalen = 0
    current = ""
    data_path = ""
    stock_market_list = []

    def __init__(self, config_content):
        self.config = yaml.load(config_content, Loader=yaml.FullLoader)
        self.code = self.config["service"]["stock_code"]
        self.scale = self.config["service"]["default_scale"]
        self.datalen = self.config["service"]["default_datalen"]
        self.current = time.strftime("%Y%m%d", time.localtime())
        self.data_path = self.config["service"]["data_storage_path"].format(self.current, self.code, self.scale)

        if not os.path.exists(self.data_path):
            self.download_data()
        self.load_data()

    def download_data(self):
        url = self.config["service"]["offline_resource"].format(self.code, self.scale, self.datalen)
        response = requests.get(url)
        if response.status_code != 200:
            logging.critical("get data from sina failed, status code: %d", response.status_code)
            exit(-1)

        with open(self.data_path, "w", encoding='utf-8') as f:
            f.write(response.text)
        logging.info("download data success, data path: %s", self.data_path)

    def load_data(self):
        with open(self.data_path, 'r', encoding="utf-8") as f:
            stock_markets_content = f.read()

        stock_markets = json.loads(stock_markets_content)
        for market in stock_markets:
            self.stock_market_list.append(
                StockMarket(market["day"],
                            float(market["open"]),
                            float(market["close"]),
                            float(market["high"]),
                            float(market["low"])))
        self.stock_market_list.reverse()
        logging.info("load data success")

    def get_stock(self):
        if len(self.stock_market_list) == 0:
            return None
        return self.stock_market_list.pop()


class OnlineStockMarketManager(object):
    def __init__(self, config_content):
        pass
