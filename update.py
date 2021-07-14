#!/usr/bin/env python3
# coding=utf-8

import time
import json
import logging
import requests

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
    resource_url = config["data"]["resource"]
    scale = config["offline"]["scale"]
    len = config["offline"]["len"]

    for stock in config["stocks"]:
        url = resource_url.format(stock["code"], scale, len)
        path = "data/{}.json".format(stock["code"])
        try:
            response = requests.get(url, timeout=5)
        except requests.exceptions.RequestException as e:
            logging.error(e)
            continue

        if response.status_code != 200:
            logging.error("get data from sina failed, status code: %d", response.status_code)
            continue

        with open(path, "w", encoding='utf-8') as f:
            f.write(response.text)
        logging.info("update data success, code: %s, name: %s", stock["code"], stock["name"])
        time.sleep(3)
