import pandas as pd
import sqlite3
from binance.depthcache import DepthCache
import math
import numpy as np

def histogram(df, step):
    start = math.floor(min(df[0]))
    stop = math.ceil(max(df[0]))
    
    y = np.zeros(int((stop-start)/step))

    for i,price in enumerate(df[0]):
        if price >= start and price < stop:
            index =  math.floor((price -start)/step)
            y[index] += df[1][i]

    return y

conn = sqlite3.connect('./data/BTCUSDT_book.db')
query = "select * from obook order by time"

conn.row_factory = sqlite3.Row
c = conn.cursor()
c.execute(query)
rows = c.fetchall()

depth_cache = DepthCache(None)
time_set = set()
price_set =set()
for row in rows:
    time_set.add(row[0])
    price_set.add(row[2])

for row in rows:
    if row[1]:
        depth_cache.add_bid((row[2], row[3]))
    else:
        depth_cache.add_ask((row[2], row[3]))

df_asks = pd.DataFrame(depth_cache.get_asks())
df_bids = pd.DataFrame(depth_cache.get_bids())
# df_asks.to_csv("data.csv")

y_ask = histogram(df_asks, 0.25)
y_bid = histogram(df_bids, 0.25)





import ipdb; ipdb.set_trace()



