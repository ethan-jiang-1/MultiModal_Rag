from openai import AzureOpenAI
from dotenv import load_dotenv
import sys
import os
import json_repair

if "./" not in sys.path:
    sys.path.append("./")
load_dotenv()

def get_gpt_messages(system_prompt, user_prompt):
    messages=[
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": user_prompt
        },
    ]
    return messages

def get_gpt_client():
    client = AzureOpenAI(api_key=os.getenv("OPENAI_API_KEY"),
                         azure_endpoint=os.getenv("OPENAI_BASE_URL"),
                         api_version="2024-02-15-preview")
    return client


def jsons_load_repair(content):
    resp = json_repair.repair_json(content, 
                                   ensure_ascii=True, 
                                   return_objects=True)
    return resp
