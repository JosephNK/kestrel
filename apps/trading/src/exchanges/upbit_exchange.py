import os
import pyupbit

import pandas as pd


class UpbitExchange:
    access_key: str
    secret_key: str

    def __init__(self):
        self.access_key = os.environ.get("UPBIT_ACCESS_KEY")
        self.secret_key = os.environ.get("UPBIT_SECRET_KEY")

    def get30DayCandle(self):
        try:
            df: pd.DataFrame = pyupbit.get_ohlcv("KRW-BTC", count=30, interval="day")
            if df is None:
                return ""
            return df.to_json()
        except Exception as e:
            print("Exception occurred:", e)
            raise

    # def aaa(self):
    #     try:
    #         upbit = pyupbit.Upbit(self.access_key, self.secret_key)
    #         if df is None:
    #             return ""
    #         return df.to_json()
    #     except Exception as e:
    #         print("Exception occurred:", e)
    #         raise
