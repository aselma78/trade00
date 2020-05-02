import sqlite3
from decimal import Decimal
from binance.client import Client
from binance.websockets import BinanceSocketManager

def adapt_decimal(d):
    return format(round(d, 14), 'f')

def convert_decimal(s):
    return Decimal(s)

class TradeDatabase:

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
        c.execute('''CREATE TABLE IF NOT EXISTS trades (
            id int primary key, 
            price real, 
            quantity real, 
            bid int,  
            ask int, 
            trtime int,
            evtime int,
            maker bool
            )''')

        conn.commit()

    def SaveTrade(self, trade):
        '''
        Adds a Trade to the Database
        '''
        conn = sqlite3.connect(self.name, detect_types=sqlite3.PARSE_DECLTYPES)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        values = (
            trade['t'], 
            trade['p'], 
            trade['q'],
            trade['b'], 
            trade['a'],
            trade['T'],
            trade['E'],
            trade['m'])
        c.execute('INSERT INTO trades VALUES (?, ?, ?, ?, ?, ?, ?, ?)', values)
        conn.commit()
    
    def GetTrade(self, id:str):
        ''' Gets Trade details from Database '''

        conn = sqlite3.connect(self.name, detect_types=sqlite3.PARSE_DECLTYPES)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute('SELECT * FROM trades WHERE id = ?', (id, ))
        details = c.fetchone()
        return details




def callback(trade):
    global tradedb
    #if trade['f'] != trade['l']:
    tradedb.SaveTrade(trade)
    print(trade)

if __name__ == '__main__':
    symbol = "BTCUSDT"
    tradedb = TradeDatabase(symbol + ".db")
    api_key=""
    api_secret = ""
    client = Client(api_key, api_secret)
    bm = BinanceSocketManager(client)
    try:        
        bm.start_trade_socket(symbol, callback)
        bm.start()
    except:
        bm.close()