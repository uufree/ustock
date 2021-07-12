#!/usr/bin/env python3
# coding=utf-8

import src.net_strategy
import src.stock_manager
import logging

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')

    with open("conf/config.yaml", 'r', encoding='utf-8') as f:
        config_content = f.read()

    if len(config_content) == 0:
        logging.critical("open config failed, please check")
        exit(-1)

    offsm = stock_manager.OfflineStockMarketManager(config_content)
    onsm = stock_manager.OnlineStockMarketManager(config_content)

    net_strategy = net_strategy.NetStrategy(10 * 60, 510900, offsm, onsm)
    # 不发生邮件信号
    net_strategy.is_notify = False
    net_strategy.run_offline_mode()
