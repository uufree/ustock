#!/usr/bin/env python3
# coding=utf-8

import logging
from src.ma_strategy import *
from src.stock_price_manager import *

WRITE_RESULT = False
NOTIFY = True

if __name__ == "__main__":
    # init log format
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')

    # parse config
    config_content = ""
    with open("conf/config.json", 'r') as f:
        config_content = f.read()

    if len(config_content) == 0:
        logging.critical("read config.json failed, please check")

    config = json.loads(config_content)

    low = 0
    high = 256
    max = 1024
    results = []
    while high <= max:
        ma_strategy_collection = {}
        for stock in config["stocks"]:
            content = ""
            with open("data/{}.json".format(stock["code"]), "r") as f:
                content = f.read()
            offspm = OfflineStockPriceManager(content, low, high)
            onspm = None

            ma_strategy = MaStrategyA(stock["code"], stock["name"], 10000.0, offspm, onspm)
            ma_strategy.run_offline_mode()
            ma_strategy_collection[stock["code"]] = ma_strategy
            result = ma_strategy.serialize()
            if WRITE_RESULT:
                with open("results/{}.json".format(stock["code"]), "w") as f:
                    f.write(json.dumps(result))
        low += 1
        high += 1

        if NOTIFY:
            for code, ma in ma_strategy_collection.items():
                if ma.has_buy_signal():
                    results.append(ma.get_buy_info())
                if ma.has_sell_signal():
                    results.append(ma.get_sell_info())

    with open("result.json", "w") as f:
        f.write(json.dumps({
            "results": results
        }))


