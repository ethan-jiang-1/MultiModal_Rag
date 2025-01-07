import re
from typing import List

def extract_pure_text_from_markdown(md_content: str) -> str:
    """
    Extract searchable text content from Markdown for FTS (Full Text Search).
    :param md_content: Markdown formatted content
    :return: Clean text for searching
    """
    # 1. 保留图片和链接的文本内容
    md_content = re.sub(r'!\[(.*?)\]\(.*?\)', r'\1', md_content)  # 图片 alt text
    md_content = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', md_content)   # 链接文本
    
    # 2. 移除 HTML 注释和 Markdown 标记符号
    md_content = re.sub(r'<!--.*?-->', '', md_content, flags=re.DOTALL)
    md_content = re.sub(r'[#*_`~\[\]]', '', md_content)  # 移除常见 Markdown 标记
    
    # 3. 规范化空白字符
    md_content = re.sub(r'\s+', ' ', md_content).strip()
    
    return md_content

def remove_comment(line: str) -> str:
    """
    移除行中的 <!-- ... --> 注释。
    """
    return re.sub(r'<!--.*?-->', '', line).strip()

def read_markdown_file(md_pathname: str) -> str:
    """
    读取 Markdown 文件内容。
    """
    encodings = ['utf-8', 'gbk', 'gb2312', 'gb18030', 'big5']
    for encoding in encodings:
        try:
            with open(md_pathname, "r", encoding=encoding) as f:
                content = f.read()
                break
        except UnicodeDecodeError:
            if encoding == encodings[-1]:
                raise ValueError(f"Could not decode file {md_pathname} with any of the attempted encodings")
            continue
    return content

def find_all_image_refs(md_pathname: str) -> List[str]:
    """
    查找Markdown文件中的所有图片引用。
    
    Args:
        md_pathname: Markdown文件路径
        
    Returns:
        包含所有图片URL的列表
    """
    content = read_markdown_file(md_pathname)
    image_refs = re.findall(r'!\[.*?\]\(([^\)]+?)\s*(?:\".*?\")?\)', content)
    return image_refs
