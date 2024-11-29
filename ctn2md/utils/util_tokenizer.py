from whoosh.analysis import Tokenizer, Token
import tiktoken

class _ChineseTokenizer(Tokenizer):
    def __call__(self, value, positions=False, chars=False,
                 keeporiginal=False, removestops=True,
                 start_pos=0, start_char=0, mode='', **kwargs):

        import jieba
        t = Token(positions, chars, removestops=removestops, mode=mode,
                  **kwargs)

        seglist = jieba.cut(value, cut_all=True)
        for w in seglist:
            t.original = t.text = w
            t.boost = 1.0
            if positions:
                t.pos = start_pos + value.find(w)
            if chars:
                t.startchar = start_char + value.find(w)
            if chars and positions:
                t.endchar = start_char + value.find(w) + len(w)
            yield t


def get_chinese_analyzer():
    return _ChineseTokenizer()

g_tk_encoding = None

def get_token_encoding():
    global g_tk_encoding
    if g_tk_encoding is None:
        embedding_encoding = "cl100k_base"
        g_tk_encoding = tiktoken.get_encoding(embedding_encoding)
    return g_tk_encoding