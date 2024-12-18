from dotenv import load_dotenv
import os
import openai
#import rich
#from openai import OpenAI

load_dotenv()

EMBEDDING_TEXT_MODEL = "text-embedding-3-small"
EMBEDDING_VEC_LEN = 1536

endpoint = os.environ["AZURE_OPENAI_ENDPOINT"]
api_key = os.environ["AZURE_OPENAI_API_KEY"]

_openai_client = openai.AzureOpenAI(
    azure_endpoint=endpoint,
    api_key=api_key,
    api_version=os.environ.get("AZURE_OPENAI_VERSION")
)

def get_text_embedding(text, deployment=EMBEDDING_TEXT_MODEL):
    text = text.replace("\n", " ")
    embeddings = _openai_client.embeddings.create(
        model=deployment,
        input=text
    )
    return embeddings.data[0].embedding

if __name__ == "__main__":
    embedding = get_text_embedding("hello")
    print(len(embedding))
