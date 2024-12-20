import json
import os
import pyupbit

import pandas as pd

from src.models.exception.exchange_exception import ExchangeException
from src.utils.metrics import Metrics


class UpbitExchange:
    """
    업비트 거래소와의 상호작용을 담당하는 클래스
    - 시장 데이터 조회
    - 투자 상태 모니터링
    - 주문 실행
    을 처리합니다.
    """

    ticker: str  # 거래 대상 티커 (예: "KRW-BTC")
    access_key: str  # 업비트 API 접근 키
    secret_key: str  # 업비트 API 비밀 키
    upbit: pyupbit.Upbit  # 업비트 API 클라이언트 인스턴스

    def __init__(self):
        """
        UpbitExchange 클래스 초기화
        환경 변수에서 API 키를 가져와 업비트 API 클라이언트를 생성합니다.
        """
        self.ticker = "KRW-BTC"  # 기본값으로 비트코인 설정
        self.access_key = os.environ.get("UPBIT_ACCESS_KEY")
        self.secret_key = os.environ.get("UPBIT_SECRET_KEY")
        self.upbit = pyupbit.Upbit(self.access_key, self.secret_key)

    def prepare_analysis_data(self) -> str:
        """
        투자 분석에 필요한 모든 데이터를 수집하여 JSON 형태의 문자열로 반환하는 함수

        Returns:
            str: JSON 형식의 데이터 문자열
                - investment_status: 현재 투자 상태 정보 (잔고, 수익률 등)
                - candle_data: 30일간의 일봉 데이터 (OHLCV)
                - hour_candle_data: 24시간의 시간봉 데이터 (OHLCV)
                - orderbook_status: 현재 호가 데이터 (매수/매도 주문)
        """
        try:
            # 각종 데이터 수집
            investment_status = self.get_current_investment_status()
            candle_data = self.get_30_day_candle()
            hour_candle_data = self.get_24_hour_candle()
            orderbook_status = self.get_orderbook_status()

            # 데이터 통합 및 JSON 형식으로 변환
            analysis_data = {
                "investment_status": investment_status,
                "candle_data": candle_data,
                "hour_candle_data": hour_candle_data,
                "orderbook_status": orderbook_status,
            }

            return json.dumps(analysis_data, indent=2)

        except Exception as e:
            print("Exception in prepareAnalysisData:", e)
            raise

    def get_current_investment_status(self):
        try:
            # 투자 상태를 저장할 딕셔너리
            status = {
                # 코인과 원화의 잔고 정보를 저장할 딕셔너리
                "balance": {},
                # 현재 코인의 시장 가격 (원화)
                # 예: BTC가 5,000만원일 경우 -> 50000000
                "current_price": 0,
                # 투자한 총 원화 금액 (매수 평균가 * 보유 수량)
                # 예: 4,800만원에 1 BTC를 매수했다면 -> 48000000
                "invested_amount": 0,
                # 보유한 코인의 현재 가치 (현재가 * 보유 수량)
                # 예: 현재가 5,000만원이고 1 BTC를 보유 중이라면 -> 50000000
                "current_value": 0,
                # 현재 평가 손익 (current_value - invested_amount)
                # 예: 4,800만원에 매수하여 5,000만원이 된 경우 -> 2000000 (200만원 이익)
                # 예: 5,000만원에 매수하여 4,800만원이 된 경우 -> -2000000 (200만원 손실)
                "profit_loss": 0,
                # 현재 수익률 (%) ((current_value / invested_amount - 1) * 100)
                # 예: 4,800만원 매수 후 5,000만원이 된 경우 -> 4.17 (4.17% 이익)
                # 예: 5,000만원 매수 후 4,800만원이 된 경우 -> -4.00 (4% 손실)
                "profit_loss_percent": 0,
            }

            # 현재가 조회
            current_price = pyupbit.get_current_price(self.ticker)
            status["current_price"] = current_price

            # 보유 잔고 조회
            balances = self.upbit.get_balances()
            for balance in balances:
                currency = balance["currency"]
                # ticker에서 currency 부분 추출 (예: "KRW-BTC"에서 "BTC")
                ticker_currency = self.ticker.split("-")[1]

                # 해당 ticker의 currency와 KRW만 처리
                if currency in [ticker_currency, "KRW"]:
                    status["balance"][currency] = {
                        "amount": float(balance["balance"]),  # 보유 수량
                        "avg_buy_price": float(balance["avg_buy_price"]),  # 매수 평균가
                        "locked": float(balance["locked"]),  # 거래가 예약된 금액
                    }

            # 코인 보유중인 경우 수익률 계산
            ticker_currency = self.ticker.split("-")[1]  # "KRW-BTC"에서 "BTC" 추출
            if ticker_currency in status["balance"]:
                coin_balance = status["balance"][ticker_currency]

                # 투자 금액 계산 (매수 평균가 * 보유 수량)
                invested_amount = coin_balance["amount"] * coin_balance["avg_buy_price"]
                # 현재 가치 계산 (현재가 * 보유 수량)
                current_value = coin_balance["amount"] * current_price

                status["invested_amount"] = invested_amount
                status["current_value"] = current_value
                # 평가 손익 계산 (현재 가치 - 투자 금액)
                status["profit_loss"] = current_value - invested_amount
                # 수익률 계산 ((현재 가치 / 투자 금액 - 1) * 100)
                status["profit_loss_percent"] = (
                    ((current_value / invested_amount) - 1) * 100
                    if invested_amount > 0
                    else 0
                )

            return status
        except Exception as e:
            print("Exception in get_current_investment_status:", e)
            raise ExchangeException(f"Exception in Get Current Investment Status : {e}")

    def get_orderbook_status(self):
        """
        현재 시장의 호가창(orderbook) 데이터를 조회하고 분석하는 함수
        매수/매도 호가의 물량과 가격을 단계별로 조회하여 시장 동향을 파악할 수 있음

        Returns:
            dict: 호가 데이터 분석 결과
                - timestamp: 호가 데이터 생성 시간
                - total_ask_size: 총 매도 주문량
                - total_bid_size: 총 매수 주문량
                - ask_bid_ratio: 매도/매수 물량 비율
                - orderbook_units: 호가 단계별 상세 데이터
        """
        try:
            # 업비트 API를 통해 호가 데이터 조회
            orderbook_data = pyupbit.get_orderbook(self.ticker)
            if not orderbook_data:
                return None

            # orderbook 데이터 타입 체크 및 처리
            if isinstance(orderbook_data, list):
                orderbook = orderbook_data[0]  # 리스트인 경우 첫 번째 요소 사용
            elif isinstance(orderbook_data, dict):
                orderbook = orderbook_data  # 딕셔너리인 경우 그대로 사용
            else:
                raise ExchangeException(
                    f"Unexpected orderbook data type: {type(orderbook_data)}"
                )

            # 필수 키 존재 여부 확인
            required_keys = [
                "timestamp",
                "total_ask_size",
                "total_bid_size",
                "orderbook_units",
            ]
            if not all(key in orderbook for key in required_keys):
                raise ExchangeException("Missing required keys in orderbook data")

            # 호가 데이터 분석 결과를 저장할 딕셔너리
            status = {
                # 호가 데이터의 생성 시간 (timestamp)
                # 밀리초(ms) 단위로 반환됨
                # 예: 1632145728571 -> 2021-09-20 15:42:08.571
                "timestamp": orderbook["timestamp"],
                # 매도 호가의 총 물량 (ask: 매도 주문)
                # 예: 2.5 -> 시장에 매도 주문으로 걸려있는 BTC의 총량이 2.5 BTC
                "total_ask_size": orderbook["total_ask_size"],
                # 매수 호가의 총 물량 (bid: 매수 주문)
                # 예: 1.8 -> 시장에 매수 주문으로 걸려있는 BTC의 총량이 1.8 BTC
                "total_bid_size": orderbook["total_bid_size"],
                # 매도/매수 물량 비율
                # 1보다 크면 매도 물량이 많다는 의미 (매도 우세)
                # 1보다 작으면 매수 물량이 많다는 의미 (매수 우세)
                # 예: 1.5 -> 매도 물량이 매수 물량보다 50% 많음
                "ask_bid_ratio": (
                    orderbook["total_ask_size"] / orderbook["total_bid_size"]
                    if orderbook["total_bid_size"] > 0
                    else 0
                ),
                # 각 호가 단계별 상세 데이터를 저장할 리스트
                "orderbook_units": [],
            }

            # 호가 단계별 데이터 분석 (기본적으로 최대 15단계)
            # orderbook_units는 가격이 유리한 순서대로 정렬되어 있음
            for unit in orderbook["orderbook_units"]:
                # 필요한 키가 모두 있는지 확인
                if not all(
                    key in unit
                    for key in ["ask_price", "bid_price", "ask_size", "bid_size"]
                ):
                    continue  # 필요한 데이터가 없는 경우 건너뜀

                status["orderbook_units"].append(
                    {
                        # 매도 호가 (매도 주문이 걸려있는 가격)
                        # 예: 50000000 -> 5천만원에 매도 주문
                        "ask_price": unit["ask_price"],
                        # 매수 호가 (매수 주문이 걸려있는 가격)
                        # 예: 49990000 -> 4,999만원에 매수 주문
                        "bid_price": unit["bid_price"],
                        # 해당 매도 호가의 코인 수량
                        # 예: 0.1 -> 해당 가격에 0.1 BTC만큼 매도 주문이 있음
                        "ask_size": unit["ask_size"],
                        # 해당 매수 호가의 코인 수량
                        # 예: 0.15 -> 해당 가격에 0.15 BTC만큼 매수 주문이 있음
                        "bid_size": unit["bid_size"],
                    }
                )

            return status
        except Exception as e:
            print("Exception in get_orderbook_status:", e)
            raise ExchangeException(f"Exception in Get Orderbook Status : {e}")

    def get_30_day_candle(self):
        """
        최근 30일간의 일봉 데이터를 조회합니다.

        Returns:
            str: 일봉 데이터의 JSON 문자열
                포함 정보:
                - open: 시가
                - high: 고가
                - low: 저가
                - close: 종가
                - volume: 거래량
                - value: 거래금액
        """
        try:
            df: pd.DataFrame = pyupbit.get_ohlcv(self.ticker, count=30, interval="day")
            if df is None:
                return ""
            df = Metrics.add_indicators(df)
            return df.to_json()
        except Exception as e:
            print("Exception in get_30_day_candle:", e)
            raise ExchangeException(f"Exception in Get 30 Day Candle : {e}")

    def get_24_hour_candle(self):
        """
        최근 24시간의 시간봉 데이터를 조회합니다.

        Returns:
            str: 시간봉 데이터의 JSON 문자열
                포함 정보:
                - open: 시가
                - high: 고가
                - low: 저가
                - close: 종가
                - volume: 거래량
                - value: 거래금액
        """
        try:
            df: pd.DataFrame = pyupbit.get_ohlcv(
                self.ticker, count=24, interval="minute60"
            )
            if df is None:
                return ""
            df = Metrics.add_indicators(df)
            return df.to_json()
        except Exception as e:
            print("Exception in get_24_hour_candle:", e)
            raise ExchangeException(f"Exception in Get 24 Hour Candle : {e}")

    def trading(self, answer: str):
        """
        AI 모델의 결정에 따라 실제 매매를 실행합니다.

        Args:
            answer (dict): AI 모델의 매매 결정 정보
                - decision: 'buy', 'sell', 또는 'hold'
                - reason: 매매 결정의 이유

        주의사항:
        - 최소 거래금액은 5000원
        - 매수 시 수수료 0.05% 고려 (0.9995)
        """
        try:
            # if df is None:
            #     return ""
            # return df.to_json()
            decision = answer["decision"].lower()
            reason = answer["reason"]
            if decision == "buy":
                # Buy
                print("Buy", reason)
                my_krw = self.upbit.get_balance("KRW")
                if my_krw * 0.9995 > 5000:
                    print("Buy Order Executed")
                    # buy_result = self.upbit.buy_market_order(
                    #     ticker=self.ticker, price=my_krw * 0.9995
                    # )
                    # if buy_result is None:
                    #     raise ExchangeException("An error with the buy order")
                else:
                    print("Buy Faild Below 5000 Won")
            elif decision == "sell":
                # Sell
                print("Sell", reason)
                my_coin = self.upbit.get_balance(self.ticker)
                current_price = pyupbit.get_orderbook(ticker="KRW-BTC")[
                    "orderbook_units"
                ][0]["ask_price"]
                if my_coin * current_price > 5000:
                    print("Sell Order Executed")
                    # sell_result = self.upbit.sell_market_order(
                    #     ticker=self.ticker, volume=my_coin
                    # )
                    # if sell_result is None:
                    #     raise ExchangeException("An error with the sell order")
                else:
                    print("Sell Faild Below 5000 Won")
            elif decision == "hold":
                # Hold
                print("Hold", reason)
            return ""
        except Exception as e:
            print("Exception occurred:", e)
            raise
