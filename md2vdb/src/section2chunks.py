from dotenv import load_dotenv
#import os
import re
import sys
#import logging
import rich
from dataclasses import dataclass

load_dotenv()

if "./" not in sys.path:
    sys.path.append("./")

from md2vdb.utils.util_tokenizer import get_token_encoding

MAX_TOKENS_IN_CHUNK = 512


@dataclass
class OrderedNames:
    order: str 
    title: str 
    desc: str

@dataclass
class ChunkedSectionInfo:
    chunk_id: str
    parent: str
    order: int
    title: str
    desc: str
    max_tokens_in_chunk: int
    doc_path: str 
    doc_title: str
    doc_chunk: str

def _parse_ordered_name(line):
    # 正则表达式匹配结构：
    # 1) [ordered_name] 和 [ordered_name] 之间的层级标识（数字.数字.数字）
    # 2) 层级标识后面的标题
    # 3) [desc] 和 [desc] 之间的内容作为 desc
    pattern = re.compile(r'''
        \[ordered_name\]\s*         # 匹配[ordered_name]，后面可能有空格
        (?P<order>[\d\.]+)          # 匹配层级标识，格式为数字.数字.数字，如 1.4.6
        \)\s*                        # 匹配右括号
        (?P<title>.*?)               # 匹配标题内容（非贪婪模式，直到下一个标记）
        \[ordered_name\]\s*          # 匹配结束的[ordered_name]标签
        \[desc\]\s*(?P<desc>.*?)\s*\[desc\]  # 匹配[desc]和[desc]之间的内容，作为desc
    ''', re.VERBOSE | re.DOTALL)
    
    # 搜索匹配
    match = pattern.search(line)
    
    if match:
        order = match.group("order")
        title = match.group("title").strip()
        desc = match.group("desc").strip()
        return OrderedNames(order, title, desc)
    else:
        return None

def _get_parent_id(id):
    if id.find(".") == -1:
        return ""
    names = id.split(".")
    names = names[0:len(names)- 1]
    return ".".join(names)

def chunk_section_to_chunks(md_section, doc_path=None, doc_title=None, max_tokens_in_chunk=MAX_TOKENS_IN_CHUNK, need_desc_at_top=True):
    lines = md_section.splitlines()

    ordered_names = None
    total_tokens = 0
    chunks = {}
    chunk_no = 0
    for line in lines:
        if line.startswith("<!-- [desc]"):
            continue 
        if line.startswith("<!-- [ordered_name]"):
            if ordered_names is not None:
                raise ValueError("order_names found twice?")
            ordered_names = _parse_ordered_name(line)
            if not isinstance(ordered_names, OrderedNames):
                raise ValueError("Not able found all information")
            continue
                
        if ordered_names is None:
            raise ValueError("not qualified section -- no [ordered_name] found")
        token_count = len(get_token_encoding().encode(line)) + 1 
        if total_tokens + token_count > max_tokens_in_chunk:
            chunk_no += 1
            if chunk_no not in chunks:
                chunks[chunk_no] = []
                if need_desc_at_top:
                    chunks[chunk_no].append(f"[desc] {ordered_names.desc} [desc]")
            chunks[chunk_no].append(line)
            total_tokens = token_count
        else:
            if chunk_no not in chunks:
                chunks[chunk_no] = []
                if need_desc_at_top:
                    chunks[chunk_no].append(f"[desc] {ordered_names.desc} [desc]")
            chunks[chunk_no].append(line)
            total_tokens += token_count

    
    if ordered_names is None:
        raise ValueError("No ordered_name")

    id = ordered_names.order
    parent = _get_parent_id(id)
    title = ordered_names.title
    desc = ordered_names.desc
    max_tokens_in_chunk = max_tokens_in_chunk

    csis = []
    for order, chunk in chunks.items():
        order = int(order)
        doc_chunk = "\n".join(chunk)
        csi = ChunkedSectionInfo(chunk_id=id, 
                                 parent=parent, 
                                 order=order, 
                                 title=title, 
                                 desc=desc, 
                                 max_tokens_in_chunk=max_tokens_in_chunk, 
                                 doc_path=doc_path, 
                                 doc_title=doc_title, 
                                 doc_chunk=doc_chunk)
        csis.append(csi)

    return csis

def _test_parse_ordered_name():
    line ="<!-- [ordered_name] 1) 深度学习在视电阻率快速反演中的研究 [ordered_name] [desc] 深度学习在视电阻率快速反演中的研究 [desc] -->"
    ret = _parse_ordered_name(line)
    rich.print(ret)

    line = "<!-- [ordered_name] 3.2.1) 卷积层与 BN 层参数融合 [ordered_name] [desc] 深度学习卷积和重参数化原理 __ 重参数化原理 __ 卷积层与 BN 层参数融合 [desc] -->"
    ret = _parse_ordered_name(line)
    rich.print(ret)

def _test_chunk_secion():   
    pname_md_section = "_work/ctn2md_深度学习在视电阻率快速反演中的研究_lvlm/xcs_6a2683b0_0006_3_1_1-_卷积原理.md"    
    doc_path = "_work/ctn2md_深度学习在视电阻率快速反演中的研究_lvlm/深度学习在视电阻率快速反演中的研究.pdf"
    doc_title = "深度学习在视电阻率快速反演中的研究和应用"

    with open(pname_md_section, encoding="utf-8") as f:
        md_section = f.read()

    csis = chunk_section_to_chunks(md_section, doc_path=doc_path, doc_title=doc_title, max_tokens_in_chunk=256)
    rich.print(csis)            

if __name__ == "__main__":
    _test_parse_ordered_name()

    _test_chunk_secion()




    