"""
First proof of concept plotting realtime wesocket data
"""
import finplot as fplt
import pandas as pd
import requests
from threading import Thread
from time import time



from TradingModel import TradingModel
from Binance import Binance
from binance.client import Client
from binance.websockets import BinanceSocketManager

import multiprocessing


plots = []


def update_plot():
    candlesticks = df['t o c h l'.split()]

    if not plots:
        candlestick_plot = fplt.candlestick_ochl(candlesticks)
        plots.append(candlestick_plot)

        candlestick_plot.colors.update(dict(
                bull_shadow = '#388d53',
                bull_frame  = '#205536',
                bull_body   = '#52b370',
                bear_shadow = '#d56161',
                bear_frame  = '#5c1a10',
                bear_body   = '#e8704f'))
        candlestick_plot.repaint()
    else:
        plots[0].update_data(candlesticks)

def update_candlestick_data(trade):
    global df
    global interval_secs
    global resolutions

    if interval_secs==resolutions[0]:
        print(trade)
    force_add = False
    t = trade['T']
    t -= t % (interval_secs)
    c = float(trade['p'])
    if len(df) ==20:
        
        time_list=[]
        for i in range(20):
            time_list.append(t-i*interval_secs*1000)
        time_list.reverse()
        df["t"] = time_list
        force_add = True
    if t < df['t'].iloc[-1]:
        # ignore already-recorded trades
        return
    elif t >= df['t'].iloc[-1]+interval_secs*1000 or force_add:
        #add new candle
        o = df['c'].iloc[-1]

        h = c if c>o else o
        l = o if o<c else c
        df1 = pd.DataFrame(dict(t=[t], o=[o], c=[c], h=[l], l=[l]))
        df = pd.concat([df, df1], ignore_index=True, sort=False)
    else:
        #update last candle
        i = df.index.max()
        df.loc[i,'c'] = c
        if c > df.loc[i,'h']:
            df.loc[i,'h'] = c
        if c < df.loc[i,'l']:
            df.loc[i,'l'] = c

def target():
    global client
    global symbol
    try:
        bm = BinanceSocketManager(client)
        bm.start_aggtrade_socket(symbol, update_candlestick_data)
        bm.start()

        fplt.create_plot(symbol+str(res), init_zoom_periods=100, maximize=False)
        update_plot()
        fplt.timer_callback(update_plot, 2.0) # update every second
        fplt.show()
    except:
        bm.close()


if __name__ == '__main__':
    api_key=""
    api_secret = ""
    client = Client(api_key, api_secret)

    resolutions=[60,20,10]
    processes = list()  
    symbol = "ETHUSDT"

    for res in resolutions:
        #import ipdb;ipdb.set_trace()
        interval_secs = res
        if res == 60:
            model = TradingModel(symbol, timeframe="1m", num_frames=200)
            df = model.df.rename(columns={"time":"t", "close":"c", "open":"o", "high":"h", "low":"l", "volume":"v"})
        elif res == 180:
            model = TradingModel(symbol, timeframe="3m")
            df = model.df.rename(columns={"time":"t", "close":"c", "open":"o", "high":"h", "low":"l", "volume":"v"})
        else:
            model = TradingModel(symbol, timeframe="1m", num_frames=20)
            df = model.df.rename(columns={"time":"t", "close":"c", "open":"o", "high":"h", "low":"l", "volume":"v"})

        process = multiprocessing.Process(target=target)
        processes.append(process)
        process.start()

    for process in processes:
        process.join()

