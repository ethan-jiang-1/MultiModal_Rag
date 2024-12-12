from dotenv import load_dotenv
#import os
import sys
#import logging
import rich

load_dotenv()

if "./" not in sys.path:
    sys.path.append("./")

from md2vdb.utils.util_tokenizer import get_token_encoding

MAX_TOKENS_IN_CHUNK = 256

def chunk_section(md_section, max_tokens_in_chunk=MAX_TOKENS_IN_CHUNK):
    lines = md_section.splitlines()

    desc = None
    total_tokens = 0
    chunks = {}
    chunk_no = 0
    for line in lines:
        if line.startswith("<!-- [desc]"):
            desc = line.replace("<!-- ", "").replace(" -->", "")
            continue 
        if line.startswith("<!-- [ordered_name]"):
            continue

        if desc is None:
            raise ValueError("not qualified section -- no [desc]")
        token_count = len(get_token_encoding().encode(line)) + 1 
        if total_tokens + token_count > max_tokens_in_chunk:
            chunk_no += 1
            if chunk_no not in chunks:
                chunks[chunk_no] = []
            chunks[chunk_no].append(line)
            total_tokens = token_count
        else:
            if chunk_no not in chunks:
                chunks[chunk_no] = []
            chunks[chunk_no].append(line)
            total_tokens += token_count

    return desc, chunks            

if __name__ == "__main__":
    pname_md_section = "_work/ctn2md_深度学习在视电阻率快速反演中的研究_lvlm/xcs_6a2683b0_0008_3_2_2-_结构重参数化原理.md"

    with open(pname_md_section, encoding="utf-8") as f:
        md_section = f.read()

    desc, chunks = chunk_section(md_section)
    rich.print(desc)
    rich.print(chunks)

    