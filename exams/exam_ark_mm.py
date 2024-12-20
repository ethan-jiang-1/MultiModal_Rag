import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get("ARK_API_KEY"),
    base_url="https://ark.cn-beijing.volces.com/api/v3",
)

# Image input:
response = client.chat.completions.create(
    model="ep-20241220100411-qb77p",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "这是哪里？"},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": "https://ark-project.tos-cn-beijing.ivolces.com/images/view.jpeg"
                    }
                },
            ],
        }
    ],
)

print(response.choices[0])