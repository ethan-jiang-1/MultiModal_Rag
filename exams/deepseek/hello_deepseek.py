from openai import OpenAI
from dotenv import load_dotenv
import rich
import os

load_dotenv()

client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"), 
                base_url="https://api.deepseek.com")

response = client.chat.completions.create(
    #model="deepseek-chat",
    model="deepseek-coder",
    messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Hello, Tell me about yourself in json"},
    ],
    stream=False
)

rich.print(response)
rich.print(response.choices[0].message.content)