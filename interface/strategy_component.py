from connectors.bitmex import BitmexClient
from connectors.binance_futures import BinanceFuturesClient
import tkinter as tk
from tkinter.font import BOLD
from interface.styling import *
import typing
from tkinter import ttk


class StrategyEditor(tk.Frame):
    def __init__(self,root,binance:BinanceFuturesClient,bitmex:BitmexClient,*args,**kwargs):
        super().__init__(*args,**kwargs)
        
        self.root = root

        self._exchanges = {
            "Binance": binance,
            "Bitmex": bitmex
        }
        
        self._all_timeframes = ["1m","5m","15m","30m","1h","4h"]
        
        self._all_contracts = []
        for exchange,client in self._exchanges.items():
            for symbol, contract in client.contracts.items():
                
                self._all_contracts.append(symbol + "_" + exchange.capitalize())


        self._commands_frame = tk.Frame(self,bg=BG_COLOR)
        self._commands_frame.pack(side=tk.TOP)

        self._table_frame = tk.Frame(self,bg=BG_COLOR)
        self._table_frame.pack(side=tk.TOP)


        self._add_button = tk.Button(self._commands_frame, text="Add strategy", font=GLOBAL_FONT,
                                    command=self._add_strategy_row, bg=BG_COLOR_2, fg=FG_COLOR)
        
        self._add_button.pack(side=tk.TOP)

        self.body_widgets = dict()

        self._headers = [ "Contract","Strategy", "Timeframe", "Balance %", "TP %", "SL %"]
        
        self._base_params = [
                            {"code_name":"contract","widget":ttk.Combobox,"data_type":str,
                            "values":self._all_contracts,"width":15},

                            {"code_name":"strategy_type","widget":tk.OptionMenu,"data_type":str,
                            "values":["Technical","Breakout"],"width":10},
                            
                            {"code_name":"timeframe","widget":tk.OptionMenu,"data_type":str,
                            "values":self._all_timeframes,"width":7},

                            {"code_name":"balance_percentage","widget":tk.Entry,"data_type":float,
                            "width":7},

                            {"code_name":"take_profit","widget":tk.Entry,"data_type":float,
                            "width":7},
                            
                            {"code_name":"stop_loss","widget":tk.Entry,"data_type":float,
                            "width":7},

                            {"code_name":"parameters","widget":tk.Button,"data_type":float,
                            "text":"Parameters", "bg": BG_COLOR_2,"command":self._show_popup},

                            {"code_name":"activation","widget":tk.Button,"data_type":float,
                            "text":"OFF", "bg": DANGER_COLOR,"command":self._switch_strategy},

                            {"code_name":"delete","widget":tk.Button,"data_type":float,
                            "text":REMOVE_ICON, "bg": DANGER_COLOR,"command":self._delete_row},
        
        ]
        
        self._additional_parameters = dict()
        
        self._extra_input = dict()

        self._extra_params = {
            "Technical":[
                {"code_name":"ema_fast","name":"MACD Fast Length","widget":tk.Entry,"data_type":int},
                {"code_name":"ema_slow","name":"MACD Slow Length","widget":tk.Entry,"data_type":int},
                {"code_name":"ema_signal","name":"MACD Signal Length","widget":tk.Entry,"data_type":int},


            ],
            "Breakout":[
                {"code_name":"min_volume","name":"Minimum Volume","widget":tk.Entry,"data_type":float}
            ]
        }
        


        for idx, header in enumerate(self._headers):
            header = tk.Label(self._table_frame,text=header,bg=BG_COLOR, fg=FG_COLOR, font=BOLD_FONT)
            header.grid(row=0,column=idx)

        for h in self._base_params:
            self.body_widgets[h["code_name"]] = dict()

            if h["widget"] in  [tk.OptionMenu,ttk.Combobox]:
                self.body_widgets[h["code_name"] + "_var"] = dict() #to manage dynamic values

        self._body_index = 1

        
    def _add_strategy_row(self):
       
        b_index = self._body_index

        for col, base_param in enumerate(self._base_params):
            code_name = base_param["code_name"]

            if base_param["widget"] == tk.OptionMenu:

                self.body_widgets[code_name+"_var"][b_index] = tk.StringVar()
                self.body_widgets[code_name+"_var"][b_index].set(base_param["values"][0]) #set first elements as default

                self.body_widgets[code_name][b_index] = tk.OptionMenu(self._table_frame,self.body_widgets[code_name+"_var"][b_index],
                                                                      *base_param["values"])

                self.body_widgets[code_name][b_index].config(width=base_param["width"])
            
            elif base_param["widget"] == ttk.Combobox:

                self.body_widgets[code_name+"_var"][b_index] = tk.StringVar()
                self.body_widgets[code_name+"_var"][b_index].set(base_param["values"][0]) #set first elements as default

                self.body_widgets[code_name][b_index] = ttk.Combobox(self._table_frame,textvariable=self.body_widgets[code_name+"_var"][b_index]
                                                                    ,width=15,height=20,justify=tk.CENTER)
                self.body_widgets[code_name][b_index]["values"] = tuple(base_param["values"])
                self.body_widgets[code_name][b_index]["state"] = "readonly"
                

            elif base_param["widget"] == tk.Entry:
                self.body_widgets[code_name][b_index] = tk.Entry(self._table_frame,justify=tk.CENTER)
            
            elif base_param["widget"] == tk.Button:
                self.body_widgets[code_name][b_index] = tk.Button(self._table_frame,text=base_param["text"],
                                                                bg=base_param["bg"],fg=FG_COLOR,
                                                                command= lambda frozen_command=base_param["command"]: frozen_command(b_index))

            
            else:
                continue
            
            
            self.body_widgets[code_name][b_index].grid(row=b_index,column=col,padx=15, pady=15)

           

        
        self._additional_parameters[b_index] = dict()

        for strat, params in self._extra_params.items():
            for param in params:
                self._additional_parameters[b_index][param["code_name"]] = None

        self._body_index += 1
         
    def _delete_row(self, b_index: int):
        
        for element in self._base_params:
            self.body_widgets[element["code_name"]][b_index].grid_forget() #remove from ui

            del self.body_widgets[element["code_name"]][b_index] #remove from dict

    def _show_popup(self, b_index: int):
        
        self._popup_window = tk.Toplevel(self)

        #Clicked button coordinates
        x = self.body_widgets["parameters"][b_index].winfo_rootx()
        y = self.body_widgets["parameters"][b_index].winfo_rooty()
        

        self._popup_window.wm_title("Parameters")
        self._popup_window.configure(bg=BG_COLOR)
        self._popup_window.attributes("-topmost","true")
        self._popup_window.geometry(f"+{x-70}+{y+40}") #coordinates of popup window

        #if grab_set is called, when popup opens it won't allow to click other windows
        #self._popup_window.grab_set()

        strategy_selected = self.body_widgets["strategy_type_var"][b_index].get()

        row_nb = 0
        
        #ADD POPUP CONTENT
        for param in self._extra_params[strategy_selected]:
            code_name = param["code_name"]

            temp_label = tk.Label(self._popup_window,bg=BG_COLOR,fg=FG_COLOR,text=param["name"],font=BOLD_FONT)
            temp_label.grid(row=row_nb,column=0)

            if param["widget"] == tk.Entry:
                self._extra_input[code_name] = tk.Entry(self._popup_window,bg=BG_COLOR_2,justify=tk.CENTER,fg=FG_COLOR,insertbackground=FG_COLOR)
                
                
                # if there is a validated input, keep them
                previous_input =  self._additional_parameters[b_index][code_name]

                if previous_input is not None:
                    self._extra_input[code_name].insert(tk.END,str(previous_input))
            else:
                continue
            
            
            self._extra_input[code_name].grid(row=row_nb,column=1)

            row_nb += 1
        
        # VALIDATION BUTTON
        validation_btn = tk.Button(self._popup_window,bg=SUCCESS_COLOR, fg=FG_COLOR, text="Validate",
                                    command= lambda: self._validate_parameters(b_index))
        
        validation_btn.grid(row=row_nb,column=0,columnspan=2)
    def _validate_parameters(self,b_index:int):
        
        strategy_selected = self.body_widgets["strategy_type_var"][b_index].get()

        for param in self._extra_params[strategy_selected]:
            code_name = param["code_name"]

            extra_input = self._extra_input[code_name].get()
            if extra_input == "":
                self._additional_parameters[b_index][code_name] = None
            else:
                self._additional_parameters[b_index][code_name] = param["data_type"](extra_input) #convert str to correct data type

        
        self._popup_window.destroy() 
    
    def _switch_strategy(self, b_index: int):
        
        for param in ["balance_percentage","take_profit","stop_loss"]:
            if self.body_widgets[param][b_index].get() == "":
                self.root.logging_frame.add_log(f"Missing {param} parameter!")
                return
        
        strategy_selected = self.body_widgets["strategy_type_var"][b_index].get()

        for param in self._extra_params[strategy_selected]:
            if self._additional_parameters[b_index][param["code_name"]] is None:
                self.root.logging_frame.add_log(f"Missing {param['code_name']} parameter!")
                return

        symbol = self.body_widgets["contract_var"][b_index].get().split("_")[0]
        exchange = self.body_widgets["contract_var"][b_index].get().split("_")[1]
        timeframe = self.body_widgets["timeframe_var"][b_index].get()

        balance_percentage = float(self.body_widgets["balance_percentage"][b_index].get())
        take_profit = float(self.body_widgets["take_profit"][b_index].get())
        stop_loss = float(self.body_widgets["stop_loss"][b_index].get())

        if self.body_widgets["activation"][b_index].cget("text") == "OFF":

            for param in self._base_params:
                code_name = param["code_name"]

                if code_name != "activation" and "_var" not in code_name:
                    #if user has a running order he can't change current entries
                    self.body_widgets[code_name][b_index].config(state=tk.DISABLED)

            self.body_widgets["activation"][b_index].config(bg=SUCCESS_COLOR, text="ON")

            self.root.logging_frame.add_log(f"{strategy_selected} strategy on {symbol}/{timeframe} started")

        else:
            for param in self._base_params:
                code_name = param["code_name"]

                if code_name != "activation" and "_var" in code_name:
                    #if user has a running order he can't change current entries
                    self.body_widgets[code_name][b_index].config(state=tk.NORMAL)

            self.body_widgets["activation"][b_index].config(bg=DANGER_COLOR, text="OFF")

            self.root.logging_frame.add_log(f"{strategy_selected} strategy on {symbol}/{timeframe} stopped")

