import sqlite3
from decimal import Decimal
from binance.client import Client
from binance.websockets import BinanceSocketManager
from binance.depthcache import DepthCacheManager
import traceback
import time

def adapt_decimal(d):
    return format(round(d, 14), 'f')

def convert_decimal(s):
    return Decimal(s)

class OrderBookDatabase:

    def __init__(self, name:str):
        
        sqlite3.register_adapter(Decimal, adapt_decimal)
        sqlite3.register_converter("decimal", convert_decimal)
        self.name = name
        self.Initialise()
        
    def Initialise(self):
        ''' Initialises the Database ''' 

        conn = sqlite3.connect(self.name, detect_types=sqlite3.PARSE_DECLTYPES)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        # Create tables
        c.execute('''CREATE TABLE IF NOT EXISTS obook (
            time int,
            bidask bool,
            price real, 
            quantity real
            )''')

        conn.commit()

    def SaveOrderChunk(self, ochunk):
        '''
        Adds Book Orders to the Database
        '''
        conn = sqlite3.connect(self.name, detect_types=sqlite3.PARSE_DECLTYPES)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()

        for order in ochunk['b']:
            values = (
                ochunk['E'],
                True, 
                order[0],
                order[1] )
            c.execute('INSERT INTO obook VALUES (?, ?, ?, ?)', values)
        for order in ochunk['a']:
            values = (
                ochunk['E'],
                False, 
                order[0],
                order[1] )
            c.execute('INSERT INTO obook VALUES (?, ?, ?, ?)', values)
        conn.commit()

def callback_init_db(res):
    # print("\n\n------------------------------------")
    # tm = int(time.time()*1000)
    print(res)
    msg = dict()
    msg['E'] = int(time.time()*1000)
    msg['b'] = res['bids']
    msg['a'] = res['asks']
    obookdb.SaveOrderChunk(msg)
    # pass

def callback_db(msg):
    global obookdb
    #if trade['f'] != trade['l']:
    # tradedb.SaveTrade(trade)
    # print("\n\n------------------------------------")
    obookdb.SaveOrderChunk(msg)
    print(msg)
    # pass

if __name__ == '__main__':
    symbol = "BTCUSDT"
    obookdb = OrderBookDatabase("DATA/" + symbol + "_book.db")
    api_key=""
    api_secret = ""
    client = Client(api_key, api_secret)
    bm = BinanceSocketManager(client)
    try:
        DepthCacheManager(client, symbol, callback=callback_db, callback_init=callback_init_db, refresh_interval=30, bm=bm, limit=50)        
    except Exception as e:
        print(traceback.format_exc())
        bm.close()