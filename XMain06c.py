from binance.websockets import BinanceSocketManager
from binance.depthcache import DepthCacheManager
from binance.client import Client

import pandas as pd
import numpy as np
import math

from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg


class BarGraph(pg.BarGraphItem):
    def mouseClickEvent(self, event):
        print("clicked")


def update():
    global x
    global bg_ask, y_ask
    global bg_bid, y_bid

    bg_ask.setOpts(x=x, height=y_ask)
    bg_bid.setOpts(x=x, height=y_bid)
    

def process_trades(trade):
    global y_ask, y_bid
    global df_asks, df_bids
    # import ipdb;ipdb.set_trace()
    if trade["m"]:
        # df = pd.DataFrame.from_dict({"price":[trade["p"]], "quantity":[trade["q"]]})
        df_asks=df_asks.append({"price":trade["p"], "quantity":trade["q"]},  ignore_index=True)
        y_ask = histogram(df_asks)
    else:
        # df = pd.DataFrame.from_dict({"price":[trade["p"]], "quantity":[trade["q"]]})
        df_bids=df_bids.append({"price":trade["p"], "quantity":trade["q"]},  ignore_index=True)
        y_bid = histogram(df_bids)
    
    

def histogram(df):
    global rango, x, start, stop, step

    # x = np.arange(start, stop, step)
    y = np.zeros(len(x))

    # import ipdb;ipdb.set_trace()

    for i,prize in enumerate(df["price"]):
        price = float(prize)
        if price >= start and price < stop:
            index =  math.floor((price - x[0])/step)
            y[index] += float(df["quantity"][i])

    return y



## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    global rango
    global df_asks, y_ask
    global df_bids, y_bid
    global rango

    df_asks = pd.DataFrame()
    df_bids = pd.DataFrame()

    rango = [8500, 9000, .1]

    start = rango[0]
    stop = rango[1]
    step = rango[2]

    
    x = np.arange(start, stop, step)
    y_ask = np.zeros(len(x))
    y_bid = np.zeros(len(x))
    # df_asks=np.random.normal(size=(1,100))

    api_key=""
    api_secret = ""
    client = Client(api_key, api_secret)
    symbol = "BTCUSDT"

    bm = BinanceSocketManager(client)
    bm.start_trade_socket(symbol, process_trades)
    bm.start()



    # input()
    app = QtGui.QApplication([])
    win = pg.GraphicsWindow(title="Basic plotting examples")
    win.resize(1000,600)
    win.setWindowTitle('pyqtgraph example: Plotting')

    # Enable antialiasing for prettier plots
    pg.setConfigOptions(antialias=True)




    p6 = win.addPlot(title="Updating BarGraph")
    # x = np.arange(100)
    # y1=np.sin(x)
    #bg = pg.BarGraphItem(x=df_asks[0], height=np.log(1+df_asks[1]), width=rango[2], brush='r')
    bg_ask = pg.BarGraphItem(x=x, height=y_ask, width=rango[2], brush='r')
    bg_bid = pg.BarGraphItem(x=x, height=y_bid, width=rango[2], brush='g')

    p6.addItem(bg_ask)
    p6.addItem(bg_bid)

    timer = QtCore.QTimer()
    timer.timeout.connect(update)
    timer.start(50)


    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()

