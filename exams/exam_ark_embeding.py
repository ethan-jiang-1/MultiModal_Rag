

import os
from openai import OpenAI
from dotenv import load_dotenv
#import rich

load_dotenv()

# gets API Key from environment variable OPENAI_API_KEY
client = OpenAI(
    api_key=os.environ.get("ARK_API_KEY"),
    base_url="https://ark.cn-beijing.volces.com/api/v3",
)

print("----- embeddings request -----")
resp = client.embeddings.create(
    model="ep-20241220102000-c4f7m",
    input=["花椰菜又称菜花、花菜，是一种常见的蔬菜。"],
    encoding_format="float"
)
print(resp)

embededing = resp.data[0].embedding
print(len(embededing))