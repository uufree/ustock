from unittest import mock
import unittest

import net_strategy
import os


class MockDemo(unittest.TestCase):
    def test_add(self):
        for name in os.listdir("./data"):
            os.remove("./data/%s" % name)

        strategy = net_strategy.NetStrategy(1, 510900)
        # 刚开始还没有买入过
        strategy.get_market = mock.Mock(return_value=1.4)
        cur_price = strategy.get_market()
        last_trade_price, last_line = strategy.get_last_trade()
        self.assertEqual(last_trade_price, None)
        self.assertEqual(last_line, None)
        ok, net_line = strategy.if_trigger_net_price(cur_price, last_line)
        self.assertEqual(ok, True)
        self.assertEqual(strategy.signal, "buy")
        strategy.serialize(cur_price, net_line[1], strategy.net_content[net_line[1]]["buy_amount"])

        # 价格下降，应该再买入一波
        strategy.get_market = mock.Mock(return_value=1.3)
        cur_price = strategy.get_market()
        last_trade_price, last_line = strategy.get_last_trade()
        self.assertEqual(last_trade_price, 1.4)
        self.assertEqual(last_line, "1.40")
        ok, net_line = strategy.if_trigger_net_price(cur_price, last_line)
        self.assertEqual(ok, True)
        self.assertEqual(strategy.signal, "buy")
        strategy.serialize(cur_price, net_line[1], strategy.net_content[net_line[1]]["buy_amount"])

        # 价格上涨，应该卖出一波
        strategy.get_market = mock.Mock(return_value=1.4)
        cur_price = strategy.get_market()
        last_trade_price, last_line = strategy.get_last_trade()
        print(last_trade_price)
        print(last_line)
        self.assertEqual(last_trade_price, 1.3)
        self.assertEqual(last_line, "1.30")
        print(cur_price)
        ok, net_line = strategy.if_trigger_net_price(cur_price, last_line)
        self.assertEqual(ok, True)
        self.assertEqual(strategy.signal, "sell")


if __name__ == '__main__':
    unittest.main()
