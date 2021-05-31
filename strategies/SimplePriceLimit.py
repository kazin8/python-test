from pandas import DataFrame

from strategies.StrategyInterface import StrategyInterface


class SimplePriceLimit(StrategyInterface):
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        pass

    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        pass

    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        pass