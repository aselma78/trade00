import pandas as pd
import sqlite3
from binance.depthcache import DepthCache
import math
import numpy as np

# ID = 0
# PRICE =1
# QUANTITY =2
# BID = 3
# ASK =4
# TRTIME = 5
# EVTIME = 6
# MAKER = 7

conn = sqlite3.connect('./DATA/BTCUSDT_trade.db')
query = "select * from trades order by trtime"

# conn.row_factory = sqlite3.Row
# c = conn.cursor()
# c.execute(query)
# rows = c.fetchall()

df = pd.read_sql_query(query, conn)

print(type(df['price']))

# for row in rows:
#     print(row[TRTIME])



