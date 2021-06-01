from src.logger import logger

import math
import uuid
from datetime import datetime

from pandas import DataFrame

from src.api.saxo import Session
from src.broker.BrokerInterface import BrokerInterface
from src.storage.OrderMemoryStorage import shared_order_storage


class SaxoBroker(BrokerInterface):
    def __init__(self, config):
        self.config = config
        self.instrument = None
        self.session = None

        self.create_session()

    def create_session(self):
        self.session = Session(self.config.get('app_key'), self.config.get('auth_endpoint'),
                               self.config.get('token_endpoint'), self.config.get('secret'))

    def get_instrument_id(self):
        return self.instrument['Data'][0]['Identifier']

    def get_instrument(self, ticker):
        self.instrument = self.session.get('ref/v1/instruments', KeyWords=ticker,
                                           AssetTypes=self.config.get('asset_type'))
        return self.instrument

    def get_dataframe(self, uic, timeframe=60, limit=1000) -> DataFrame:
        candles = self.session.get('chart/v1/charts/', AssetType=self.config.get('asset_type'),
                                   Horizon=timeframe, Uic=uic, Count=limit)

        df = DataFrame(candles['Data'], columns=['Time', 'OpenBid', 'HighBid', 'LowBid', 'CloseBid'])
        df.columns = ['time', 'open', 'high', 'low', 'close']

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
            order = self.session.post('trade/v2/orders', post={
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

            try:
                order_id = order['OrderId']
                date = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
            except KeyError:
                logger.error('Broker Error: {}', order['ErrorInfo']['Message'])
                exit(1)
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
