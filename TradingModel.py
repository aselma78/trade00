import pandas as pd
import numpy as np
import requests
import json

import plotly.graph_objs as go
from plotly.offline import plot
from plotly.subplots import make_subplots

from finta import TA
from pyti.smoothed_moving_average import smoothed_moving_average as sma
from pyti.bollinger_bands import lower_bollinger_band as lbb
from pyti.bollinger_bands import upper_bollinger_band as ubb

from importlib import reload
from . import Binance as bi
from . import Indicators as ind
reload(bi)
reload(ind)

class TradingModel:
    
    def __init__(self, symbol):
        self.symbol = symbol
        self.exchange = bi.Binance()
        self.df = self.exchange.GetSymbolData(symbol, '4h')
        self.last_price = self.df['close'][len(self.df['close'])-1]
        self.buy_signals = []

        try:
            self.df['fast_sma'] = sma(self.df['close'].tolist(), 10)
            self.df['slow_sma'] = sma(self.df['close'].tolist(), 30)
            self.df['low_boll'] = lbb(self.df['close'].tolist(), 14)
            self.df['up_boll'] = ubb(self.df['close'].tolist(), 14)
            self.df['vwap'] = (self.df['volume']*(self.df['close'])).cumsum() / self.df['volume'].cumsum()
            #self.df['vwap'] = (self.df['volume']*(self.df['high']+self.df['low'])/2).cumsum() / self.df['volume'].cumsum()
            self.df['vwma'] = self.vwma(14)

            # From Indicators
            self.df = ind.macd(self.df)
            self.df = ind.money_flow_index(self.df)
            self.df = ind.rsi(self.df)

            #From Finta
            vw_macd = TA.VW_MACD(self.df)
            self.df['vw_macd'] = vw_macd['MACD']
            self.df['vw_macd_sig'] = vw_macd['SIGNAL']
            

        except Exception as e:
            print(" Exception raised when trying to compute indicators on "+self.symbol)
            print(e)
            return None

    def vwma(self, n):
        #import ipdb; ipdb.set_trace()

        vector_size = len(self.df['volume'])

        aux_volume = np.concatenate(( np.zeros(n),  self.df['volume'].values ))
        aux_weighted_price = np.zeros( n + vector_size )

        tmp1 = np.zeros(vector_size)
        tmp2 = np.zeros(vector_size)
        for i in range(0,vector_size):
            weighted_price = self.df['volume'][i] * ( self.df['high'][i] + self.df['low'][i] ) / 2.            

            tmp1[i] = tmp1[i-1] + weighted_price - aux_weighted_price[i]
            tmp2[i] = tmp2[i-1] + self.df['volume'][i] - aux_volume[i]

            aux_weighted_price[i+n] = weighted_price

        return tmp1 / tmp2

    def strategy(self): 
        
        '''If Price is 3% below Slow Moving Average, then Buy
        Put selling order for 2% above buying price'''

        df = self.df

        buy_signals = []

        for i in range(1, len(df['close'])):
            if df['slow_sma'][i] > df['low'][i] and (df['slow_sma'][i] - df['low'][i]) > 0.03 * df['low'][i]:
                buy_signals.append([df['time'][i], df['low'][i]])

        self.plotData(buy_signals = buy_signals)

    def plotData(self, buy_signals = False):
        df = self.df

        INCREASING_COLOR = '#3D9970'
        DECREASING_COLOR = '#FF4136'

        colors = []
        data = []

        for i in range(len(df['close'])):
            if i != 0:
                if df['close'][i] > df['close'][i-1]:
                    colors.append(INCREASING_COLOR)
                else:
                    colors.append(DECREASING_COLOR)
            else:
                colors.append(DECREASING_COLOR)


        # plot candlestick chart
        candle = go.Candlestick(
            x = df['time'],
            open = df['open'],
            close = df['close'],
            high = df['high'],
            low = df['low'],
            name = "Candlesticks")

        # plot MAs
        fsma = go.Scatter(
            x = df['time'],
            y = df['fast_sma'],
            name = "Fast SMA",
            line = dict(color = ('rgba(102, 207, 255, 50)')))

        ssma = go.Scatter(
            x = df['time'],
            y = df['slow_sma'],
            name = "Slow SMA",
            line = dict(color = ('rgba(255, 207, 102, 50)')))

        lowbb = go.Scatter(
            x = df['time'],
            y = df['low_boll'],
            name = "Lower Bollinger Band",
            line = dict(color = ('rgba(255, 102, 207, 50)')))

        upbb = go.Scatter(
            x = df['time'],
            y = df['up_boll'],
            name = "Upper Bollinger Band",
            line = dict(color = ('rgba(255, 102, 207, 50)')))

        vwap = go.Scatter(
            x = df['time'],
            y = df['vwap'],
            name = "Vwap",
            line = dict(color = ('rgba(255, 102, 107, 50)')))

        for i in range(5,455,100):
            vwma = go.Scatter(
                x = df['time'],
                y = self.vwma(i),
                name = "vwma"+str(i),
                line = dict(color = ('rgba(0, 255, 0, 50)')))
            data.append(vwma)

        vol = go.Bar(
            x = df['time'],
            y = df['volume'],
            marker=dict(color = colors),       
            name = "volume") 

        macd_val = go.Scatter(
            x = df['time'],
            y = df['macd_val'],
            name = "macd_val",
            line = dict(color = ('rgba(255, 102, 107, 50)')))

        macd_signal_line = go.Scatter(
            x = df['time'],
            y = df['macd_signal_line'],
            name = "macd_signal_line",
            line = dict(color = ('rgba(255, 0, 0, 50)')))

        vw_macd = go.Scatter(
            x = df['time'],
            y = df['vw_macd'],
            name = "vw_macd",
            line = dict(color = ('rgba(123, 255, 107, 50)')))

        vw_macd_sig = go.Scatter(
            x = df['time'],
            y = df['vw_macd_sig'],
            name = "vw_macd_sig",
            line = dict(color = ('rgba(0, 255, 0, 50)')))

        mfi = go.Scatter(
            x = df['time'],
            y = 1 - df['money_flow_index'],
            name = "money_flow_index",
            line = dict(color = ('rgba(0, 0, 255, 50)')))

        rsi = go.Scatter(
            x = df['time'],
            y = df['rsi'],
            name = "rsi",
            line = dict(color = ('rgba(0, 255, 255, 50)')))

        

        data.extend([candle, vwap])

        if buy_signals:
            buys = go.Scatter(
                    x = [item[0] for item in buy_signals],
                    y = [item[1] for item in buy_signals],
                    name = "Buy Signals",
                    mode = "markers",
                )

            sells = go.Scatter(
                    x = [item[0] for item in buy_signals],
                    y = [item[1]*1.05 for item in buy_signals],
                    name = "Sell Signals",
                    mode = "markers",
                )

            data = [candle, ssma, fsma, buys, sells]


        # style and display
        layout = go.Layout(title = self.symbol)

        fig = make_subplots(rows=4, cols=1, shared_xaxes=True, row_heights=[100,25,25,25])

        #fig = go.Figure()
        #fig = go.Figure(data = data, layout = layout)
        #fig = go.Figure(data = data)
        for gobject in data:
            fig.add_trace(gobject,row=1,col=1)
        
        fig.add_trace(vol,row=2,col=1)        

        fig.add_trace(rsi,row=3,col=1)
        fig.add_trace(mfi,row=3,col=1)

        fig.add_trace(macd_val,row=4,col=1)
        fig.add_trace(macd_signal_line,row=4,col=1)
        fig.add_trace(vw_macd,row=4,col=1)
        fig.add_trace(vw_macd_sig,row=4,col=1)

        fig.layout.template = "plotly_dark"


        plot(fig, filename=self.symbol+'.html')


    def maStrategy(self, i:int):
        ''' If price is 10% below the Slow MA, return True'''

        df = self.df
        buy_price = 0.8 * df['slow_sma'][i]
        if buy_price >= df['close'][i]:
            self.buy_signals.append([df['time'][i], df['close'][i], df['close'][i] * 1.045])
            return True

        return False

    def bollStrategy(self, i:int):
        ''' If price is 5% below the Lower Bollinger Band, return True'''

        df = self.df
        buy_price = 0.98 * df['low_boll'][i]
        if buy_price >= df['close'][i]:
            self.buy_signals.append([df['time'][i], df['close'][i], df['close'][i] * 1.045])
            return True

        return False


def Main():

    exchange = bi.Binance()
    symbols = exchange.GetTradingSymbols()
    for symbol in symbols:

        # import pdb; pdb.set_trace()
        input("\nPress key to continue...")
        print(symbol)
        model = TradingModel(symbol)
        plot = True
        
        # if model.maStrategy(len(model.df['close'])-1):
        #   print(" MA Strategy match on "+symbol)
        #   plot = True

        if model.bollStrategy(len(model.df['close'])-1):
            print(" Boll Strategy match on "+symbol)
            plot = True

        if plot:
            model.plotData()

if __name__ == '__main__':
    Main()
