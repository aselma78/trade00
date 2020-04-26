from binance.websockets import BinanceSocketManager
from binance.depthcache import DepthCacheManager
from binance.client import Client
import pandas as pd

def process_depth(depth_cache):
    import ipdb;ipdb.set_trace()
    df_asks = pd.DataFrame(depth_cache.get_asks())
    df_bids = pd.DataFrame(depth_cache.get_bids())

if __name__ == '__main__':

    api_key=""
    api_secret = ""
    client = Client(api_key, api_secret)
    symbol = "BTCUSDT"

    bm = BinanceSocketManager(client)
    dcm = DepthCacheManager(client, symbol, callback=process_depth, refresh_interval=30, bm=bm, limit=500)
