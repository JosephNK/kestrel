import pandas as od
import ta
from ta.utils import dropna


class Metrics:

    @staticmethod
    def add_indicators(df):
        df = dropna(df)

        # 볼린저 밴드
        indicator_bb = ta.volatility.BollingerBands(
            close=df["close"], window=20, window_dev=2
        )
        df["bb_bbm"] = indicator_bb.bollinger_mavg()
        df["bb_bbh"] = indicator_bb.bollinger_hband()
        df["bb_bbl"] = indicator_bb.bollinger_lband()

        # RSI
        df["rsi"] = ta.momentum.RSIIndicator(close=df["close"], window=14).rsi()

        # MACD
        macd = ta.trend.MACD(close=df["close"])
        df["macd"] = macd.macd()
        df["macd_signal"] = macd.macd_signal()
        df["macd_diff"] = macd.macd_diff()

        # 이동평균선
        df["sma_20"] = ta.trend.SMAIndicator(
            close=df["close"], window=20
        ).sma_indicator()
        df["ema_12"] = ta.trend.EMAIndicator(
            close=df["close"], window=12
        ).ema_indicator()

        return df
