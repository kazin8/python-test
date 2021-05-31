from abc import ABC, abstractmethod

from pandas import DataFrame


class StrategyInterface:
    @abstractmethod
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        return dataframe

    @abstractmethod
    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        return dataframe

    @abstractmethod
    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        return dataframe