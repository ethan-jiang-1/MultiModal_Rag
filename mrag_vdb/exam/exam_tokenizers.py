import pyrwkv_tokenizer
tokenizer = pyrwkv_tokenizer.RWKVTokenizer()
ret = tokenizer.encode("Today is a beautiful day. 今天是美好的一天。")
print(ret)

