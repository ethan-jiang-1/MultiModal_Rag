import re

def extract_pure_text_from_markdown(md_content):
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

def remove_comment(line):
    """
    移除行中的 <!-- ... --> 注释。
    """
    return re.sub(r'<!--.*?-->', '', line).strip()
