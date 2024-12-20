import os


class Logging:

    @staticmethod
    def logging_langSmith(project_name=None, set_enable=True):
        if set_enable:
            result = os.environ.get("LANGCHAIN_API_KEY")
            if result is None or result.strip() == "":
                print("LangChain API Key가 설정되지 않았습니다.")
                return
            os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
            os.environ["LANGCHAIN_TRACING_V2"] = "true"
            os.environ["LANGCHAIN_PROJECT"] = project_name
            print(f"LangSmith Enabled. (Project Name : {project_name})")
        else:
            os.environ["LANGCHAIN_TRACING_V2"] = "false"
            print("LangSmith Disabled.")
