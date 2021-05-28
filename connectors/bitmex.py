import pprint

import requests

def get_contracts():
    base_url = "https://www.bitmex.com/api/v1"
    endpoint = "/instrument/active"
    contracts = []

    response_object = requests.get(base_url + endpoint)
    data = response_object.json()

    for contract in data:
       contracts.append(contract["symbol"])
    return contracts

get_contracts()