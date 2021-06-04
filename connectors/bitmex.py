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

class BitmexClient:
    def __init__(self,is_testnet:bool, public_key:str, secret_key:str):
        
        if is_testnet:
            self._base_url = "https://testnet.bitmex.com"
            self._wss_url = "wss://testnet.bitmex.com/realtime"
        else:
            self._base_url = "https://www.bitmex.com"
            self._wss_url = "wss://www.bitmex.com/realtime"

        self._public_key = public_key
        self._secret_key = secret_key

        self.contracts = self.get_contracts()
        self.balances = self.get_balances()

        self.prices = dict()

        self._ws = None
        
        self.logs = []

        t = threading.Thread(target=self._start_ws)
        t.start()

        logger.info("Bitmex Client successfully initialized")
        
    def _add_log(self,msg:str):
        logger.info("%s",msg)
        self.logs.append({"log":msg,"displayed":False})

    def _generate_signature(self,method: str, endpoint: str, expires: str, data: typing.Dict) -> str:
        """
        Generates an `api-signature` value to make an auth request

        Args:
            method (str): api request method
            endpoint (str): request endpoint
            expires (str): expiration time of request
            data (typing.Dict): request params 

        Returns:
            str: `api-signature` value to make a authenticated request
        """
        message = method + endpoint + "?" + urlencode(data) + expires if len(data) > 0 else method + endpoint + expires
        return hmac.new(self._secret_key.encode(), message.encode(), hashlib.sha256).hexdigest()

    def _generate_headers(self,method:str, endpoint: str,data:typing.Dict) -> typing.Dict:
        """
        Generates "headers" dictionary to make a call for Bitmex endpoints

        Returns:
            typing.Dict: Generated headers to send a request
        """
        headers = dict()
        expires = str(int(time.time())+5)
        headers["api-expires"] = expires
        headers["api-key"] = self._public_key
        headers["api-signature"] = self._generate_signature(method,endpoint,expires,data)
        return headers

    def _make_request(self,method: str,endpoint: str,data: typing.Dict):
        
        headers = self._generate_headers(method,endpoint,data)

        if method in ["GET","get"]:
            try:
                response = requests.get(self._base_url+endpoint,params=data,headers=headers)
            except Exception as e:
                logger.error("Connection error while making %s request to %s endpoint: %s",method,endpoint,e)
                return None
        
        elif method in ["POST","post"]:
            try:
                response = requests.post(self._base_url + endpoint,params=data,headers=headers)
            except:
                logger.error("Connection error while making %s request to %s endpoint: %s",method,endpoint,e)
                return None

        elif method in ["DELETE","delete"]:
            try:
                response = requests.delete(self._base_url + endpoint,params=data,headers=headers)
            except Exception as e:
                logger.error("Connection error while making %s request to %s endpoint: %s",method,endpoint,e)
                return None
        else:
            raise ValueError()
        

        print(response.json())
        if response.status_code == 200:
            return response.json()
        else:
            logger.error("Error while making %s request to %s endpoint: (error code: %s) --> %s",method,endpoint,response.status_code,response.json())
            return None
            
    def get_contracts(self) -> typing.Dict[str,Contract]:
        endpoint = "/api/v1/instrument/active"
        instruments = self._make_request("GET",endpoint,dict())

        contracts = dict()

        if instruments is not None:
            for s in instruments:
                contracts[s["symbol"]] = Contract(s,"bitmex")
        
        return contracts

    def get_balances(self) -> typing.Dict[str,Balance]:
        endpoint = "/api/v1/user/margin"

        data = dict()
        data["currency"] = "all"

        margin_data = self._make_request("GET",endpoint,data)

        balances = dict()
        if margin_data is not None:
            for a in margin_data:
                balances[a["currency"]] = Balance(a, "bitmex")
        
        return balances

    
    def get_historical_data(self, contract:Contract, timeframe:str) -> typing.List[Candle]:
        endpoint = "/api/v1/trade/buckedet"
        
        data = dict()
        data["symbol"] = contract.symbol
        data["partial"] = True
        data["binSize"] = timeframe
        data["count"] = 500

        raw_candles = self._make_request("GET",endpoint,data)

        candles = []

        if raw_candles is not None:
            for c in reversed(raw_candles):
                candles.append(Candle(c,timeframe,"bitmex"))

        return candles

    
    def place_order(self,contract: Contract, order_type: str, quantity: int, side: str, price= None, tif = None) -> OrderStatus:
        endpoint = "/api/v1/order"

        data = dict()
        data["symbol"] = contract.symbol
        data["side"] = side.capitalize()
        data["orderQty"] = round(quantity / contract.lot_size) * contract.lot_size
        data["ordType"] = order_type.capitalize

        if price is not None:
            data["price"] = round(round(price / contract.tick_size) * contract.tick_size,8)

        if tif is not None:
            data["tif"] = tif

        order_status = self._make_request("POST",endpoint,data)

        if order_status is not None:
            order_status = OrderStatus(order_status,"bitmex")
        
        return order_status
        


    def cancel_order(self,order_id: str) -> OrderStatus:
        endpoint = "/api/v1/order"

        data = dict()
        data["orderID"] = order_id
       
        order_status = self._make_request("DELETE",endpoint,data)

        if order_status is not None:
            #we can cancel more than one in one api call, but we will do one by one
            order_status = OrderStatus(order_status[0],"bitmex")
        
        return order_status
        



    def get_order_status(self, order_id:str, contract: Contract):
        endpoint = "/api/v1/order"

        data = dict()
        data["symbol"] = contract.symbol
        data["reverse"] = True #returns recent orders first

        order_status = self._make_request("GET",endpoint,data)

        if order_status is not None:
            for order in order_status:
                if order["orderID"] == order_id:
                    return OrderStatus(order,"bitmex")

    
    def _start_ws(self):
        """
        Starts websocket connection
        If it fails when creating forever loop, waits 2 secs and restarts the loop again
        """
        self._ws = websocket.WebSocketApp(self._wss_url,on_open=self._on_open,on_close=self._on_close,on_error=self._on_error,on_message=self._on_message)

        while True:
            try:
                self._ws.run_forever()

            except Exception as e:
                logger.error("Bitmex websocket error: %s",e)
            
            time.sleep(2)

    def _on_open(self,ws):
        logger.info("Bitmex webSocket connection opened")

        #we subscribe whole feed
        self.subscribe_channel("instrument")
    
    def _on_close(self,ws):
        logger.warning("Bitmex websocket connection closed")

    def _on_error(self,ws,msg: str):
        logger.error("Bitmex websokcet connection error: %s",msg)

    def _on_message(self,ws,msg: str):
        #print(msg)

        data = json.loads(msg)

        if "table" in data:
            if data["table"] == "instrument":
                for d in data["data"]:
                    symbol = d["symbol"]

                    if symbol not in self.prices:
                        self.prices[symbol] = {"bid": None,"ask":None}

                    if "bidPrice" in d:
                        self.prices[symbol]["bid"] = d["bidPrice"]
                    if "askPrice" in d:
                        self.prices[symbol]["ask"] = d["askPrice"]
                    
                    
                    
                    #print(self.prices[symbol])

    def subscribe_channel(self,topic:str):
        data = dict()
        data["op"] = "subscribe"
        data["args"] = []
       
        data["args"].append(topic)
        
        
        try:
            self._ws.send(json.dumps(data))
        except Exception as e:
            logger.error("Websocket error while subscribing to %s: %s",topic,e)

       