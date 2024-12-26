from dotenv import load_dotenv
import os
import openai
import rich
#from openai import OpenAI

load_dotenv()


class _EmbeddinigEncoderOpenAIsmall():
    _EMBEDDING_TEXT_MODEL = "text-embedding-3-small"
    _EMBEDDING_VEC_LEN = 1536
    _g_client = None 

    @classmethod
    def get_client(cls):
        if cls._g_client is None:
            cls._client = openai.AzureOpenAI(
                azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
                api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
                api_version=os.environ.get("AZURE_OPENAI_VERSION")
            )
        return cls._client

    @classmethod
    def get_embeding_len(cls) -> int:
        return cls._EMBEDDING_VEC_LEN
    
    @classmethod
    def get_embedding_vec(cls, text) -> list[float]:
        text = text.replace("\n", " ")
        client = cls.get_client()
        embeddings = client.embeddings.create(
            model=cls._EMBEDDING_TEXT_MODEL,
            input=text
        )
        return embeddings.data[0].embedding
    
    @classmethod
    def get_embedding_encoder_name(cls):
        return cls._EMBEDDING_TEXT_MODEL  


_EmbeddinigEncoder = _EmbeddinigEncoderOpenAIsmall

def get_embeding_len() -> int:
    return _EmbeddinigEncoder._EMBEDDING_VEC_LEN

def get_embedding_vec(text) -> list[float]:
    return _EmbeddinigEncoder.get_embedding_vec(text)

def get_embedding_encoder_name():
    return _EmbeddinigEncoder.get_embedding_encoder_name()



if __name__ == "__main__":
    embedding = get_embedding_vec("hello")
    rich.print(embedding[:16])
    print(len(embedding))