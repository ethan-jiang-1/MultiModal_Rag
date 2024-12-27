from openai import OpenAI
import os
from dotenv import load_dotenv
import rich
import sys

sys.path.append("./")

load_dotenv()

from mrag_vdb.utils.util_logging import setup_logger_handlers

setup_logger_handlers()

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=os.environ.get("OPENROUTER_API_KEY"),
)

your_site_url = "https://notyet.com"
your_app_name = "not_yet"

completion = client.chat.completions.create(
  extra_headers={
    "HTTP-Referer":  your_site_url, # Optional, for including your app on openrouter.ai rankings.
    "X-Title": your_app_name, # Optional. Shows in rankings on openrouter.ai.
  },
  #model="openai/gpt-3.5-turbo",
  model="google/gemini-2.0-flash-thinking-exp:free",
  messages=[
    {
      "role": "user",
      "content": "what is your name?  do you happen to know what is the meaning of life?"
    }
  ]
)
rich.print(completion)
rich.print(completion.choices[0].message.content)