import pandas as pd
import requests
import json

import numpy as np
import Indicators

import plotly.graph_objs as go
from plotly.offline import plot
from plotly.subplots import make_subplots

import finplot as fplt

from Binance import Binance

# size of requested dataframe
N = 2000

class TradingModel:
    
    # We can now remove the code where we're computing the indicators from this class,
    # As we will be computing them in the Strategies class (on a per-need basis)

    def __init__(self, symbol, timeframe:str='4h', exchange:str="Binance", num_frames:int=N):
        self.symbol = symbol
        self.timeframe = timeframe
        if exchange == "Binance":
            self.exchange = Binance()
            self.df = self.exchange.GetSymbolKlines(symbol, timeframe, num_frames)
            self.last_price = self.df['close'][len(self.df['close'])-1]
        else:
            self.df = pd.read_csv("empty.csv")

    # We'll look directly in the dataframe to see what indicators we're plotting

    def plotData(self, buy_signals = False, sell_signals = False, plot_title:str="",target="default",
                indicators=[]):
        if target=="default":
            self.plotFinplot(buy_signals=buy_signals, sell_signals=sell_signals, plot_title=plot_title,
                indicators=indicators)
        else:
            self.plotLy(buy_signals=buy_signals, sell_signals=sell_signals, plot_title=plot_title,
                indicators=indicators)

    def plotFinplot(self, buy_signals = False, sell_signals = False, plot_title:str="",
    indicators=[]):
        df = self.df

        ax,ax2,ax3 = fplt.create_plot(self.symbol, rows=3)

        # plot candle sticks
        candles = df[['time','open','close','high','low']]
        fplt.candlestick_ochl(candles, ax=ax)

        # put an MA in there
        fplt.plot(df['time'], df['close'].rolling(25).mean(), ax=ax, color='#00f', legend='ma-25')

        # place some dumb markers
        #hi_wicks = df['high'] - df[['open','close']].T.max()
        #df.loc[(hi_wicks>hi_wicks.quantile(0.99)), 'marker'] = df['high']
        #fplt.plot(df['time'], df['marker'], ax=ax, color='#0F0', style='v', legend='dummy mark')

        #hi_wicks = df[['open','close']].T.min() - df['low']
        #df.loc[(hi_wicks>hi_wicks.quantile(0.99)), 'marker'] = df['low']
        #fplt.plot(df['time'], df['marker'], ax=ax, color='#F00', style='v', legend='dumb mark')

        fplt.plot(df['time'], Indicators.vwma(df)['vwma'], ax=ax, color='#927', legend='vwma')

        fplt.plot(df['time'], df['50_ema'], ax=ax, color='#ccc', legend='50 EMA')
        fplt.plot(df['time'], df['200_ema'], ax=ax, color='#ddd', legend='200 EMA')

        # draw some random crap on our second plot
        fplt.plot(df['time'], Indicators.rsi(df)['rsi'], ax=ax2, color='#927', legend='rsi')
        fplt.set_y_range(-1.4, +1.7, ax2) # fix y-axis range

        fplt.plot(df['time'], 0.3*np.ones(len(df['time'])), ax=ax2, color='#ccc', legend='30%')
        fplt.plot(df['time'], 0.7*np.ones(len(df['time'])), ax=ax2, color='#ccc', legend='70%')

        # finally a volume bar chart in our third plot
        volumes = df[['time','open','close','volume']]
        fplt.volume_ocv(volumes, ax=ax3)

        # buy/sell signals
        if buy_signals:
            x = [float(item[0]) for item in buy_signals]
            y = [float(item[1]) for item in buy_signals]
            fplt.plot(x, y, ax=ax, color='#00FF00', style='v', legend='Buy Signals')

        if sell_signals:
            x = [float(item[0]) for item in sell_signals]
            y = [float(item[1]) for item in sell_signals]
            fplt.plot(x, y, ax=ax, color='#FF0000', style='v', legend='Sell Signals')
            
        # we're done
        fplt.show()

    def plotLy(self, buy_signals = False, sell_signals = False, plot_title:str="",
            indicators=[
                dict(col_name="fast_ema", color="indianred", name="FAST EMA"), 
                dict(col_name="50_ema", color="indianred", name="50 EMA"), 
                dict(col_name="200_ema", color="indianred", name="200 EMA")]):
        df = self.df

        # plot candlestick chart
        candle = go.Candlestick(
            x = df['time'],
            open = df['open'],
            close = df['close'],
            high = df['high'],
            low = df['low'],
            name = "Candlesticks")

        data = [candle]

        for item in indicators:
            if df.__contains__(item['col_name']):
                fsma = go.Scatter(
                    x = df['time'],
                    y = df[item['col_name']],
                    name = item['name'],
                    line = dict(color = (item['color'])))
                data.append(fsma)

        # if df.__contains__('50_ema'):
        #   fsma = go.Scatter(
        #       x = df['time'],
        #       y = df['50_ema'],
        #       name = "50 EMA",
        #       line = dict(color = ('rgba(102, 207, 255, 50)')))
        #   data.append(fsma)

        # if df.__contains__('200_ema'):
        #   fsma = go.Scatter(
        #       x = df['time'],
        #       y = df['200_ema'],
        #       name = "200 EMA",
        #       line = dict(color = ('rgba(102, 207, 255, 50)')))
        #   data.append(fsma)

        if df.__contains__('fast_sma'):
            fsma = go.Scatter(
                x = df['time'],
                y = df['fast_sma'],
                name = "Fast SMA",
                line = dict(color = ('rgba(102, 207, 255, 50)')))
            data.append(fsma)

        if df.__contains__('slow_sma'):
            ssma = go.Scatter(
                x = df['time'],
                y = df['slow_sma'],
                name = "Slow SMA",
                line = dict(color = ('rgba(255, 207, 102, 50)')))
            data.append(ssma)

        if df.__contains__('low_boll'):
            lowbb = go.Scatter(
                x = df['time'],
                y = df['low_boll'],
                name = "Lower Bollinger Band",
                line = dict(color = ('rgba(255, 102, 207, 50)')))
            data.append(lowbb)

        # Now, Let's also plot the Ichimoku Indicators

        if df.__contains__('tenkansen'):
            trace = go.Scatter(
                x = df['time'],
                y = df['tenkansen'],
                name = "Tenkansen",
                line = dict(color = ('rgba(40, 40, 141, 100)')))
            data.append(trace)
        
        if df.__contains__('kijunsen'):
            trace = go.Scatter(
                x = df['time'],
                y = df['kijunsen'],
                name = "Kijunsen",
                line = dict(color = ('rgba(140, 40, 40, 100)')))
            data.append(trace)

        if df.__contains__('senkou_a'):
            trace = go.Scatter(
                x = df['time'],
                y = df['senkou_a'],
                name = "Senkou A",
                line = dict(color = ('rgba(160, 240, 160, 100)')))
            data.append(trace)
    
        # As you saw in the chart earlier, the portion between Senkou A and B
        # is filled, either with red or with green. Here, We'll only be using red
        # I haven't found a proper way to change the colors of the fill based on
        # who is on top (Senkou A or B). If you have a way, please put it into the
        # comments, or bettew yet, write it in the code on github (make a pull request)!!

        if df.__contains__('senkou_b'):
            trace = go.Scatter(
                x = df['time'],
                y = df['senkou_b'],
                name = "Senkou B",
                fill = "tonexty",
                line = dict(color = ('rgba(240, 160, 160, 50)')))
            data.append(trace)

        if buy_signals:
            buys = go.Scatter(
                    x = [item[0] for item in buy_signals],
                    y = [item[1] for item in buy_signals],
                    name = "Buy Signals",
                    mode = "markers",
                    marker_size = 20
                )
            data.append(buys)

        if sell_signals:
            sells = go.Scatter(
                x = [item[0] for item in sell_signals],
                y = [item[1] for item in sell_signals],
                name = "Sell Signals",
                mode = "markers",
                marker_size = 20
            )
            data.append(sells)

        # style and display
        # let's customize our layout a little bit:
        layout = go.Layout(
            title=plot_title,
            xaxis = {
                "title" : self.symbol,
                "rangeslider" : {"visible": False},
                "type" : "date"
            },
            yaxis = {
                "fixedrange" : False,
            })
            
        fig = go.Figure(data = data, layout = layout)

        plot(fig, filename='graphs/'+plot_title+'.html')
    

if __name__ == '__main__':
    pass
