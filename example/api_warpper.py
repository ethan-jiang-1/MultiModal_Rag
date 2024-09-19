import os
import openai
from dotenv import load_dotenv
import json
load_dotenv()


endpoint = os.environ["AZURE_OPENAI_ENDPOINT"]
api_key = os.environ["AZURE_OPENAI_API_KEY"]

client = openai.AzureOpenAI(
    azure_endpoint=endpoint,
    api_key=api_key,
    api_version="2024-02-15-preview"
)

def get_completion(prompt, model="gpt-4o"):
    messages = [{"role": "user", "content": prompt}]
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0,
    )
    return response.choices[0].message.content


def get_embedding(text, deployment='text-embedding-3-small'):
    embeddings = client.embeddings.create(
    model=deployment,
    input=text
)
    return embeddings.data[0].embedding