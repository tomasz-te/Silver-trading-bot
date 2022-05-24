# In TWS -> Configuration -> API -> Settings -> Mark Enalble ActiveX and Socket Clients and unmark Read-Only API
# Note Socket port

from math import floor
import pandas as pd
import yfinance as yf
import pandas_ta as ta
import pickle
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import *
import threading
import time


def get_slv_price():
    df = yf.Ticker("SLV")
    data = df.history()
    price = data['Close'].iloc[-1]
    return round(price,2)


# Preparing current input data for model
def generate_signal():
    df = yf.Ticker("SI=F")
    data = df.history(period="max")
    data.drop([column for column in data.columns if column not in ['Open','Close', 'High', 'Low']], axis=1, inplace=True)
    df = yf.Ticker("GC=F")
    gold = df.history(period="max")
    data['Gold'] = gold['Close']
    data['Gold'].fillna(method='ffill', inplace=True)
    windows = [10, 30, 100]

    for window in windows:
        data["Silver_"+str(window)] = data['Close'].rolling(window+1).apply(lambda x: (x.iloc[window] - x.iloc[0]) / x.iloc[0] * 100)
        data["Gold_"+str(window)] = data['Gold'].rolling(window+1).apply(lambda x: (x.iloc[window] - x.iloc[0]) / x.iloc[0] * 100)

    data['RSI_14']=ta.rsi(data['Close'],lenght=14)

    MACD = ta.macd(data['Close'],fast=12, slow=26, signal=9)
    data = pd.concat([data,MACD],axis=1)

    STOCH = ta.stoch(high=data.High,low=data.Low,close=data.Close)
    data = pd.concat([data, STOCH], axis=1)

    data.drop(['Open','High','Low','Close','Gold'], axis=1, inplace=True)

    model = pickle.load(open('model.sav', 'rb'))
    print(data.iloc[-1])
    current_signal = int(model.predict(data.iloc[-1:])[0])
    print('Current signal: ', current_signal)
    return current_signal



own_silver = int(input('Do you currently own SLV? 1 for yes, 0 for not: '))
if own_silver == 1:
    SLV_shares = int(input('How many shares do you own?'))
cash_balance = float(input('What is your current cash balance?'))

# Class For IB Connetction
class IBApi(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
    # Listen for real time Bar
    def realtimeBar(self, reqID, time, open, high, low, close, volume, wap, count):
        bot.on_bar_update(reqID, time, open, high, low, close, volume, wap, count)
# Bot Logic
class Bot:
    ib = None
    def __init__(self):
        self.ib = IBApi()
        self.ib.connect("127.0.0.1", 7498, 1) # 7497 for live
        ib_thread = threading.Thread(target=self.run_loop, daemon=True)
        ib_thread.start()
        time.sleep(1)
        symbol = 'SLV'
        # Create IB Contract object
        contract = Contract()
        contract.symbol = symbol.upper()
        contract.secType = 'STK'
        contract.exchange = 'SMART'
        contract.currency = 'USD'
        # Request real market data
        self.ib.reqRealTimeBars(0, contract, 5, 'TRADES', 1, [])

        if generate_signal() == 1:

            # Submit order
            # Create order object
            order = Order()
            order.orderType = 'MKT'
            order.action = 'BUY'
            quantity = floor(cash_balance / get_slv_price())
            order.totalQuantity = quantity
            # Create Contract Object
            contract = Contract()
            contract.symbol = symbol
            contract.secType = 'STK'
            contract.exchange = 'SMART'
            contract.primaryExchange = 'ISLAND'
            contract.currency = 'USD'
            # Place the order
            self.ib.placeOrder(1, contract, order)


    # Separate thread for code to run further
    def run_loop(self):
        self.ib.run()
    # Pass realtime bar data back to out bot object
    def on_bar_update(self, reqID, time, open, high, low, close, volume, wap, count):
        print(close)
# Start Bot
bot = Bot()
