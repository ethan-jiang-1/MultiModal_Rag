from dotenv import load_dotenv
#import os
import re
import sys
#import logging
import rich
from dataclasses import dataclass
from typing import List

load_dotenv()

if "./" not in sys.path:
    sys.path.append("./")

from mrag_vdb.utils.util_tokenizer import get_token_encoding
from mrag_vdb.common.chunked_meta_info import ChunkedSectionInfo

MAX_TOKENS_IN_CHUNK = 512


@dataclass
class OrderedNames:
    toc_order: str 
    heading: str 
    desc: str


def _parse_ordered_name(line:str) -> dict:
    # 正则表达式匹配结构：
    # 1) [ordered_name] 和 [ordered_name] 之间的层级标识（数字.数字.数字）
    # 2) 层级标识后面的标题
    # 3) [desc] 和 [desc] 之间的内容作为 desc
    pattern = re.compile(r'''
        \[ordered_name\]\s*         # 匹配[ordered_name]，后面可能有空格
        (?P<toc_order>[\d\.]+)          # 匹配层级标识，格式为数字.数字.数字，如 1.4.6
        \)\s*                        # 匹配右括号
        (?P<heading>.*?)               # 匹配标题内容（非贪婪模式，直到下一个标记）
        \[ordered_name\]\s*          # 匹配结束的[ordered_name]标签
        \[desc\]\s*(?P<desc>.*?)\s*\[desc\]  # 匹配[desc]和[desc]之间的内容，作为desc
    ''', re.VERBOSE | re.DOTALL)
    
    # 搜索匹配
    match = pattern.search(line)
    
    if match:
        toc_order = match.group("toc_order")
        heading = match.group("heading").strip()
        desc = match.group("desc").strip()
        return OrderedNames(toc_order, heading, desc)
    else:
        return None

def _get_parent_id(sec_id:str) -> str:
    if sec_id.find(".") == -1:
        return ""
    names = sec_id.split(".")
    names = names[0:len(names)- 1]
    return ".".join(names)

def _get_toc_level(sec_id:str) -> int:
    names = sec_id.split(".")
    return len(names)

def split_section_to_chunks(md_section:str, doc_unique_id:str, doc_title:str = None, fname_org_doc:str = None, max_tokens_in_chunk:int = MAX_TOKENS_IN_CHUNK, need_desc_at_top: bool = True) -> List[ChunkedSectionInfo]:
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

    sec_id = ordered_names.toc_order
    parent = _get_parent_id(sec_id)
    level = _get_toc_level(sec_id)
    heading = ordered_names.heading
    desc = ordered_names.desc
    max_tokens_in_chunk = max_tokens_in_chunk

    csis = []
    total = len(chunks.keys())
    for order, chunk in chunks.items():
        order = int(order)
        doc_chunk = "\n".join(chunk)
        csi = ChunkedSectionInfo(sec_id=sec_id, 
                                 parent_sec_id=parent, 
                                 level=level,
                                 order=order,
                                 total=total, 
                                 heading=heading, 
                                 desc=desc,
                                 max_tokens=max_tokens_in_chunk, 
                                 doc_unique_id=doc_unique_id, 
                                 doc_title=doc_title, 
                                 fname_org_doc=fname_org_doc,
                                 content=doc_chunk,
                                 sec_seq_no=-1)
        csis.append(csi)

    return csis

def _test_parse_ordered_name():
    line ="<!-- [ordered_name] 1) 深度学习在视电阻率快速反演中的研究 [ordered_name] [desc] 深度学习在视电阻率快速反演中的研究 [desc] -->"
    ret = _parse_ordered_name(line)
    rich.print(ret)

    line = "<!-- [ordered_name] 3.2.1) 卷积层与 BN 层参数融合 [ordered_name] [desc] 深度学习卷积和重参数化原理 __ 重参数化原理 __ 卷积层与 BN 层参数融合 [desc] -->"
    ret = _parse_ordered_name(line)
    rich.print(ret)

def _test_chunk_secion(max_tokens_in_chunk=256):   
    pname_md_section = "_work/ctn2md_深度学习在视电阻率快速反演中的研究_lvlm/xcs_ca5fb9b7_0006_3_1_1-_卷积原理.md"    
    doc_unique_id = "深度学习在视电阻率快速反演中的研究_1234"
    doc_title = "深度学习在视电阻率快速反演中的研究和应用"

    with open(pname_md_section, encoding="utf-8") as f:
        md_section = f.read()

    csis = split_section_to_chunks(md_section, doc_unique_id, doc_title=doc_title, max_tokens_in_chunk=max_tokens_in_chunk)
    rich.print(csis)            

if __name__ == "__main__":
    _test_parse_ordered_name()

    _test_chunk_secion(max_tokens_in_chunk=256)




    