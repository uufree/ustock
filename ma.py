#!/usr/bin/env python3
# coding=utf-8

import logging
from src.ma_strategy import *
from src.stock_price_manager import *

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

    content = ""
    with open("data/sh512690.json", "r") as f:
        content = f.read()
    offspm = OfflineStockPriceManager(content)
    onspm = None

    ma_strategy = MaStrategyA(10000.0, offspm, onspm)
    ma_strategy.run_offline_mode()
    result = ma_strategy.serialize()
    with open("results/sh512690.txt", "w") as f:
        f.write(result)

