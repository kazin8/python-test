import json
import pprint
import traceback

import pandas as pd
from strategies.EmaRsiBBCombined import EmaRsiBBCombined

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
pd.set_option('mode.chained_assignment', None)

from api.saxo import Session
import sched, time

CONFIG_PATH = 'config.json'

config = json.loads(open(CONFIG_PATH, 'r').read())
APP_KEY = config.get('app_key')
AUTH_ENDPOINT = config.get('auth_endpoint')
TOKEN_ENDPOINT = config.get('token_endpoint')
SECRET = config.get('secret')
STRATEGY = config.get('strategy')


# s = sched.scheduler(time.time, time.sleep)

def get_instrument(ticker):
    return access.get('ref/v1/instruments', KeyWords=ticker, AssetTypes='FxSpot')


def get_candles(uic, timeframe=60, limit=1200):
    return access.get('chart/v1/charts/', AssetType='FxSpot', Horizon=timeframe, Uic=uic, Count=limit)


def place_limit_order(uic, direction, amount, price):
    return access.post('trade/v2/orders', post={
        'Uic': uic,
        'BuySell': direction,
        'AssetType': 'FxSpot',
        'Amount': amount,
        'OrderPrice': price,
        'OrderType': 'Limit',
        'OrderRelation': 'StandAlone',
        'ManualOrder': 'true',
        'OrderDuration': {
            'DurationType': 'GoodTillCancel'
        }
    })


# def get_orders(sc):
#     orders = access.get('port/v1/orders/me',
#                         FieldGroups='DisplayAndFormat')
# s.enter(5, 1, get_orders, (sc,))


if __name__ == '__main__':
    # a = 1
    access = Session(APP_KEY, AUTH_ENDPOINT, TOKEN_ENDPOINT, SECRET)
    print('[Authorised SAXO]')

    try:
        instrument = get_instrument(STRATEGY['ticker'])

        identifier = instrument['Data'][0]['Identifier']

        # out = access.get('trade/v1/infoprices/list', Uics=identifier, AssetType='FxSpot', Amount=STRATEGY['amount'],
        #                  FieldGroups='DisplayAndFormat,Quote')

        # get candles
        out = get_candles(identifier)

        # create dataframe
        df = pd.DataFrame(out['Data'], columns=['Time', 'OpenAsk', 'HighAsk', 'LowAsk', 'CloseAsk'])
        df.columns = ['time', 'open', 'high', 'low', 'close']

        # resolve strategy
        strategy = EmaRsiBBCombined()
        strategy.populate_indicators(dataframe=df, metadata=instrument)
        strategy.populate_buy_trend(dataframe=df, metadata=instrument)
        strategy.populate_sell_trend(dataframe=df, metadata=instrument)

        # print(df)

        # when last row (current candle) has buy/sell signal
        # script should place limit order
        last_row = df.tail(1)
        if last_row['buy'].bool():
            pass # place buy order
        elif df.tail(1)['sell'].bool():
            pass # place sell order

        if STRATEGY['type'] == 'priceLimit':
            # s.enter(5, 1, getOrders, (s,))
            # s.run()

            order = place_limit_order(identifier, 'Buy', STRATEGY['amount'], STRATEGY['buyPrice'])

            print(order)

    except:
        print('\n** EXCEPTION **\n', traceback.format_exc(), '\n')