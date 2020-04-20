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


class WsTarget:
    def __init__(self, df, client=None, symbol="ETHUSD", interval_secs=5, resolutions=[5], plots=[]):
        self.df = df
        self.client = client
        self.symbol = symbol
        self.interval_secs = interval_secs
        self.resolutions = resolutions
        self.plots = plots

    def update_plot(self):
        candlesticks = self.df['t o c h l'.split()]

        if not self.plots:
            candlestick_plot = fplt.candlestick_ochl(candlesticks)
            self.plots.append(candlestick_plot)

            candlestick_plot.colors.update(dict(
                    bull_shadow = '#388d53',
                    bull_frame  = '#205536',
                    bull_body   = '#52b370',
                    bear_shadow = '#d56161',
                    bear_frame  = '#5c1a10',
                    bear_body   = '#e8704f'))
            candlestick_plot.repaint()
        else:
            self.plots[0].update_data(candlesticks)

    def update_candlestick_data(self,trade):
        interval_secs = self.interval_secs
        resolutions = self.resolutions

        if interval_secs==resolutions[0]:
            print(trade)
        force_add = False
        t = trade['T']
        t -= t % (interval_secs)
        c = float(trade['p'])
        if len(self.df) ==20:
            
            time_list=[]
            for i in range(20):
                time_list.append(t-i*interval_secs*1000)
            time_list.reverse()
            self.df["t"] = time_list
            force_add = True
        if t < self.df['t'].iloc[-1]:
            # ignore already-recorded trades
            return
        elif t >= self.df['t'].iloc[-1]+interval_secs*1000 or force_add:
            #add new candle
            o = self.df['c'].iloc[-1]

            h = c if c>o else o
            l = o if o<c else c
            df1 = pd.DataFrame(dict(t=[t], o=[o], c=[c], h=[l], l=[l]))
            self.df = pd.concat([self.df, df1], ignore_index=True, sort=False)
        else:
            #update last candle
            i = self.df.index.max()
            self.df.loc[i,'c'] = c
            if c > self.df.loc[i,'h']:
                self.df.loc[i,'h'] = c
            if c < self.df.loc[i,'l']:
                self.df.loc[i,'l'] = c

    def target(self):
        client = self.client
        symbol = self.symbol
        try:
            bm = BinanceSocketManager(client)
            bm.start_aggtrade_socket(symbol, self.update_candlestick_data)
            bm.start()

            fplt.create_plot(symbol+str(res), init_zoom_periods=100, maximize=False)
            self.update_plot()
            fplt.timer_callback(self.update_plot, 2.0) # update every second
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

        wst = WsTarget(df=df, client=client, symbol=symbol, interval_secs=interval_secs, resolutions=resolutions, plots=[])

        process = multiprocessing.Process(target=wst.target)
        processes.append(process)
        process.start()

    for process in processes:
        process.join()

