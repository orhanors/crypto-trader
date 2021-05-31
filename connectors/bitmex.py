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

        t = threading.Thread(target=self._start_ws)
        t.start()

        logger.info("Bitmex Client successfully initialized")
        

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