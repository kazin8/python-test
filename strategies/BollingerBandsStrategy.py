import pandas as pd
import talib.abstract as ta
from pandas import DataFrame

from strategies.StrategyInterface import StrategyInterface
from vendor.qtpylib.indicators import bollinger_bands, crossed_below, crossed_above


class BollingerBandsStrategy(StrategyInterface):
    timeframe = 5

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:

        bb = bollinger_bands(dataframe['close'], window=20, stds=2)

        dataframe['bb_lower'] = bb['lower']
        dataframe['bb_upper'] = bb['upper']

        return dataframe

    # detect buy reason
    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe['buy'] = False

        dataframe.loc[
            (
                dataframe['close'] < dataframe['bb_lower']
            ),
            'buy'
        ] = True

        return dataframe

    # detect sell reason
    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe['sell'] = False

        dataframe.loc[
            (
                (dataframe['close'] > dataframe['bb_upper'])
                # &
                # (dataframe['close'].shift(2) > dataframe['bb_upper'].shift(2))
            ),
            'sell'
        ] = True

        return dataframe