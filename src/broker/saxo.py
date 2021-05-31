from src.api.saxo import Session
from src.broker.BrokerInterface import BrokerInterface


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
        self.instrument = self.session.get('ref/v1/instruments', KeyWords=ticker, AssetTypes='FxSpot')
        return self.instrument

    def get_candles(self, uic, timeframe=60, limit=1200):
        return self.session.get('chart/v1/charts/', AssetType='FxSpot', Horizon=timeframe, Uic=uic, Count=limit)

    def place_limit_order(self, uic, direction, amount, price):
        return self.session.post('trade/v2/orders', post={
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
