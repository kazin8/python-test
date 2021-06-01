from src.logger import logger

import math
import uuid
from datetime import timedelta, datetime

import finnhub
import pandas as pd
from pandas import DataFrame

from src.broker.BrokerInterface import BrokerInterface
from alpaca_trade_api.rest import REST, TimeFrame

from src.storage.OrderMemoryStorage import shared_order_storage


class AlpacaBroker(BrokerInterface):
    def __init__(self, config):
        self.config = config
        self.session = None
        self.instrument = None

        self.create_session()

    def create_session(self):
        self.session = REST(self.config.get('app_key'), self.config.get('secret'), self.config.get('base_url'))

    def get_instrument(self, ticker):
        self.instrument = self.session.get_asset(ticker)

        return self.instrument

    def get_instrument_id(self):
        return self.instrument.symbol

    def get_dataframe(self, uic, timeframe=60, limit=1200) -> DataFrame:
        timedelta_days = 100

        d1 = datetime.today() - timedelta(days=round(timedelta_days))
        d2 = datetime.today()

        if 'paper' in self.config.get('base_url'):
            finnhub_client = finnhub.Client(api_key=self.config.get('finnhub_key'))

            candles = finnhub_client.stock_candles(uic, timeframe, int(d1.timestamp()), int(d2.timestamp()))

            df = DataFrame(candles, columns=['c', 'h', 'l', 'o', 't'])
            df.columns = ['open', 'high', 'low', 'close', 'time']
            df['time'] = pd.to_datetime(df['time'], unit='s')

            return df
        else:
            if timeframe < 60:
                timeframe = TimeFrame.Minute
            else:
                timeframe = TimeFrame.Hour

            candles = self.session.get_bars(uic, timeframe, d1.strftime('%Y-%m-%d'), d2.strftime('%Y-%m-%d'),
                                            limit=10000)

            df = DataFrame(candles._raw)
            df.columns = ['time', 'open', 'high', 'low', 'close', 'volume']

            return df

    def place_limit_order(self, uic, direction, amount, price, date=None, backtesting=False):
        if direction.lower() == 'buy':
            amount = amount / price
            amount = math.floor(amount)

        if amount < 1:
            logger.error('You can\'t trade 0 stocks')
            exit(1)

        order_id = None

        if not backtesting:
            order = self.session.submit_order(
                symbol=uic,
                side=direction.lower(),
                type='limit',
                limit_price=price,
                qty=amount,
                time_in_force='day'
            )

            order_id = order.id
        else:
            order_id = str(uuid.uuid4())

        order = {
            'id': order_id,
            'asset_id': uic,
            'direction': direction,
            'amount': amount,
            'price': price,
            'date': date
        }

        order = shared_order_storage.store_order(order)

        return order
