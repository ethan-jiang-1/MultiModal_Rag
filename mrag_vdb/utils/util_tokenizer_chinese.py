
from typing import Generator
import rich
import logging   
from dotenv import load_dotenv
load_dotenv()

def get_chinese_analyzer():
    from whoosh.analysis import Tokenizer, Token
    logging.info("start load jieba...")
    import jieba
    logging.info("end loading jieba")

    class _ChineseTokenizer(Tokenizer):

        def __call__(self, value, positions=False, chars=False,
                    keeporiginal=False, removestops=True,
                    start_pos=0, start_char=0, mode='', **kwargs) -> Generator[Token, None, None]:

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

    return _ChineseTokenizer()


if __name__ == "__main__":
    from mmbase.utils.util_logging import setup_logger_handlers
    setup_logger_handlers()

    logging.info("start load tokenizer...")
    chinese_tokenizer = get_chinese_analyzer()
    logging.info("tokenizer loaded.")

    rich.print(chinese_tokenizer)

    ret3 = chinese_tokenizer("我爱北京天安门")
    rich.print(ret3)
    for token in ret3:
        print(token)

    ret3 = chinese_tokenizer("从这里来，到这里去")
    rich.print(ret3)
    for token in ret3:
        print(token)

