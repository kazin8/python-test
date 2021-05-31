import json
import pprint
import traceback

import pandas as pd

from src.broker.saxo import SaxoBroker
from strategies.EmaRsiBBCombined import EmaRsiBBCombined

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
pd.set_option('mode.chained_assignment', None)

CONFIG_PATH = 'config.json'

config = json.loads(open(CONFIG_PATH, 'r').read())
STRATEGY_CONFIG = config.get('strategy')

brokers = {
    'saxo': SaxoBroker,
}

strategies = {
    'EmaRsiBBCombined': EmaRsiBBCombined,
    # 'SimplePriceLimit'
}

if __name__ == '__main__':
    broker = None
    try:
        broker = brokers[config.get('platform')](config)
    except KeyError:
        print('Unknown broker ' + config.get('platform') + '; Stop working')
        exit(1)

    strategy = None
    try:
        strategy = strategies[STRATEGY_CONFIG['type']]()
    except KeyError:
        print('Unknown strategy type ' + STRATEGY_CONFIG['type'] + '; Stop working')
        exit(1)

    instrument = broker.get_instrument(STRATEGY_CONFIG['ticker'])
    identifier = broker.get_instrument_id()

    # out = access.get('trade/v1/infoprices/list', Uics=identifier, AssetType='FxSpot', Amount=STRATEGY['amount'],
    #                  FieldGroups='DisplayAndFormat,Quote')

    # get candles
    out = broker.get_candles(identifier)

    # create dataframe
    df = pd.DataFrame(out['Data'], columns=['Time', 'OpenAsk', 'HighAsk', 'LowAsk', 'CloseAsk'])
    df.columns = ['time', 'open', 'high', 'low', 'close']

    # calculate strategy indicators & trends
    strategy.populate_indicators(dataframe=df, metadata=instrument)
    strategy.populate_buy_trend(dataframe=df, metadata=instrument)
    strategy.populate_sell_trend(dataframe=df, metadata=instrument)

    print(df)

    order = None
    # when last row (current candle) has buy/sell signal
    # script should place limit order
    last_row = df.tail(1)
    if last_row['buy'].bool():
        order = broker.place_limit_order(identifier, 'Buy', STRATEGY_CONFIG['amount'], STRATEGY_CONFIG['buyPrice'])
    elif last_row['sell'].bool():
        # should be refactor to use local db with open orders
        order = broker.place_limit_order(identifier, 'Sell', STRATEGY_CONFIG['amount'], STRATEGY_CONFIG['buyPrice'])

    print(order)
