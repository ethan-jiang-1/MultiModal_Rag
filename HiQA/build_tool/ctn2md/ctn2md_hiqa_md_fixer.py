from dotenv import load_dotenv
import os
import sys
import logging
import rich
#import re
#import random
#import json
#import json_repair

load_dotenv()

if "./" not in sys.path:
    sys.path.append("./")

from HiQA.utils.util_logging import setup_logger_handlers
from HiQA.build_tool.ctn2md.md_info_base import save_md_info, load_md_info

HIQA_INSTRUCT = """
请帮我修改内容格式,我会给你一个PDF文档,文档中的文本可能是文字段落也可能来自表格。请将这些内容转换为markdown格式源码,且输出只有markdown源码,其他要求如下：
1. 无需考虑图片,只提取文字和表格

##2. 要求格式为,PDF文本中的每一章节都作为markdown中的一个一级标题(只用一个 # 号)章节,
   无论章节还是子章节的标题,都要用markdown的一级标题表示,我们将用章节的编号来标记章节的级别。
   该章节的内容从这一章节的标题的后一行开始写。

3. 重点是准确识别文本中的章节编号和表格,表格格式请仔细处理。

##4. 关于章节和编号,对于PDF中的一切章节,子章节,都要在markdown中对应一个一级标题章节(一个# 章节）并且用章节的编号来表示级别,
   而非多个#,章节编号均为"x.x.x. XXXX"的格式

##5. 关于表格,一旦遇你认为是表格,请处理成如下格式,表格内容用markdown的格式源码,但前后不要换行：
---table begin---
Table tile: Name of Table
| column0 | column1 | column2 |
|---|---|---|
| row1 | value | value |
| row2 | value | value |
---table end---
说明：表格的前后由"---table begin---"和"---table end---"包裹,"---table begin---"的下一行是表名。
在提供的文本中,表格会被处理成每个cell一行,当你发现内容是表格时,请重新将其排列为markdown的表格格式。
此外,表格所在的段落也应有独立的标题。

##6. 转换后的每个章节中只能有一个表格,如果有多段表格,请为每一个表格设置一个新章节,放置这个表格,并且设置合适的标题。
7. 输出内容只包含markdown源码,不要输出任何其他内容。markdown源码前后不要有说明和补充。
8. 你是一个支持超长文本的模型,你的任务是格式处理,因此不要省略、总结、丢弃任何内容,只要是输入的内容,也包括表格内容,都要在输出中体现出来。

##9. 不要带 '```', 'markdown' 这种多余内容

##10. 请谨慎使用 '#' 符号,这代表后面是一个独立章节的编号和标题。请正确,准确的使用'#'号设置章节。这一章节的内容从标题的后一行开始写。

##11. 请为每个章节设置一个准确、简要的标题。如果原文中有合适的标题请保留原文标题,若无,则设置一个合适的标题。
##12. 章节编号请使用阿拉伯数字,请使用小数点'.'作为编号间隔符,请严格遵循上下文的编号,如上一段为 '# 3. '时,其子章节为 '# 3.2. '

13. 请严格保证章节编号是正确的、递增的、层次的,请正确,准确的设置章节编号,请确保每个段落都有编号。
"""


def fix_markdown_content_for_hiqa(md_info_path):
    out_dir = os.path.dirname(md_info_path)
    md_info = load_md_info(md_info_path)
    if md_info is None:
        return None, None 

    fname_output_s2_md = md_info.get("fname_output_s2_md", None)
    if fname_output_s2_md is None:
        return None, None 

    pname_s2 = os.path.join(out_dir, fname_output_s2_md)
    with open(pname_s2, "r", encoding="utf8") as f:
        md_text = f.read()
        rich.print(md_text)

    #md_text_new = filter_markdown_images(md_text, out_dir, md_info)
    md_text_new = md_text

    fname_s3_md_name = os.path.basename(fname_output_s2_md).replace("_s2.md", "_s3.md")
    fname_output_s3_md = os.path.join(out_dir, fname_s3_md_name)
    with open(fname_output_s3_md, "w+") as f:
        f.write(md_text_new)

    logging.info(f"fname_s3_md_name: {fname_s3_md_name}")
    if isinstance(md_info, dict):
        md_info["fname_output_s3_md"] = os.path.basename(fname_output_s3_md)
        save_md_info(out_dir, md_info)
    return fname_output_s2_md, md_info    


if __name__ == "__main__":
    setup_logger_handlers()

    #md_info_path = "_work/ctn2md_exam0/info.json"
    #md_info_path = "_work/ctn2md_chatgpt/info.json"
    md_info_path = "_work/ctn2md_backpanel/info.json"
    md_info_path, md_info = fix_markdown_content_for_hiqa(md_info_path)
    print(md_info_path)
    rich.print(md_info)