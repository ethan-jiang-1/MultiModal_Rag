from dotenv import load_dotenv
#import os
import sys
#import logging
import rich

load_dotenv()

if "./" not in sys.path:
    sys.path.append("./")

from ctn2md.utils.util_logging import setup_logger_handlers
#from ctn2md.src.md_info_base import MdInfo

def exam_md2csv(pname_md):
    from HiQA.build_tool.md2csv import parse_markdown


    with open(pname_md, 'r', encoding="utf8") as f:
        file_content = f.read()

    doc_title, sections = parse_markdown(file_content)
    rich.print(doc_title)
    print(f"number of sections: {len(sections)}")
    rich.print(sections)

    # md_info_path = find_md_info_path(pname_md)
    # md_info = load_md_info(md_info_path)
    # rich.print(md_info)

if __name__ == "__main__":
    setup_logger_handlers()

    #pname_md = "_work/ctn2md_时代的人力资源管理进化(徐刚)/AIGC时代的人力资源管理进化(徐刚)___pdf.md"
    pname_md = "_work/ctn2md_时代的人力资源管理进化(徐刚)/AIGC时代的人力资源管理进化(徐刚)___pdf_s40.md"

    exam_md2csv(pname_md)

