import talib.abstract as ta
from pandas import DataFrame

from strategies.StrategyInterface import StrategyInterface
from vendor.qtpylib.indicators import bollinger_bands, crossed_below, crossed_above


class EmaRsiBBCombined(StrategyInterface):
    buy_rsi_value = 30
    sell_rsi_value = 70

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # populate indicators
        dataframe['ema_50'] = ta.EMA(dataframe, timeperiod=50)
        dataframe['ema_100'] = ta.EMA(dataframe, timeperiod=100)
        dataframe['ema_200'] = ta.EMA(dataframe, timeperiod=200)

        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)

        # !!! as for me stds should be 2
        bb_20 = bollinger_bands(dataframe['close'], window=20, stds=20)
        dataframe['bb_20_lowerband'] = bb_20['lower']
        dataframe['bb_20_middleband'] = bb_20['mid']
        dataframe['bb_20_upperband'] = bb_20['upper']

        # debug
        dataframe['tmp_ema_buy'] = crossed_above(dataframe['ema_50'], dataframe['ema_200'])
        dataframe['tmp_ema_sell'] = crossed_below(dataframe['ema_200'], dataframe['ema_50'])

        return dataframe

    # detect buy reason
    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe['buy'] = False

        dataframe.loc[
            (
                (
                    dataframe['rsi'] < self.buy_rsi_value
                )
                &
                (
                    crossed_above(dataframe['ema_50'], dataframe['ema_200'])
                )
                # @todo implement bb conditions
            ),
            'buy'
        ] = True

        return dataframe

    # detect sell reason
    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe['sell'] = False

        dataframe.loc[
            (
                (
                    dataframe['rsi'] > self.sell_rsi_value
                )
                &
                (
                    crossed_below(dataframe['ema_200'], dataframe['ema_50'])
                )
                # @todo implement bb conditions
            ),
            'sell'
        ] = True

        return dataframe