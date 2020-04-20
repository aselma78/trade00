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


def update_candlestick_data(trade, interval_mins=1):
    global df
    print(trade)
    force_add = False
    #import ipdb;ipdb.set_trace()
    t = trade['T']
    t -= t % (5)
    c = float(trade['p'])
    if len(df) ==20:
        
        time_list=[]
        for i in range(20):
            time_list.append(t-i*5000)
        #import ipdb;ipdb.set_trace()
        time_list.reverse()
        df["t"] = time_list
        force_add = True
        # price=[t for i in range(20)]
        # df = pd.DataFrame(dict(t=time_list, o=price, c=price, h=price, l=price))
    if t < df['t'].iloc[-1]:
        # ignore already-recorded trades
        return
    elif t >= df['t'].iloc[-1]+5000 or force_add:
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
    #import ipdb;ipdb.set_trace()

if __name__ == '__main__':
    api_key=""
    api_secret = ""
    client = Client(api_key, api_secret)
    bm = BinanceSocketManager(client)
    try:        
        symbol = "ETHUSDT"
        model = TradingModel(symbol, timeframe="1m", num_frames=20)
        df = model.df.rename(columns={"time":"t", "close":"c", "open":"o", "high":"h", "low":"l", "volume":"v"})
        #df.drop(["v", "date"])
        
        bm.start_aggtrade_socket('ETHUSDT', update_candlestick_data)
        bm.start()

        fplt.create_plot('Realtime Websocket', init_zoom_periods=100, maximize=False)
        update_plot()
        fplt.timer_callback(update_plot, 2.0) # update every second
        fplt.show()
    except:
        bm.close()



# start_aggtrade_socket(symbol, callback)[source]

#     Start a websocket for symbol trade data

#     https://github.com/binance-exchange/binance-official-api-docs/blob/master/web-socket-streams.md#aggregate-trade-streams
#     Parameters: 

#         symbol (str) – required
#         callback (function) – callback function to handle messages

#     Returns:    

#     connection key string if successful, False otherwise

#     Message Format

#     {
#         "e": "aggTrade",                # event type
#         "E": 1499405254326,             # event time
#         "s": "ETHBTC",                  # symbol
#         "a": 70232,                             # aggregated tradeid
#         "p": "0.10281118",              # price
#         "q": "8.15632997",              # quantity
#         "f": 77489,                             # first breakdown trade id
#         "l": 77489,                             # last breakdown trade id
#         "T": 1499405254324,             # trade time
#         "m": false,                             # whether buyer is a maker
#         "M": true                               # can be ignored
#     }

