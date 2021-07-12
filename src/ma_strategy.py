#!/usr/bin/env python3
# coding=utf-8

import logging
import json

class MA:
    price_list = []
    length = 0

    def __init__(self, length):
        self.length = length
        self.price_list = []

    def valid(self):
        return len(self.price_list) == self.length

    def add(self, price):
        if len(self.price_list) > self.length:
            logging.critical("len(price list): %d, length: %d", len(self.price_list), self.length)
            exit(0)
        if len(self.price_list) == self.length:
            self.price_list.pop(0)
        self.price_list.append(price)

    def average(self):
        if len(self.price_list) != self.length:
            logging.critical("len(price list): %d, length: %d", len(self.price_list), self.length)
            exit(0)

        sum = 0.0
        for price in self.price_list:
            sum += price
        return float(format(sum / self.length, ".3f"))

class TradePair:
    init_money = 0.0
    money = 0.0
    buy_count = 0
    buy_time = ""
    sell_time = ""
    buy_price = 0.0
    sell_price = 0.0
    buy_charge = 0.0
    sell_charge = 0.0
    profit_ratio = 0.0
    profit_money = 0.0

    def __init__(self, money):
        self.money = money
        self.init_money = money

    def set_buy_info(self, buy_time, buy_price):
        self.buy_time = buy_time
        self.buy_price = buy_price
        self.buy_count = self.money / buy_price - self.money / buy_price % 100
        self.buy_charge = self.buy_count * self.buy_price / 10000
        self.money = self.money - (self.buy_price * self.buy_count) - self.buy_charge

    # 不能在同天交易
    def check_sell_cond(self, day):
        buy_dur = str(self.buy_time).split(" ")[0]
        sell_dur = str(day).split(" ")[0]
        if buy_dur == sell_dur:
            return False
        return True

    def set_sell_info(self, sell_time, sell_price):
        self.sell_time = sell_time
        self.sell_price = sell_price
        self.sell_charge = self.buy_count * sell_price / 10000
        self.money = self.money - self.sell_charge + (self.buy_count * self.sell_price)
        self.profit_money = self.money - self.init_money
        self.profit_ratio = self.money / self.init_money - 1

    def get_money(self):
        return self.money

    def serialize(self):
        data = {
            "init_money": format(self.init_money, ".3f"),
            "final_money": format(self.money, ".3f"),
            "buy_count": format(self.buy_count, ".3f"),
            "buy_price": format(self.buy_price, ".3f"),
            "buy_time": self.buy_time,
            "sell_price": format(self.sell_price, ".3f"),
            "sell_time": self.sell_time,
            "profit_money": format(self.profit_money, ".3f"),
            "profit_ratio": format(self.profit_ratio, ".3f")
        }
        return json.dumps(data)

class MaStrategyA:
    MA10 = {}
    MA20 = {}
    MA30 = {}
    offline_smm = {}
    online_smm = {}
    last_check = False
    current_trade_pair = None
    history_trade_pair_list = []
    money = 0

    def __init__(self, money, offspm, onspm):
        self.offline_spm = offspm
        self.online_spm = onspm
        self.MA10 = MA(10)
        self.MA20 = MA(20)
        self.MA30 = MA(30)
        self.current_trade_pair = None
        self.history_trade_pair_list = []
        self.money = money

    def run_offline_mode(self):
        while True:
            price, day = self.offline_spm.get_price()
            if price == -1 or day == "":
                logging.info("read offline data finished.")
                break

            self.MA10.add(price)
            self.MA20.add(price)
            self.MA30.add(price)

            # MA均线未构建完成，不进行交易
            if (not self.MA10.valid()) or (not self.MA20.valid()) or (not self.MA30.valid()):
                continue

            # 跳过15:00
            if str(day).find("15:00:00") == True:
                continue

            logging.info("ma10: %f, ma20: %f, ma30: %f", self.MA10.average(), self.MA20.average(), self.MA30.average())

            if self.current_trade_pair == None and self.check_buy_cond():
                self.current_trade_pair = TradePair(self.money)
                self.current_trade_pair.set_buy_info(day, price)
                continue

            if self.current_trade_pair != None and self.check_sell_cond() and self.current_trade_pair.check_sell_cond(day):
                self.current_trade_pair.set_sell_info(day, price)
                self.history_trade_pair_list.append(self.current_trade_pair)
                self.money = self.current_trade_pair.money
                self.current_trade_pair = None
                continue

    def check_buy_cond(self):
        if self.MA10.average() > self.MA20.average() and self.MA20.average() > self.MA30.average():
            return True
        return False

    def check_sell_cond(self):
        return not self.check_buy_cond()

    def serialize(self):
        content = ""
        for trade_pair in self.history_trade_pair_list:
            content += trade_pair.serialize()
            content += "\n"
        return content

    def run_online_mode(self):
        pass

