#!/usr/bin/env python3
# coding=utf-8

import json
import time
import logging
import os

import util


class NetStrategy(object):
    net_content = {}
    time_interval = 60
    fund_code = 0
    signal = ""
    offline_stock_market_manager = {}
    online_stock_market_manager = {}
    is_notify = False
    cur_time = ""
    net_lines = []
    seq = 0
    buy_vol = 0.0
    sell_vol = 0.0

    def __init__(self, interval, fund_code, offline_stock_market_manager, online_stock_market_manager):
        # 运行时间间隔
        self.time_interval = interval
        self.fund_code = fund_code
        self.offline_stock_market_manager = offline_stock_market_manager
        self.online_stock_market_manager = online_stock_market_manager
        with open("conf/%s.json" % fund_code) as jsonFile:
            self.net_content = json.load(jsonFile)
            jsonFile.close()

        self.net_lines = self.net_content.keys()
        self.net_lines = [(float(x), x) for x in self.net_lines]
        self.net_lines.sort(key=lambda tup: tup[0])  # 按第一个来sort

    def run_offline_mode(self):
        while True:
            self.cur_time, cur_price = self.get_offline_market()
            if cur_price == -1:
                logging.info("read offline data finished.")
                logging.info("earn money:%f" % (self.sell_vol - self.buy_vol))
                break
            logging.info("time: %s, price: %f", self.cur_time, cur_price)

            last_trade_price, last_line = self.get_last_trade()
            logging.info("[run_offline_mode] last_trade_price: %s, last_line: %s", last_trade_price, last_line)
            ok, net_line = self.if_trigger_net_price(cur_price, last_line)
            # net_line是字符串
            if ok:
                logging.info("[run_offline_mode] ok")
                trigger_line_float, trigger_line_str = net_line[0], net_line[1]
                self.trade(cur_price, trigger_line_str)

    def run_online_mode(self):
        while True:
            cur_price = self.get_online_market()
            last_trade_price, last_line = self.get_last_trade()
            ok, net_line = self.if_trigger_net_price(cur_price, last_line)
            # net_line是字符串
            if ok:
                trigger_line_float, trigger_line_str = net_line[0], net_line[1]
                self.trade(cur_price, trigger_line_str)
            time.sleep(self.time_interval)

    def get_online_market(self):
        stock_market = self.online_stock_market_manager.get_stock()
        if stock_market is None:
            return "", -1
        return stock_market.day, stock_market.close

    def get_offline_market(self):
        stock_market = self.offline_stock_market_manager.get_stock()
        if stock_market is None:
            return "", -1
        return stock_market.day, stock_market.close

    def get_last_trade(self):
        last_trade_price = None
        last_line = None
        names = os.listdir("./data")
        names.sort()
        names.reverse()
        names = [n for n in names if n.startswith(str(self.fund_code)) and n.endswith(".json")]
        logging.info("[get_last_trade] names:%s" % names)
        if len(names) != 0:
            logging.info("[get_last_trade] file:%s" % names[0])
            with open("./data/%s" % names[0]) as f:
                content = json.load(f)
                logging.info("[get_last_trade] content:%s" % content)
                last_trade_price = float(content["trade_price"])
                last_line = str(content["net_line"])
                f.close()
        return last_trade_price, last_line

    def if_trigger_net_price(self, cur_price, last_line):  # 如果last_line是1.3，则cur_price > 1.4 or cur_price < 1.2才能触发
        assert isinstance(cur_price, float)
        if last_line is not None:
            assert isinstance(last_line, str)

        net_lines = self.net_lines
        # 处理还没有买过的情况!!! 以小于网格0.05来算
        if last_line is None:
            for i in range(len(net_lines)):
                if abs(net_lines[i][0] - cur_price) < 0.05:
                    self.signal = "buy"
                    return True, net_lines[i]

        idx = None
        for i in range(len(net_lines)):
            if net_lines[i][1] == last_line:
                idx = i
                break
        a = 1
        for i in range(idx):
            left_line = net_lines[i]
            if left_line is not None and cur_price <= left_line[0]:
                self.signal = "buy"
                return True, (cur_price, left_line[1])
        for i in range(idx + 1, len(net_lines)):
            right_line = net_lines[i]
            if right_line is not None and cur_price >= right_line[0]:
                self.signal = "sell"
                return True, (cur_price, right_line[1])

        return False, ()

    def trade(self, cur_price, trigger_line):  # 执行买卖函数
        amount = 0
        if self.signal == "buy":
            amount = self.net_content[trigger_line]["buy_amount"]
            self.buy_vol += float(amount) * cur_price
        elif self.signal == "sell":
            amount = self.net_content[trigger_line]["sell_amount"]
            self.sell_vol += float(amount) * cur_price

        self.serialize(cur_price, trigger_line, amount)

        if self.is_notify:
            util.notify(self.fund_code, self.signal, cur_price, amount)

    def serialize(self, price, net_line, amount):  # 写入文件
        file_name = time.strftime("%Y-%m-%d_%H:%M", time.localtime())
        data = {
            "trade_price": float(price),
            "net_line": str(net_line),
            "amount": amount,
            "signal": self.signal
        }
        with open('data/%s_%s_%d.json' % (self.fund_code, file_name, self.seq), 'w', encoding='utf-8') as f:
            json.dump(data, f)
            f.close()
        self.seq += 1
        logging.info("[serialize] filename:%s" % file_name)
