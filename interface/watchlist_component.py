import tkinter as tk
from tkinter.font import BOLD
from interface.styling import *

class Watchlist(tk.Frame):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

        self._commands_frame = tk.Frame(self,bg=BG_COLOR)
        self._commands_frame.pack(side=tk.TOP)

        self._table_frame = tk.Frame(self, bg=BG_COLOR)
        self._table_frame.pack(side= tk.TOP)

        self._binance_label = tk.Label(self._commands_frame,text="BINANCE", bg=BG_COLOR,fg=FG_COLOR,font=BOLD_FONT)
        self._binance_label.grid(row=0,column=0)

        self._binance_entry = tk.Entry(self._commands_frame,bg=BG_COLOR_2, fg=FG_COLOR, justify=tk.CENTER, insertbackground=FG_COLOR)
        self._binance_entry.grid(row=1,column=0)

        self._bitmex_label = tk.Label(self._commands_frame,text="BITMEX", bg=BG_COLOR,fg=FG_COLOR,font=BOLD_FONT)
        self._bitmex_label.grid(row=0,column=1)

        self._bitmex_entry = tk.Entry(self._commands_frame,bg=BG_COLOR_2, fg=FG_COLOR, justify=tk.CENTER, insertbackground=FG_COLOR)
        self._bitmex_entry.grid(row=1,column=1)
