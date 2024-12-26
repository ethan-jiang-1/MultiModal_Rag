from dotenv import load_dotenv
import rich

load_dotenv()

class _TokenizerRemoteOpenAI():
    _TOKENIZER_TEXT_MODEL = "cl100k_base"
    _g_tk_encoding = None
    def _get_tokenizer(cls):
        import tiktoken
        if cls._g_tk_encoding is None:
            cls._g_tk_encoding = tiktoken.get_encoding(cls._TOKENIZER_TEXT_MODEL)
        return cls._g_tk_encoding  

    @classmethod
    def get_tokens(cls, text:str) -> list[int]:
        tokenizer = cls._get_tokenizer(cls)
        return tokenizer.encode(text)
    
class _TokenizerLocalRWKV():
    _g_rwkv_tokenizer = None

    @classmethod
    def _get_tokenizer(cls):
        if cls._g_rwkv_tokenizer is None:
            import pyrwkv_tokenizer
            cls._g_rwkv_tokenizer = pyrwkv_tokenizer.RWKVTokenizer()
        return cls._g_rwkv_tokenizer
    
    @classmethod
    def get_tokens(cls, text:str) -> list[int]:
        tokenizer = cls._get_tokenizer()
        return tokenizer.encode(text)
    
#_Tokenizer = _TokenizerOpenAI
_Tokenizer = _TokenizerLocalRWKV
def get_text_tokens(text:str) -> list[str]:
    return _Tokenizer.get_tokens(text)

if __name__ == "__main__":

    ret1 = get_text_tokens("I love to eat apples.")
    rich.print(ret1)
    ret2 = get_text_tokens("豆包")
    rich.print(ret2)


    ret1 = _TokenizerLocalRWKV.get_tokens("I love to eat apples.")
    rich.print(ret1)
    ret2 = _TokenizerLocalRWKV.get_tokens("豆包")
    rich.print(ret2)
    
    ret1 = _TokenizerRemoteOpenAI.get_tokens("I love to eat apples.")
    rich.print(ret1)
    ret2 = _TokenizerRemoteOpenAI.get_tokens("豆包")
    rich.print(ret2)