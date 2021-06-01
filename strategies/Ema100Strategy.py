import talib.abstract as ta
from pandas import DataFrame
from src.logger import logger

from strategies.StrategyInterface import StrategyInterface
from vendor.qtpylib.indicators import bollinger_bands, crossed_below, crossed_above


class Ema100Strategy(StrategyInterface):
    timeframe = 15

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        if len(dataframe) < 100:
            logger.error('Historical data contains just ' + str(len(dataframe)) + ' periods, impossible to calculate EMA100, '
                                                                           'try to use RSI strategy instead')
            exit(1)

        dataframe['ema_50'] = ta.EMA(dataframe, timeperiod=50)
        dataframe['ema_100'] = ta.EMA(dataframe, timeperiod=100)

        return dataframe

    # detect buy reason
    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe['buy'] = False

        dataframe.loc[
            (
                crossed_above(dataframe['ema_100'], dataframe['ema_50'])
            ),
            'buy'
        ] = True

        return dataframe

    # detect sell reason
    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe['sell'] = False

        dataframe.loc[
            (
                crossed_above(dataframe['ema_50'], dataframe['ema_100'])
            ),
            'sell'
        ] = True

        return dataframe