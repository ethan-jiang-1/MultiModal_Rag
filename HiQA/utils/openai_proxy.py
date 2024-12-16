from dotenv import load_dotenv
import os
import openai
#from openai import OpenAI

load_dotenv()

EMBEDDING_MODEL = "text-embedding-3-small"

endpoint = os.environ["AZURE_OPENAI_ENDPOINT"]
api_key = os.environ["AZURE_OPENAI_API_KEY"]

client = openai.AzureOpenAI(
    azure_endpoint=endpoint,
    api_key=api_key,
    api_version=os.environ.get("AZURE_OPENAI_VERSION")
)

def send_messages(user_input, knowledge, role=None, model="gpt-4o"):
    if not role:
        role = """Role: You are an intelligent customer service agent, please answer questions from a professional perspective.
Note:
  1. When users ask questions, I will provide you with some information, please refer to the information and your own knowledge to answer.
  2. Your answers should be accurate and reasonable, but not summary.
  3. If your own knowledge and given information can not answer the user's question, do not answer, and tell the user "Sorry, your question is beyond my knowledge, I can not answer." .
  4. If some data is missing, try to calculate through the data first, show the calculation process first, and then answer after the calculation step is complete.
  5. If tables are identified in the data, or you need to output a table, please strictly follow markdown's format to output the table.".
  6. Output language should be English.
"""

    model = model
    content = f"Answer this question by the given content: {user_input}\n ***Given Content Below***\n{knowledge}"

    print(content)
    if model == "gpt-3.5-turbo-1106":
        # reduce msg length to 16k token
        content = content[:14000]

    msgs = [{"role": "system", "content": role}, {"role": "user", "content": content}]

    result = client.chat.completions.create(
        model=model,
        # model='gpt-4-32k',
        # model='gpt-4-1106-preview',
        # max_tokens=4000,
        messages=msgs,
        stream=False,
        timeout=120
    )

    return result.choices[0].message.content

def get_text_embedding(text, deployment=EMBEDDING_MODEL):
    text = text.replace("\n", " ")
    embeddings = client.embeddings.create(
        model=deployment,
        input=text
    )
    return embeddings.data[0].embedding