import time
import tkinter as tk

from connectors.binance_futures import BinanceFuturesClient
from connectors.bitmex import BitmexClient

from interface.styling import *
from interface.logging_component import Logging
from interface.watchlist_component import Watchlist

class Root(tk.Tk):
    def __init__(self,binance: BinanceFuturesClient, bitmex: BitmexClient):
        super().__init__()
        
        self.binance = binance
        self.bitmex = bitmex
        
        self.title(APP_TITLE)
        
        self.configure(bg = BG_COLOR)

        self._left_frame = tk.Frame(self,bg=BG_COLOR)
        self._left_frame.pack(side = tk.LEFT)

        self._right_frame = tk.Frame(self,bg=BG_COLOR)
        self._right_frame.pack(side=tk.LEFT)
        
        self._watchlist_frame = Watchlist(self._left_frame, bg=BG_COLOR)
        self._watchlist_frame.pack(side=tk.TOP)

        self._logging_frame = Logging(self._left_frame,bg=BG_COLOR)
        self._logging_frame.pack(side=tk.TOP)

        self._update_ui()
    def _update_ui(self):

        for log in self.bitmex.logs:
            if not log["displayed"]:
                self._logging_frame.add_log(log["log"])
                log["displayed"] = True

        for log in self.binance.logs:
            if not log["displayed"]:
                self._logging_frame.add_log(log["log"])
                log["displayed"] = True

        self.after(1500,self._update_ui) #call function after 1.5 sec