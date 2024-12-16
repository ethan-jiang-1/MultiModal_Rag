import os
import openai
from dotenv import load_dotenv
import json
import sys
load_dotenv()

sys.path.append("./")

from HiQA.utils.openai_proxy import EMBEDDING_MODEL
endpoint = os.environ["AZURE_OPENAI_ENDPOINT"]
api_key = os.environ["AZURE_OPENAI_API_KEY"]

client = openai.AzureOpenAI(
    azure_endpoint=endpoint,
    api_key=api_key,
    api_version=os.environ["AZURE_OPENAI_VERSION"]
)

def get_completion(prompt, model="gpt-4o"):
    messages = [{"role": "user", "content": prompt}]
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0,
        timeout=120,
    )
    return response.choices[0].message.content


def get_text_embedding(text, deployment=EMBEDDING_MODEL):
    embeddings = client.embeddings.create(
    model=deployment,
    input=text
)
    return embeddings.data[0].embedding