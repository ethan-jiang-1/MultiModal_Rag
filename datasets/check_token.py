import os
import pandas as pd
import tqdm
import sys

if "./" not in sys.path:
    sys.path.append("./")

from HiQA.utils.tokenizer import get_token_encoding
encoding = get_token_encoding()

total_row = 0
total_char = 0
total_tokens = 0
total_words = 0

kb_name = "test"
emd_dir = f"datasets/{kb_name}/embeddings"
for file in tqdm.tqdm(os.listdir(emd_dir)):
    if not file.endswith(".csv"):
        continue
    if os.path.getsize(os.path.join(emd_dir, file)) <= 2:
        continue

    df = pd.read_csv(os.path.join(emd_dir, file), encoding='utf-8')
    total_row += len(df)
    for _, row in df.iterrows():
        total_char += len(row['section'])
        total_words += len(row['section'].split(' '))
        total_tokens += len(encoding.encode(row['section']))

print(f'kb_name: {kb_name}')
print('total row:', total_row)
print('total char:', total_char)
print('total tokens:', total_tokens)
print('total words:', total_words)

