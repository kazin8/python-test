import talib.abstract as ta
from pandas import DataFrame
from src.logger import logger

from strategies.StrategyInterface import StrategyInterface
from vendor.qtpylib.indicators import bollinger_bands, crossed_below, crossed_above


class Ema200Strategy(StrategyInterface):
    timeframe = 60

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        if len(dataframe) < 200:
            logger.error('Historical data contains just ' + str(len(dataframe)) + ' periods, impossible to calculate EMA200, '
                                                                           'try to use EMA100 strategy instead')
            exit(1)

        dataframe['ema_50'] = ta.EMA(dataframe, timeperiod=50)
        dataframe['ema_200'] = ta.EMA(dataframe, timeperiod=200)

        return dataframe

    # detect buy reason
    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe['buy'] = False

        dataframe.loc[
            (
                crossed_above(dataframe['ema_200'], dataframe['ema_50'])
            ),
            'buy'
        ] = True

        return dataframe

    # detect sell reason
    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe['sell'] = False

        dataframe.loc[
            (
                crossed_above(dataframe['ema_50'], dataframe['ema_200'])
            ),
            'sell'
        ] = True

        return dataframe