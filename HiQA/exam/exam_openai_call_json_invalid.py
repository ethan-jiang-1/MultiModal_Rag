from dotenv import load_dotenv # , find_dotenv
import sys
import rich
#import os
##import pandas as pd

sys.path.append("./")

from HiQA.utils.util_client_chat_completions import chat_completions_response_json

load_dotenv()

if __name__ == "__main__":
    try:
        ret = chat_completions_response_json("hi", model="gpt-4o-mini")
        rich.print(ret)
    except Exception as ex:
        rich.print(ex)

    try:
        ret = chat_completions_response_json("hi", model="gpt-4o")
        rich.print(ret)
    except Exception as ex:
        rich.print(ex)