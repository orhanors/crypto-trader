import tkinter as tk
from interface.styling import *
from datetime import datetime
class Logging(tk.Frame):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

        self._logging_text = tk.Text(self,height=10,width=60,state=tk.DISABLED,bg=BG_COLOR, fg=FG_COLOR_2,font=GLOBAL_FONT)
        self._logging_text.pack(side=tk.TOP)

    def add_log(self,message:str):
        self._logging_text.configure(state=tk.NORMAL)

        self._logging_text.insert("1.0", datetime.now().strftime("%a %H:%M:%S :: ") + message + "\n") # 1.0 indicates that latest message will be on the top

        self._logging_text.configure(state=tk.DISABLED)