from dotenv import load_dotenv
#import os
import sys
#import logging
import rich

load_dotenv()

if "./" not in sys.path:
    sys.path.append("./")

from HiQA.utils.util_logging import setup_logger_handlers
from HiQA.build_tool.ctn2md.md_info_base import load_md_info, find_md_info_path
from HiQA.build_tool.md2csv import parse_markdown

def exam_md2csv(pname_md):
    with open(pname_md, 'r', encoding="utf8") as f:
        file_content = f.read()

    doc_title, sections = parse_markdown(file_content)
    rich.print(doc_title)
    rich.print(sections)

    md_info_path = find_md_info_path(pname_md)
    md_info = load_md_info(md_info_path)
    rich.print(md_info)

if __name__ == "__main__":
    setup_logger_handlers()

    #pname_md = "_work/ctn2md_exam10/AIGC时代的人力资源管理进化(徐刚)___pdf_s2.md"
    pname_md = "_work/md_samples/5. back panel 与环境匹配工程校核_P2___pptx_s3.md"
    exam_md2csv(pname_md)

