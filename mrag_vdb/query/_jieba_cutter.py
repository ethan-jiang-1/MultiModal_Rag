import jieba
from typing import List

chinese_stopwords = [
    "的", "了", "在", "是", "我", "我们", "你", "你们", "他", "她", "它", "这", "那", 
    "和", "与", "对", "对于", "与其", "就", "都", "但", "但是", "或者", "如果", "仅仅", 
    "所以", "为什么", "怎么", "怎么样", "就是", "已经", "可能", "会", "的话", "很", "非常", 
    "太", "只", "并", "不", "没有", "没", "这样", "就", "并且", "还是", "在于", "作为", "当", 
    "因为", "之后", "此外", "所有", "于是", "然后", "这样", "就是", "你们", "她们", "它们", 
    "其中", "例如", "一下", "一些", "其他", "更多", "更", "更加", "相对", "如果", "希望", 
    "但是", "然而", "据说", "即使", "一直", "所", "与其", "这样", "将", "所以", "更加", "一起", 
    "当然", "不是", "为了", "以及", "对比", "并且", "或者", "如何", "虽然", "即便", "便", "而", 
    "如", "得", "那", "而是", "为", "只有", "自己", "此", "其", "向", "比", "给", "可以", "不能", 
    "已经", "依然", "且", "为了", "从", "到", "无", "用", "没有", "没有", "这样", "请", "到", "同", 
    "比", "就", "不是", "从而", "却", "不过", "用以", "似乎", "可", "不是", "所有", "还是", "它", 
    "都", "真是", "如同", "便", "为了", "一种", "那些", "是", "向", "也", "同样", "当", "对"
]

# 英文常见停用词列表
english_stopwords = [
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", 
    "are", "aren't", "aren't", "as", "at", "be", "because", "been", "before", "being", 
    "below", "between", "both", "but", "by", "can't", "cannot", "could", "couldn't", 
    "did", "didn't", "do", "does", "doesn't", "don't", "doing", "don't", "down", 
    "during", "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't", 
    "have", "haven't", "having", "he", "he'd", "he'll", "he's", "had", "had", "how", 
    "how's", "here", "hereafter", "hereby", "herein", "hereinafter", "hereupon", "hers", 
    "herself", "he's", "how", "how's", "i", "i'd", "i'll", "i'm", "i've", "if", "in", 
    "isn't", "into", "is", "isn't", "it", "it'd", "it'll", "it's", "i.e.", "of", "off", 
    "on", "once", "only", "onto", "or", "other", "ought", "our", "ours", "ourselves", 
    "out", "over", "per", "quite", "rather", "said", "same", "shall", "shan't", "she", 
    "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such", "than", 
    "that", "that's", "that", "the", "their", "theirs", "them", "themselves", "there", 
    "therefore", "these", "they", "they'd", "they'll", "they're", "they've", "to", "too", 
    "under", "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're", 
    "we've", "were", "weren't", "what", "what's", "what've", "when", "when's", "when", 
    "where", "where's", "where", "which", "which's", "while", "who", "who'd", "who'll", 
    "who's", "whom", "why", "why's", "why", "with", "won't", "would", "wouldn't", "you", 
    "you'd", "you'll", "you're", "you've", "your", "yours", "yourself", "yourselves"
]

# 中英文常见标点符号集合
punctuation = set([
    '，', '。', '！', '？', '：', '；', '“', '”', '《', '》', '（', '）', 
    '【', '】', '—', '、', '·', '.', ',', '!', '?', ':', ';', '"', '(', ')', 
    '[', ']', '{', '}', '<', '>', "'", '`', '~', '(', ')', '&', '#', '%', 
    '$', '@', '^', '=', '+', '-', '_', '/', '\\', '|', '*', '...'
])

def jieba_cut(text_str: str) -> List[str]:
    """
    使用 jieba 对查询字符串进行分词，并过滤中文和英文的停用词。
    
    :param text_str: 输入文本
    :return: 过滤停用词后的分词列表
    """
    # 对中文文本进行分词
    words = jieba.cut(text_str)

    # 过滤掉中文停用词、英文停用词、标点符号和空格
    filtered_words = [
        word for word in words 
        if word not in chinese_stopwords 
        and word not in english_stopwords 
        and word not in punctuation 
        and word.strip() != ""
    ]
    return filtered_words

if __name__ == "__main__":
    query_str = "我想要找一份关于自然语言处理的工作, are you kidding? 中英文符号：，。！？ .,!? " 
    print("query_str", query_str)
    print("jieba cut", jieba_cut(query_str))