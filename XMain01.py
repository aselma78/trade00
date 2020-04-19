from TradingModel import TradingModel
from Binance import Binance
import multiprocessing
from Utils import cart_prod


def Main():
    processes = list()
    exchange = Binance()
    symbols = exchange.GetTradingSymbols()
    for symbol in symbols:
        abort=True
        coins = ["bnb", "btc", "eth", "xrp", "bch", "ltc"]
        for pair in cart_prod(coins):
            if pair[0] in symbol.lower() and pair[1] in symbol.lower():
                abort=False
        if abort:
            continue
        
        print("\n" + symbol + "\n==========")
        model = TradingModel(symbol)

        process = multiprocessing.Process(target=model.plotData)
        processes.append(process)
        process.start()

        key = None
        while key not in ['y','n','e','i','']:
            key = input("Continue?[Y/n]\nExit ['e']\nIpyhon ['i']").lower()
        if key == 'n':
            break
        if key == 'e':
            for process in processes:
                process.terminate()
            break
        if key == 'i':
            import ipdb;ipdb.set_trace() 
    for process in processes:
        process.join()


if __name__ == '__main__':
    Main()