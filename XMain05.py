from Binance import Binance
import time
from Utils import cart_prod
import requests
import json

exchange = Binance("credentials.txt") 
symbols = exchange.GetTradingSymbols()

alist=[]
for symbol in symbols:
    coins = ["bnb", "btc", "eth", "xrp", "bch", "ltc"]
    for pair in cart_prod(coins):
        if pair[0] in symbol.lower() and pair[1] in symbol.lower():
            alist.append(symbol)

print(alist)

url='https://api.binance.com/api/v3/ticker/price'

print("(+) BTC -> ETH -> LTC ->BTC")
print("(-) BTC -> LTC -> ETH ->BTC")

while True:
    response = requests.get(url)
    data = json.loads(response.text)

    data_dict={}
    for line in data:
        if line['symbol'] in alist:
            data_dict[line['symbol']]=line['price']
            #print(f"{line['symbol']}:{line['price']}")

    ETHBTC=float(data_dict["ETHBTC"])
    LTCETH=float(data_dict["LTCETH"])
    LTCBTC=float(data_dict["LTCBTC"])


    profit = ((1/ETHBTC)*(1/LTCETH)*LTCBTC -1)
    profit_dolars = ((1/ETHBTC)*(1/LTCETH)*LTCBTC -1)*6000
    print(f"{profit*100}\t[%]\t\t\t{profit_dolars}\t[$/1BTC]")
    time.sleep(1)


