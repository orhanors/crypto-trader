from urllib.parse import urlencode
from models import *
import typing
import hashlib
import hmac
import requests
import logging
import time
import websocket
import threading
import json

logger = logging.getLogger()

class BinanceFuturesClient:
    def __init__(self,is_testnet: bool,public_key: str,secret_key: str):
        logger.info("Binance futures client created")
        if is_testnet:
            self.base_url = "https://testnet.binancefuture.com"
            self.wss_url = "wss://stream.binancefuture.com/ws"
        else:
            self.base_url = "https://fapi.binance.com"
            self.wss_url = "wss://fstream.binance.com/ws"
        
        self.headers = {"X-MBX-APIKEY":self.public_key}
        self.public_key = public_key
        self.secret_key = secret_key
        
        self.contracts = self.get_contracts()
        self.balances = self.get_balance()

        self.prices = dict()

        self.id = 1
        self.ws = None

        #multithreading to run websocket connection
        t = threading.Thread(target=self.start_ws)
        t.start()

    def generate_signature(self,data: typing.Dict) -> str:
        return hmac.new(self.secret_key.encode(),urlencode(data).encode(),hashlib.sha256).hexdigest()

    def generate_timestamp(self):
        return int(time.time() * 1000)

    def make_request(self,method: str,endpoint: str,data: typing.Dict):
        if method in ["GET","get"]:
            response = requests.get(self.base_url + endpoint,params=data,headers=self.headers)
        elif method in ["POST","post"]:
            response = requests.post(self.base_url + endpoint,params=data,headers=self.headers)
        elif method in ["DELETE","delete"]:
            response = requests.delete(self.base_url + endpoint,params=data,headers=self.headers)

        else:
            raise ValueError()

        if response.status_code == 200:
            return response.json()
        else:
            logger.error("Error while making %s request to %s endpoint: (error code: %s) --> %s",method,endpoint,response.status_code,response.json())
            return None

    def get_contracts(self) -> typing.Dict[str,Contract]:
        endpoint = "/fapi/v1/exchangeInfo"
        exchange_info = self.make_request("GET",endpoint, dict())

        contracts = dict()

        if exchange_info is not None:
            for contract_data in exchange_info["symbols"]:
                contracts[contract_data["pair"]] = Contract(contract_data)

        return contracts

    def get_bid_ask(self,contract: Contract) -> typing.Dict[str,float]:
        endpoint = "/fapi/v1/ticker/bookTicker" #endpoint accepts "symbol" parametr
        data = dict()
        data["symbol"] = contract.symbol

        order_book_data = self.make_request("GET",endpoint,data)

        if order_book_data is not None:
            if contract.symbol not in self.prices:
                self.prices[contract.symbol] = {"bid": float(order_book_data["bidPrice"]),"ask": float(order_book_data["askPrice"])}
            else:
                self.prices[contract.symbol]["bid"] = float(order_book_data["bidPrice"])
                self.prices[contract.symbol]["ask"] = float(order_book_data["askPrice"])

            return self.prices[contract.symbol]

    
    def get_historical_candles(self,contract: Contract,interval: str) -> typing.List[Candle]:

        endpoint = "/fapi/v1/klines"
        data = dict()
        data["symbol"] = contract.symbol
        data["interval"] = interval
        data["limit"] = 1000

        raw_candles = self.make_request("GET",endpoint,data)

        candles = []

        if raw_candles is not None:
            for c in raw_candles:
                candles.append(Candle(c))

        return candles

    def place_order(self,contract: Contract,side: str,quantity: float,order_type: str,price=None,tif=None) -> OrderStatus:
        endpoint = "/fapi/v1/order"

        data = dict()
        data["symbol"] = contract.symbol
        data["side"] = side
        data["quantity"] = quantity
        data["type"] = order_type

        if price is not None:
            data["price"] = price

        if tif is not None:
            data["timeInForce"] = tif

        data["timestamp"] = self.generate_timestamp()
        data["signature"] = self.generate_signature(data)

        order_status = self.make_request("POST",endpoint,data)

        if order_status is not None:
            order_status = OrderStatus(order_status)

        return order_status

    def cancel_order(self,contract: Contract,order_id: int) -> OrderStatus:
        endpoint = "/fapi/v1/order"

        data = dict()
        data["symbol"] = contract.symbol
        data["orderId"] = order_id

        data["timestamp"] = self.generate_timestamp()
        data["signature"] = self.generate_signature(data)

        order_status = self.make_request("DELETE",endpoint,data)
        
        if order_status is not None:
            order_status = OrderStatus(order_status)

        return order_status

    def get_balance(self) -> typing.Dict[str,Balance]:
        endpoint = "/fapi/v1/account"
        data = dict()
        data["timestamp"] = self.generate_timestamp()
        data["signature"] = self.generate_signature(data)

        account_data = self.make_request("GET",endpoint,data)

        balances = dict()
        if account_data is not None:
            for a in account_data["assets"]:
                balances[a["asset"]] = Balance(a)
        
        print("YEAHH::",balances["BNB"].wallet_balance)
        return balances

    def get_order_status(self,contract: Contract,order_id: int) -> OrderStatus:

        endpoint = "/fapi/v1/order"
        data = dict()
        data["timestamp"] = self.generate_timestamp()
        data["symbol"] = contract.symbol
        data["orderId"] = order_id
        data["signature"] = self.generate_signature(data)

        order_status = self.make_request("GET",endpoint,data)
        
        if order_status is not None:
            order_status = OrderStatus(order_status)

        return order_status


    def start_ws(self):
        self.ws = websocket.WebSocketApp(self.wss_url,on_open=self.on_open,on_close=self.on_close,on_error=self.on_error,on_message=self.on_message)

        self.ws.run_forever()

    def on_open(self,ws):
        logger.info("Binance webSocket connection opened")

        self.subscribe_channel("BTCUSDT")
    
    def on_close(self,ws):
        logger.warning("Binance websocket connection closed")

    def on_error(self,ws,msg: str):
        logger.error("Binance websokcet connection error: %s",msg)

    def on_message(self,ws,msg: str):
        #print(msg)

        data = json.loads(msg)

        if "e" in data:
            if data["e"] == "bookTicker":
                symbol = data["s"]

                if symbol not in self.prices:
                    self.prices[symbol] = {"bid": float(data["b"]),"ask":float(data["a"])}

                else:
                    self.prices[symbol]["bid"] = float(data["b"])
                    self.prices[symbol]["ask"] = float(data["a"])
                
                print(self.prices[symbol])

    def subscribe_channel(self,contract):
        data = dict()
        data["method"] = "SUBSCRIBE"
        data["params"] = []
        data["params"].append(contract.symbol.lower() + "@bookTicker")
        data["id"] = self.id
        
        self.ws.send(json.dumps(data))

        self.id += 1