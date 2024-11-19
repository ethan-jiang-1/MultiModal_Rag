import random
import chromadb
import os
import openai
import pandas as pd
import sys
from dotenv import load_dotenv
from chromadb.config import Settings

sys.path.append("./")

settings = Settings(allow_reset=True)
load_dotenv()

from HiQA.utils.openai_proxy import EMBEDDING_MODEL

endpoint = os.environ["AZURE_OPENAI_ENDPOINT"]
api_key = os.environ["AZURE_OPENAI_API_KEY"]
model = os.environ["EMBEDDING_MODLE"]

client = openai.AzureOpenAI(
    azure_endpoint=endpoint,
    api_key=api_key,
    api_version="2024-02-15-preview"
)
def get_text_embedding(text, deployment=EMBEDDING_MODEL):
    text = text.replace("\n", " ")
    embeddings = client.embeddings.create(
        model=deployment,
        input=text
    )
    return embeddings.data[0].embedding

def create_and_load_collection(client, base_name, dataset_path):
    # 生成唯一的集合名称
    collection_name = base_name + str(random.randint(0, 10000))

    # 创建集合
    collection = client.create_collection(name=collection_name)
    print(f'Collection {collection_name} created')

    # 加载数据
    embds = []
    docs = []
    metas = []
    ids = []
    id = 0

    for filename in os.listdir(dataset_path):
        if filename.endswith('.csv'):
            filepath = os.path.join(dataset_path, filename)
            df = pd.read_csv(filepath)
            for _, row in df.iterrows():
                section = row['section']
                n_tokens = row['n_tokens']
                embedding = [float(value) for value in row['embedding'][1:-1].split(',')]
                embds.append(embedding)
                docs.append(section)
                ids.append('id' + str(id))
                metas.append({'n_tokens': n_tokens, 'filename': filename, 'title': section.split('\n')[0]})
                id += 1
    collection.add(embeddings=embds, documents=docs, metadatas=metas, ids=ids)
    return collection

if __name__ == "__main__":
    from HiQA.utils.tokenizer import get_token_encoding
    encoding = get_token_encoding()

    chroma_client = chromadb.Client(settings=settings)
    chroma_client.reset()

    collections = {}
    collections['test'] = create_and_load_collection(chroma_client, "test", 'datasets/test/embeddings')
    question_embd = get_text_embedding('靠背STO间隙要求是什么？')
    results = collections['test'].query(question_embd)
    print(results)