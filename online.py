#!/usr/bin/env python3
# coding=utf-8

import logging
import datetime
from src.ma_strategy import *
from src.stock_price_manager import *
from utils.email import *

if __name__ == "__main__":
    # init log format
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')

    # run with cronjob
    # check if it shoule run
    now = time.localtime(time.time())
    hour = now.tm_hour
    minute = now.tm_min
    weekday = datetime.datetime.now().weekday()
    if weekday > 4:
        logging.info("not trade time...")
        exit(0)

    if hour < 9 or hour >= 15:
        logging.info("not trade time...")
        exit(0)

    if hour == 9 and minute <= 30:
        logging.info("not trade time...")
        exit(0)

    # 需要在：01，06，11，16这样的分钟点获取数据
    if minute % 5 != 1:
        logging.info("trade time, but not need to get data...")
        exit(0)

    # parse config
    config_content = ""
    with open("conf/config.json", 'r') as f:
        config_content = f.read()

    if len(config_content) == 0:
        logging.critical("read config.json failed, please check")

    email_config_content = ""
    with open("conf/email.json", 'r') as f:
        email_config_content = f.read()

    if len(email_config_content) == 0:
        logging.critical("read email config failed, please check")

    config = json.loads(config_content)
    email_config = json.loads(email_config_content)

    scale = config["online"]["scale"]
    len = config["online"]["len"]
    resource = config["data"]["resource"]

    aim_minute = minute - 1
    ma_strategy_collection = {}
    for stock in config["stocks"]:
        time.sleep(2)
        url = resource.format(stock["code"], scale, len)
        path = "data/{}.json".format(stock["code"])
        online_spm = OnlineStockPriceManager(url, aim_minute, path)
        logging.info("%s get data success", stock["name"])

        ma_strategy = MaStrategyA(stock["code"], stock["name"])
        ma_strategy.run(online_spm)
        ma_strategy_collection[stock["code"]] = ma_strategy

    if config["data"]["notify"]:
        sell_list = []
        buy_list = []
        for code, ma in ma_strategy_collection.items():
            if ma.has_buy_signal():
                buy_list.append(ma.get_brief_buy_info())
            if ma.has_sell_signal():
                sell_list.append(ma.get_brief_sell_info())

        if len(buy_list) == 0 and len(sell_list) == 0:
            exit(0)

        subject = ""
        for buy in buy_list:
            subject += "BUY {} ({})".format(buy.name, buy.code)
            subject += " || "
        for sell in sell_list:
            subject += "SELL {} ({})".format(sell.name, sell.code)
            subject += " || "
        send_mail(email_config["host"], email_config["port"],
                  email_config["user"], email_config["password"],
                  email_config["to_address"], subject, "")