import json
import time

import schedule

import pandas as pd

from src.logger import logger
from src.broker.AlpacaBroker import AlpacaBroker
from src.broker.SaxoBroker import SaxoBroker
from src.storage.OrderMemoryStorage import shared_order_storage

from strategies.BollingerBandsStrategy import BollingerBandsStrategy
from strategies.Ema100Strategy import Ema100Strategy
from strategies.Ema200Strategy import Ema200Strategy
from strategies.RsiStrategy import RsiStrategy

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
pd.set_option('mode.chained_assignment', None)

CONFIG_PATH = 'config.json'

config = json.loads(open(CONFIG_PATH, 'r').read())
STRATEGY_CONFIG = config.get('strategy')

brokers = {
    'saxo': SaxoBroker,
    'alpaca': AlpacaBroker,
}

strategies = {
    'RsiStrategy': RsiStrategy,
    'Ema100Strategy': Ema100Strategy,
    'Ema200Strategy': Ema200Strategy,
    'BollingerBandsStrategy': BollingerBandsStrategy,
    # 'SimplePriceLimit'
}

logger.info('Enable broker ' + config.get('platform'))
logger.info('Enable strategy ' + STRATEGY_CONFIG['type'])
logger.info('Trade ticker ' + STRATEGY_CONFIG['ticker'])
logger.info('Stake amount ' + str(STRATEGY_CONFIG['stake_amount']))

broker = None
try:
    broker = brokers[config.get('platform')](config)
except KeyError:
    logger.error('Unknown broker ' + config.get('platform') + ', Stop working')
    exit(1)

strategy = None
try:
    strategy = strategies[STRATEGY_CONFIG['type']]()
except KeyError:
    logger.error('Unknown strategy type ' + STRATEGY_CONFIG['type'] + ', Stop working')
    exit(1)


def trader():
    instrument = broker.get_instrument(STRATEGY_CONFIG['ticker'])
    identifier = broker.get_instrument_id()

    # create dataframe
    df = broker.get_dataframe(identifier, strategy.timeframe)

    # calculate strategy indicators & trends
    strategy.populate_indicators(dataframe=df, metadata=instrument)
    strategy.populate_buy_trend(dataframe=df, metadata=instrument)
    strategy.populate_sell_trend(dataframe=df, metadata=instrument)

    if STRATEGY_CONFIG['backtesting']:
        for index, row in df.iterrows():
            if index == 0:
                continue

            prev_row = df.loc[[index - 1]]
            current_row = df.loc[[index]]

            price = current_row['close'].values[0]
            if current_row['buy'].bool() and not shared_order_storage.get_last_buy_order():
                broker.place_limit_order(identifier, 'Buy', STRATEGY_CONFIG['stake_amount'],
                                         price, current_row['time'].values[0], True)

            if current_row['sell'].bool() and shared_order_storage.get_last_buy_order():
                last_buy_order = shared_order_storage.get_last_buy_order()

                broker.place_limit_order(identifier, 'Sell', last_buy_order[0]['amount'],
                                         price, current_row['time'].values[0], True)

                shared_order_storage.move_orders_to_history()

        if shared_order_storage.get_last_buy_order():
            logger.info('There is one active trade')

    else:
        # when last row (current candle) has buy/sell signal
        # script should place limit order
        current_row = df.tail(1)

        logger.debug('Current candle:\n{}', current_row)

        price = current_row['close'].values[0]

        # order = broker.place_limit_order(identifier, 'Buy', STRATEGY_CONFIG['stake_amount'], price)

        if current_row['buy'].bool() and not shared_order_storage.get_last_buy_order():
            broker.place_limit_order(identifier, 'Buy', STRATEGY_CONFIG['stake_amount'], price)
        elif current_row['sell'].bool() and shared_order_storage.get_last_buy_order():
            last_buy_order = shared_order_storage.get_last_buy_order()

            broker.place_limit_order(identifier, 'Sell', last_buy_order[0]['amount'], price)

            shared_order_storage.move_orders_to_history()


if __name__ == '__main__':
    if not STRATEGY_CONFIG['backtesting']:
        logger.warning('Backtesting mode enabled')

        schedule.every(1).minutes.do(trader)

        while 1:
            schedule.run_pending()
            time.sleep(1)
    else:
        logger.warning('Live mode enabled')
        trader()
