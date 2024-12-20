from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI


class KestrelAiModelAgent:
    llm: ChatOpenAI
    prompt: PromptTemplate

    def __init__(self):
        self.llm = ChatOpenAI(
            model_name="gpt-4o-mini",
            temperature=0.0,
        )

    # Write the extracted content in [FORMAT].
    def create_prompt(self):
        template = """
        You are a JSON data analysis expert.
        Analyze JSON data in [SOURCE] to extract product data.

        Product option values are extracted as values defined in [OPTIONS_KEYS], and the extracted values must be Grouped.

        Output Please tell me the code to create the result of [RESULT_STRUCTURE].
        And When writing code, please also add null value check logic to avoid errors.
        And when extracting [OPTION_STRUCTURE] data, all data in JSON Data must be extracted.
        However, it must be provided as a function in Python code, and the function name must be defined as "def extract_product_data(data):".
        Also, no additional explanation should be included.

        #SOURCE:
        {source}

        #OPTIONS_KEYS:
        goodsMaterial, optionCombinations, combinationOptions, standardCombinations

        #OPTION_STRUCTURE:
        [
            {{
                "option_group_name": String,
                "options": [
                    {{
                        "option_item_name": String,
                        "option_item_price": String,
                    }}
                    ...
                ]
            }}
            ...
        ]

        #RESULT_STRUCTURE:
        '''json
        {{
            "product_name": String,
            "product_brand": String,
            "product_original_price": String,
            "product_sale_price": String,
            "product_options": [OPTION_STRUCTURE]
            "product_images": Array,
        }}
        '''
        """

        # Output in [FORMAT] format.
        self.prompt = PromptTemplate.from_template(template)

    def invoke(self, source: str) -> str:
        self.create_prompt()
        chain = self.prompt | self.llm
        answer = chain.invoke({"source": source})
        content = answer.content
        return content

    def stream(self, source: str) -> list:
        self.create_prompt()
        chain = self.prompt | self.llm
        chunks = []
        for chunk in chain.stream({"source": source}):
            chunks.append(chunk.content)
            print(chunk.content, end="|", flush=True)
        return chunks
