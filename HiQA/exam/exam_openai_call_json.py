from dotenv import load_dotenv # , find_dotenv
import sys
#import os
##import pandas as pd

sys.path.append("./")

from HiQA.utils.util_client_chat_completions import chat_completions_response_json

load_dotenv()

if __name__ == "__main__":
    ret = chat_completions_response_json("hi, response in json", model="gpt-4o-mini")
    print(ret)

    ret = chat_completions_response_json("hi, response in json", model="gpt-4o", system_prompt="you are helpful assistant")
    print(ret)

    try:
        ret = chat_completions_response_json("hi")
        print(ret)
    except Exception as ex:
        print(ex)