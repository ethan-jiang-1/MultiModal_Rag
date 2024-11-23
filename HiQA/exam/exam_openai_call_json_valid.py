from dotenv import load_dotenv # , find_dotenv
import sys
import rich
#import os
##import pandas as pd

sys.path.append("./")

from HiQA.utils.util_client_chat_completions import chat_completions_response_json

load_dotenv()

if __name__ == "__main__":
    ret = chat_completions_response_json("hi, response in json", model="gpt-4o-mini")
    rich.print(ret)

    ret = chat_completions_response_json("hi, response in json", model="gpt-4o", system_prompt="you are helpful assistant")
    rich.print(ret)
