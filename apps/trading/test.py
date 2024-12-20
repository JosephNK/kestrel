from src.agents.kestrel_agent import KestrelAiModelAgent
from src.exchanges.upbit_exchange import UpbitExchange


def main():
    exchange = UpbitExchange()
    ai_agent = KestrelAiModelAgent()

    # 분석용 데이터 준비
    analysis_data = exchange.prepare_analysis_data()

    # AI 매매 결정
    answer = ai_agent.invoke(source_data=analysis_data)

    # 매매 실행
    exchange.trading(answer=answer)
