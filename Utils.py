

def cart_prod(coins):
    pairs = []
    coins2=[coin for coin in coins]
    for coin in coins:
        coins2.remove(coin)
        for coin2 in coins2:
            pairs.append((coin, coin2))
    return pairs

def process_message(msg):
    print("message type: {}".format(msg['e']))
    print(msg)
    # do something