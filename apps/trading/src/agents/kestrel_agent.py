from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

# from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI


class KestrelAiModelAgent:
    llm: ChatOpenAI
    prompt: ChatPromptTemplate
    parser: JsonOutputParser

    def __init__(self):
        self.llm = ChatOpenAI(
            model_name="gpt-4o",
            temperature=0.2,  # 일관성을 위해 temperature 설정
        )

        self.parser = JsonOutputParser()

    def create_prompt(self):
        system_template = """
        You are a Bitcoin trading expert. Analyze market data and make trading decisions based on the following information:

        MARKET DATA:
        1. Investment Status
        - Current balance, position, and P/L
        - Minimum trade: 5000 KRW
        - Risk limit: 50% of available funds

        2. Technical Analysis
        - 30-day daily candles
        - 24-hour hourly candles
        - Key indicators: RSI, MACD
        - Support/resistance levels

        3. Market Depth
        - Current orderbook (15 levels)
        - Ask/bid volume ratio
        - Price pressure analysis

        TRADING RULES:
        1. Buy when:
        - Uptrend with volume support
        - Strong bid pressure
        - Price near support level
        - RSI below 30

        2. Sell when:
        - Take profit at +5%
        - Stop loss at -3%
        - Heavy selling pressure
        - RSI above 70

        3. Hold when:
        - Sideways movement
        - Balanced orderbook
        - No clear signals
        - P/L within -2% to +4%

        Response Example:
        {{\"decision\": \"buy\", \"reason\": \"Strong buying pressure in orderbook with 30-day upward trend\"}}
        {{\"decision\": \"sell\", \"reason\": \"High ask/bid ratio indicating selling pressure, take profit at 5%\"}}
        {{\"decision\": \"hold\", \"reason\": \"Market in consolidation phase, wait for clear direction\"}}
        """

        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_template),
                ("human", "{source}"),
            ]
        )

    def invoke(self, source_data: str) -> dict:
        """
        AI 모델에 데이터를 전달하고 매매 결정을 받아오는 함수

        Args:
            source_data (str): JSON 형식의 분석 데이터 문자열 (캔들 데이터, 투자 상태, 호가 데이터 포함)

        Returns:
            dict: 매매 결정 딕셔너리
                - decision: 'buy', 'sell', 또는 'hold'
                - reason: 결정에 대한 이유
        """

        self.create_prompt()
        self.prompt = self.prompt.partial(
            format_instructions=self.parser.get_format_instructions()
        )
        chain = self.prompt | self.llm | self.parser
        answer = chain.invoke({"source": source_data})
        print("answer", answer)
        return answer
