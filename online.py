#!/usr/bin/env python3
# coding=utf-8

import logging
from src.ma_strategy import *
from src.stock_price_manager import *

NOTIFY = True

if __name__ == "__main__":
    # init log format
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')

    # run with cronjob
    # check if it shoule run
    now = time.localtime(time.time())
    hour = now.tm_hour
    minute = now.tm_min
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

    config = json.loads(config_content)
    scale = config["online"]["scale"]
    len = config["online"]["len"]
    resource = config["data"]["resource"]

    ma_strategy_collection = {}
    for stock in config["stocks"]:
        time.sleep(2)
        url = resource.format(stock["code"], scale, len)
        path = "data/{}.json".format(stock["code"])
        online_spm = OnlineStockPriceManager(url, path)
        logging.info("%s get data success", stock["name"])

        ma_strategy = MaStrategyA(stock["code"], stock["name"])
        ma_strategy.run(online_spm)
        ma_strategy_collection[stock["code"]] = ma_strategy

    if NOTIFY:
        results = []
        for code, ma in ma_strategy_collection.items():
            if ma.has_buy_signal():
                results.append(ma.get_buy_info())
            if ma.has_sell_signal():
                results.append(ma.get_sell_info())
        with open("./results.json", "w", encoding='utf-8') as f:
            f.write(json.dumps(results, ensure_ascii=False))