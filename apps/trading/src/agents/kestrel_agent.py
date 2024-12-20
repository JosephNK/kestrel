from langchain_core.prompts import (
    PromptTemplate,
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain_core.output_parsers import JsonOutputParser
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI


class KestrelAiModelAgent:
    llm: ChatOpenAI
    prompt: ChatPromptTemplate
    parser: JsonOutputParser

    def __init__(self):
        self.llm = ChatOpenAI(
            model_name="gpt-4o",
            # temperature=0.0,
        )

        self.parser = JsonOutputParser()

    def create_prompt(self):
        system_template = """
        You are an expert in cryptocurrency coin investing. Tell me whether to buy, sell, or hold at the moment based on the difference data provided.

        Response Example:
        {{\"decision\": \"buy\", \"reason\": \"some technical reason\"}}
        {{\"decision\": \"sell\", \"reason\": \"some technical reason\"}}
        {{\"decision\": \"hold\", \"reason\": \"some technical reason\"}}
        """

        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_template),
                ("human", "{source}"),
            ]
        )

    def invoke(self, source: str) -> dict:
        self.create_prompt()
        self.prompt = self.prompt.partial(
            format_instructions=self.parser.get_format_instructions()
        )
        chain = self.prompt | self.llm | self.parser
        answer = chain.invoke({"source": source})
        print("answer", answer)
        return answer
