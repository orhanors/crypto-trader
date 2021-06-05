import logging
from time import time
from typing import *
import typing

from models import *

logger = logging.getLogger()

TF_EUQIV = {"1m": 60, "5m": 300, "15m": 900,
            "30m": 900, "1h": 3600, "4h": 14400}


class Strategy:
    def __init__(self, contract: Contract, exchange: str, timeframe: str, balance_percentage: float, take_profit: float, stop_loss: float):

        self.contract = contract
        self.exchange = exchange
        self.tf = timeframe
        self.tf_equiv = TF_EUQIV[timeframe] * 1000

        self.balance_percentage = balance_percentage
        self.take_profit = take_profit
        self.stop_loss = stop_loss

        self.candles: List[Candle] = []

    def parse_trades(self, price: float, size: float, timestamp: int) -> str:

        last_candle = self.candles[-1]

        # 1)same candle
        if timestamp < last_candle.timestamp + self.tf_equiv:  # we're in the same candle

            last_candle.close = price
            last_candle.volume += size

            if price > last_candle.high:
                last_candle.high = price

            elif price < last_candle.low:
                last_candle.low = price

            return "same_candle"

        # 2)missing candle
        elif timestamp >= last_candle.timestamp + 2 * self.tf_equiv:  # we're missing at least one candle
            missing_candles = int(
                timestamp - last_candle.timestamp) / self.tf_equiv - 1

            logger.info("%s missing %s candles for %s %s (%s %s)", self.exchange, missing_candles, self.contract.symbol,
                        self.tf, timestamp, last_candle.timestamp)

            for missing in range(missing_candles):
                new_ts = last_candle.timestamp + self.tf_equiv
                candle_info = {"ts": new_ts, "open": last_candle.close, "high": last_candle.close,
                               "low": last_candle.close, "close": last_candle.close, "volume": 0}

                new_candle = Candle(candle_info, self.tf, "parse_trade")
                self.candles.append(new_candle)

                last_candle = new_candle

            new_ts = last_candle.timestamp + self.tf_equiv

            candle_info = {"ts": new_ts, "open": price, "high": price,
                           "low": price, "close": price, "volume": size}

            new_candle = Candle(candle_info, self.tf, "parse_trade")

            self.candles.append(new_candle)

            return "new_candle"

        # 3)New candle
        elif timestamp >= last_candle.timestamp + self.tf_equiv:
            new_ts = last_candle.timestamp + self.tf_equiv

            candle_info = {"ts": new_ts, "open": price, "high": price,
                           "low": price, "close": price, "volume": size}

            new_candle = Candle(candle_info, self.tf, "parse_trade")

            self.candles.append(new_candle)

            logger.info("%s new candle for %s %s", self.exchange,
                        self.contract.symbol, self.tf)

            return "new_candle"


class TechnicalStrategy(Strategy):
    def __init__(self, contract: Contract, exchange: str, timeframe: str, balance_percentage: float, take_profit: float, stop_loss: float, other_params: typing.Dict):
        super().__init__(contract, exchange, timeframe,
                         balance_percentage, take_profit, stop_loss)

        self._ema_fast = other_params["ema_fast"]
        self._ema_slow = other_params["ema_slow"]
        self._ema_signal = other_params["ema_signal"]


class BreakoutStrategy(Strategy):
    def __init__(self, contract: Contract, exchange: str, timeframe: str, balance_percentage: float, take_profit: float, stop_loss: float, other_params: typing.Dict):
        super().__init__(contract, exchange, timeframe,
                         balance_percentage, take_profit, stop_loss)

        self._min_volume = other_params["min_volume"]
