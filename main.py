import tkinter as tk
import logging
from dotenv import load_dotenv,dotenv_values
from connectors.bitmex import  BitmexClient
from connectors.binance_futures import BinanceFuturesClient



logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

stream_handler = logging.StreamHandler()
formatter = logging.Formatter( '%(asctime)s %(levelname)s :: %(message)s' )
stream_handler.setFormatter(formatter)
stream_handler.setLevel(logging.INFO)

file_handler = logging.FileHandler("info.log")
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)

logger.addHandler(stream_handler)
logger.addHandler(file_handler)


if __name__ == "__main__":
    load_dotenv()

    binance_testnet_api_key = dotenv_values(".env").get("BINANCE_TESTNET_API_KEY")
    binance_testnet_api_secret = dotenv_values(".env").get("BINANCE_TESTNET_API_SECRET")

    bitmex_testnet_api_key = dotenv_values(".env").get("BITMEX_TESTNET_API_KEY")
    bitmex_testnet_api_secret = dotenv_values(".env").get("BITMEX_TESTNET_API_SECRET")
    

    binance = BinanceFuturesClient(True, binance_testnet_api_key, binance_testnet_api_secret)
    
    # bitmex = BitmexClient(True,bitmex_testnet_api_key,bitmex_testnet_api_secret)
    # print(bitmex.get_balances())

    #print(binance.get_balance())



    root = tk.Tk()  # main window
    root.mainloop()  # infinite loop waits for user interaction