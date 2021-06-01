import talib.abstract as ta
from pandas import DataFrame

from strategies.StrategyInterface import StrategyInterface
from vendor.qtpylib.indicators import bollinger_bands, crossed_below, crossed_above


class RsiStrategy(StrategyInterface):
    timeframe = 30

    buy_rsi_value = 30
    sell_rsi_value = 70

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)

        return dataframe

    # detect buy reason
    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe['buy'] = False

        dataframe.loc[
            (
                dataframe['rsi'] < self.buy_rsi_value
            ),
            'buy'
        ] = True

        return dataframe

    # detect sell reason
    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe['sell'] = False

        dataframe.loc[
            (
                dataframe['rsi'] > self.sell_rsi_value
            ),
            'sell'
        ] = True

        return dataframe