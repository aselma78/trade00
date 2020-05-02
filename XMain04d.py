"""
First proof of concept plotting realtime wesocket data
"""
import finplot as fplt
import pandas as pd
import requests
from threading import Thread



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
        self.first_update = True
        self.ax = None
        self.ax2 = None
        self.candlestick_plot = None
        self.volume_plot = None
        self.vask_plot = None
        self.vbid_plot = None
        self.delta_plot = None
        self.delta = 0

    def update_plot(self):
        
        candlesticks = self.df['t o c h l'.split()]
        volumes = self.df['t o c v'.split()]
        vask = self.df['t o c vask'.split()]
        vbid = self.df['t o c vbid'.split()]
        # delta = self.df['t o c delta'.split()]


        if self.first_update:
            self.first_update = False
            self.candlestick_plot = fplt.candlestick_ochl(candlesticks, ax=self.ax)
            self.volume_plot = fplt.volume_ocv(volumes, ax=self.ax2)
            self.vask_plot = fplt.volume_ocv(vask, ax=self.ax3)
            self.vbid_plot = fplt.volume_ocv(vbid, ax=self.ax4)
            # self.delta_plot = fplt.volume_ocv(delta, ax=self.ax5)
            self.delta_plot = fplt.plot(self.df['t'], self.df['delta'], ax=self.ax5, color='#0f0', legend='delta')

            self.candlestick_plot.colors.update(dict(
                    bull_shadow = '#388d53',
                    bull_frame  = '#205536',
                    bull_body   = '#52b370',
                    bear_shadow = '#d56161',
                    bear_frame  = '#5c1a10',
                    bear_body   = '#e8704f'))
            self.candlestick_plot.repaint()
            self.volume_plot.repaint()
            self.vask_plot.repaint()
            self.vbid_plot.repaint()
            # self.delta_plot.repaint()

        else:
            self.candlestick_plot.update_data(candlesticks)
            self.volume_plot.update_data(volumes)
            self.vask_plot.update_data(vask)
            self.vbid_plot.update_data(vbid)
            # self.delta_plot.update_data(delta)
            self.delta_plot.update_data(self.df['delta'])


    def update_candlestick_data(self,trade):        
        interval_secs = self.interval_secs
        resolutions = self.resolutions

        if interval_secs==resolutions[0]:
            pass
            #print(trade)
        force_add = False
        v = float(trade['q'])
        t = trade['T']
        t -= t % (interval_secs)
        c = float(trade['p'])

        if trade['m']:
            vbid = v
            vask = 0
        else:
            vbid = 0
            vask = v
        if len(self.df) ==20:
            time_list=[]
            for i in range(20):
                time_list.append(t-i*interval_secs*1000)
            time_list.reverse()
            self.df["t"] = time_list
            self.df["v"] = [0]*20
            force_add = True
        if t < self.df['t'].iloc[-1]:
            # ignore already-recorded trades
            return
        elif t >= self.df['t'].iloc[-1]+interval_secs*1000 or force_add:
            #add new candle
            o = self.df['c'].iloc[-1]

            h = c if c>o else o
            l = o if o<c else c
            df1 = pd.DataFrame(dict(t=[t], o=[o], c=[c], h=[l], l=[l], v=[v],vbid=[vbid], vask=[vask], delta=[vbid-vask]))
            self.df = pd.concat([self.df, df1], ignore_index=True, sort=False)
        else:
            #update last candle

            i = self.df.index.max()
            self.df.loc[i,'vbid'] += vbid
            self.df.loc[i,'vask'] += vask
            self.df.loc[i,'delta'] += vbid - vask
            self.delta  += vbid-vask
            if interval_secs==resolutions[0]:
                print(f"delta_acc: {self.delta:+}\t\tdelta_tmp: {self.df.loc[i,'delta']:+}", end='\r', flush=True)
            self.df.loc[i,'v'] += v
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

            self.ax, self.ax2, self.ax3, self.ax4, self.ax5 = fplt.create_plot(symbol+str(res), init_zoom_periods=100, maximize=False, rows=5)
            self.update_plot()
            fplt.timer_callback(self.update_plot, 2.0) # update every second
            fplt.show()
        except:
            bm.close()


if __name__ == '__main__':
    api_key=""
    api_secret = ""
    client = Client(api_key, api_secret)

    resolutions=[60,5]
    processes = list()  
    symbol = "BTCUSDT"

    for res in resolutions:
        #import ipdb;ipdb.set_trace()

        interval_secs = res
        if res == 60:
            model = TradingModel(symbol, timeframe="1m", num_frames=1440)
            df = model.df.rename(columns={"time":"t", "close":"c", "open":"o", "high":"h", "low":"l", "volume":"v"})
        elif res == 180:
            model = TradingModel(symbol, timeframe="3m")
            df = model.df.rename(columns={"time":"t", "close":"c", "open":"o", "high":"h", "low":"l", "volume":"v"})
        else:
            model = TradingModel(symbol, timeframe="1m", num_frames=20)
            df = model.df.rename(columns={"time":"t", "close":"c", "open":"o", "high":"h", "low":"l", "volume":"v"})
        df["vbid"] = [0]*len(df["t"])
        df["vask"] = [0]*len(df["t"])
        df["delta"] = [0]*len(df["t"])
        wst = WsTarget(df=df, client=client, symbol=symbol, interval_secs=interval_secs, resolutions=resolutions, plots=[])

        process = multiprocessing.Process(target=wst.target)
        processes.append(process)
        process.start()

    for process in processes:
        process.join()

