BITMEX_MULTIPLIER = 0.00000001 #to convert satoshi to bitcoin in bitmex

# INFO: Bitmex returns XBt(satoshi) instead of XBT(Bitcoin)
"""
Balance Data Model,

Gets "assets dictionary" and takes the necessary infos
used endpoint ---> /fapi/v1/account
"""
class Balance:
    def __init__(self,info,exchange):
        if exchange == "binance":
            self.initial_margin = float(info["initialMargin"])
            self.maintanence_margin = float(info["maintMargin"])
            self.margin_balance = float(info["marginBalance"])
            self.wallet_balance = float(info["walletBalance"])
            self.unrealized_profit = float(info["unrealizedProfit"])

        elif exchange == "bitmex": 
            self.initial_margin =info["initMargin"] * BITMEX_MULTIPLIER
            self.maintanence_margin =info["maintMargin"] * BITMEX_MULTIPLIER
            self.margin_balance =info["marginBalance"] * BITMEX_MULTIPLIER
            self.wallet_balance =info["walletBalance"] * BITMEX_MULTIPLIER
            self.unrealized_profit =info["unrealisedPnl"] * BITMEX_MULTIPLIER
"""
Candle Data Model,

Takes "candle info array" and extracts necessary data
used endpoint ---> /fapi/v1/klines
"""
class Candle:
    def __init__(self,candle_info):
        self.timestamp = candle_info[0]
        self.open = float(candle_info[1])
        self.high = float(candle_info[2])
        self.low = float(candle_info[3])
        self.close = float(candle_info[4])
        self.volume = float(candle_info[5])
        


"""
Contract Data Model,

Takes "contract data object" and extracts necessary data
used endpoint ---> /fapi/v1/exchangeInfo
"""
class Contract:
    def __init__(self,contract_info,exchange):
        if exchange == "binance":
            self.symbol = contract_info["symbol"]
            self.base_asset = contract_info["baseAsset"]
            self.quate_asset = contract_info["quateAsset"]
            self.price_decimals = contract_info["pricePrecision"]
            self.quantity_decimals = contract_info["quantityPrecision"]
        elif exchange == "bitmex":
            self.symbol = contract_info["symbol"]
            self.base_asset = contract_info["rootSymbol"]
            self.quate_asset = contract_info["quoteCurrency"]
            self.price_decimals = contract_info["tickSize"]
            self.quantity_decimals = contract_info["lotSize"]            

"""
Order Status Data Model,

Takes "order status obj" and extracts necessary data
used endpoint ---> /fapi/v1/order
"""

class OrderStatus:
    def __init__(self,order_info):
        self.order_id = order_info["orderId"]
        self.status = order_info["status"]
        self.avg_price = float(order_info["avgPrice"])