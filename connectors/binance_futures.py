import requests
import logging

logger = logging.getLogger()

class BinanceFuturesClient:
    def __init__(self,is_testnet):
        if is_testnet:
            self.base_url = "https://testnet.binancefuture.com"
        else:
            self.base_url = "https://fapi.binance.com"

        self.prices = dict()

    def make_request(self,method,endpoint,data):
        if method in ["GET","get"]:
            response = requests.get(self.base_url + endpoint,params=data)
        else:
            raise ValueError()

        if response.status_code == 200:
            return response.json()
        else:
            logger.error("Error while making %s request to %s endpoint: (error code: %s) --> %s",method,endpoint,response.status_code,response.json())
            return None

    def get_contracts(self):
        exchange_info = self.make_request("GET","/fapi/v1/exchangeInfo",None)

        contracts = dict()

        if exchange_info is not None:
            for contract_data in exchange_info["symbols"]:
                contracts[contract_data["pair"]] = contract_data

        return contracts

    def get_bid_ask(self,symbol):
        endpoint = "/fapi/v1/ticker/bookTicker" #endpoint accepts "symbol" parametr
        data = dict()
        data["symbol"] = symbol

        order_book_data = self.make_request("GET",endpoint,data)

        if order_book_data is not None:
            if symbol not in self.prices:
                self.prices[symbol] = {"bid": float(order_book_data["bidPrice"]),"ask": float(order_book_data["askPrice"])}
            else:
                self.prices[symbol]["bid"] = float(order_book_data["bidPrice"])
                self.prices[symbol]["ask"] = float(order_book_data["askPrice"])

        return self.prices[symbol]

    def get_historical_candles(self,symbol,interval):
        endpoint = "/fapi/v1/klines"
        data = dict()
        data["symbol"] = symbol
        data["interval"] = interval
        data["limit"] = 1000

        raw_candles = self.make_request("GET",endpoint,data)

        candles = []

        if raw_candles is not None:
            for c in raw_candles:
                candles.append(c[0],float(c[1]),float(c[2]),float(c[3]),float(c[4]),float(c[5]))

        return candles
