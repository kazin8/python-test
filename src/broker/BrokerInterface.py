from abc import ABC, abstractmethod

from pandas import DataFrame


class BrokerInterface:
    @abstractmethod
    def get_instrument(self, ticker: str):
        raise NotImplementedError

    @abstractmethod
    def get_dataframe(self, uic, timeframe=60, limit=1000) -> DataFrame:
        raise NotImplementedError

    @abstractmethod
    def place_limit_order(self, uic: str, direction: str, amount: float, price: float):
        raise NotImplementedError

    @abstractmethod
    def get_instrument_id(self):
        raise NotImplementedError
