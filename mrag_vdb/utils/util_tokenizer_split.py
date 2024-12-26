from dotenv import load_dotenv
import rich

load_dotenv()

class _TokenizerRemoteOpenAI():
    _TOKENIZER_TEXT_MODEL = "cl100k_base"
    _g_tk_encoding = None
    
    @classmethod
    def get_tokens(cls, text:str) -> list[int]:
        import tiktoken

        def _get_token_encoding(cls) -> tiktoken.Encoding:
            if cls._g_tk_encoding is None:
                cls._g_tk_encoding = tiktoken.get_encoding(cls._TOKENIZER_TEXT_MODEL)
            return cls._g_tk_encoding  

        encoding = _get_token_encoding(cls)
        return encoding.encode(text)
    
class _TokenizerLocalRWKV():
    @classmethod
    def get_tokens(cls, text:str) -> list[int]:
        import pyrwkv_tokenizer
        tokenizer = pyrwkv_tokenizer.RWKVTokenizer()
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