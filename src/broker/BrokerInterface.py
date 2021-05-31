from abc import ABC, abstractmethod


class BrokerInterface:
    @abstractmethod
    def get_instrument(self, ticker: str):
        raise Exception('NotImplementedException')

    @abstractmethod
    def get_candles(self, uic: str, timeframe: int, limit: int):
        raise Exception('NotImplementedException')

    @abstractmethod
    def place_limit_order(self, uic: str, direction: str, amount: float, price: float):
        raise Exception('NotImplementedException')

    @abstractmethod
    def get_instrument_id(self):
        raise Exception('NotImplementedException')
