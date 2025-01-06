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

class _EmbeddinigEncoderArkSmall():
    _EMBEDDING_TEXT_MODEL = "doubao-embedding-small"
    _EMBEDDING_MODEL_NAME = "ep-20241220102000-c4f7m"
    _EMBEDDING_VEC_LEN = 2560
    _g_client = None 

    @classmethod
    def get_client(cls):
        from openai import OpenAI
        if cls._g_client is None:
            cls._client = OpenAI(
                api_key=os.environ.get("ARK_API_KEY"),
                base_url="https://ark.cn-beijing.volces.com/api/v3",
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
            model=cls._EMBEDDING_MODEL_NAME,
            input=[text],
            encoding_format="float"
        )
        return embeddings.data[0].embedding
    
    @classmethod
    def get_embedding_encoder_name(cls):
        return cls._EMBEDDING_TEXT_MODEL


class _EmbeddingEncoderQwenSmall():
    """
    通用文本向量是由通义实验室 Embedding 编码器
    使用 text-embedding-v2 模型 
    """
    _EMBEDDING_TEXT_MODEL = "text-embedding-v2"
    _EMBEDDING_VEC_LEN = 1536
    _g_client = None

    @classmethod
    def get_client(cls):
        from openai import OpenAI
        if cls._g_client is None:
            cls._client = OpenAI(
                api_key=os.environ.get("DASHSCOPE_API_KEY"),
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1" 
            )
        return cls._client

    @classmethod
    def get_embedding_len(cls) -> int:
        return cls._EMBEDDING_VEC_LEN
    
    @classmethod
    def get_embedding_vec(cls, text) -> list[float]:
        text = text.replace("\n", " ")
        client = cls.get_client()
        embeddings = client.embeddings.create(
            model=cls._EMBEDDING_TEXT_MODEL,
            input=text,
            encoding_format="float"
        )
        return embeddings.data[0].embedding
    
    @classmethod
    def get_embedding_encoder_name(cls):
        return cls._EMBEDDING_TEXT_MODEL  
    


# ** Do not change the embedding encoder unless you know what you are doing **
#_EmbeddinigEncoder = _EmbeddinigEncoderOpenAIsmall
_EmbeddinigEncoder = _EmbeddinigEncoderArkSmall

def get_embeding_len() -> int:
    return _EmbeddinigEncoder._EMBEDDING_VEC_LEN

def get_embedding_vec(text) -> list[float]:
    return _EmbeddinigEncoder.get_embedding_vec(text)

def get_embedding_encoder_name():
    return _EmbeddinigEncoder.get_embedding_encoder_name()


if __name__ == "__main__":
    text = "hello"

    embedding = get_embedding_vec(text)
    rich.print(embedding[:16])
    rich.print(_EmbeddinigEncoder, get_embedding_encoder_name(), len(embedding), get_embeding_len())
    print()

    embedding = _EmbeddinigEncoderOpenAIsmall.get_embedding_vec(text)
    rich.print(embedding[:16])
    rich.print(_EmbeddinigEncoderOpenAIsmall, _EmbeddinigEncoderOpenAIsmall.get_embedding_encoder_name(), len(embedding), _EmbeddinigEncoderOpenAIsmall.get_embeding_len())
    print()

    embedding = _EmbeddinigEncoderArkSmall.get_embedding_vec(text)
    rich.print(embedding[:16])
    rich.print(_EmbeddinigEncoderArkSmall, _EmbeddinigEncoderArkSmall.get_embedding_encoder_name(), len(embedding), _EmbeddinigEncoderArkSmall.get_embeding_len()) 
    print()

    embedding = _EmbeddingEncoderQwenSmall.get_embedding_vec(text)
    rich.print(embedding[:16])
    rich.print(_EmbeddingEncoderQwenSmall,_EmbeddingEncoderQwenSmall.get_embedding_encoder_name(), len(embedding), _EmbeddingEncoderQwenSmall.get_embedding_len())
    print()