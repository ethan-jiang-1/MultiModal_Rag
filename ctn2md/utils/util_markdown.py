import re
from typing import List

def extract_pure_text_from_markdown(md_content: str) -> str:
    """
    从 Markdown 内容中提取纯文本内容。
    :param md_content: str, Markdown 格式内容
    :return: str, 提取后的纯文本内容
    """
    # 1. 移除 Markdown 图片引用 ![alt](image_url)
    md_content = re.sub(r'!\[.*?\]\(.*?\)', '', md_content)

    # 2. 移除 HTML 注释 <!-- ... -->
    md_content = re.sub(r'<!--.*?-->', '', md_content, flags=re.DOTALL)

    # 3. 移除其他 Markdown 语法标记 (#, *, -, >, etc.)
    md_content = re.sub(r'[>#*_\-`~\[\]]', '', md_content)

    # 4. 替换 Markdown 链接引用 [text](url) 为 text
    md_content = re.sub(r'\[([^\]]+)\]\(.*?\)', r'\1', md_content)

    # 5. 移除所有换行符和空白字符（包括制表符、空格等）
    md_content = re.sub(r'\s+', '', md_content)

    # 返回提取后的纯文本内容
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
