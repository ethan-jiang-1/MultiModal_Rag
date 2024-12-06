from dotenv import load_dotenv
import os
import sys
import logging
import rich
#import random
#import re
#import shutil

load_dotenv()

if "./" not in sys.path:
    sys.path.append("./")

from ctn2md.utils.util_logging import setup_logger_handlers
from ctn2md.src.md_info_base import MdInfo
from ctn2md.gen_lp.gen_markdown_llamaparse import generate_markdown_llamaparse
from ctn2md.utils.util_ctn_type import CTN_TYPE

def gen_md_llamaparse(doc_pathname, out_dir):
    logging.info(f"##MDFLOW##: gen_md_llamaparse started...")

    md_info = MdInfo(out_dir)
    md_info.set_gen_engine("llamaparse:lp")
    md_info.set_doc_pathname(doc_pathname)

    md_info_path = generate_markdown_llamaparse(md_info)

    logging.info(f"##MDFLOW##: gen_md_llamaparse end")
    return md_info_path


class GenMd_LlamaParse:
    @classmethod
    def generate_markdown(cls,
                          doc_pathname, 
                          out_dir=None, 
                          enforced_gen=False, 
                          mdcontrols=None):
        if not cls.does_support_doc_type(doc_pathname):
            raise ValueError(f"LlamaParseGen does not support {doc_pathname}")

        md_info_path = None
        gen_needed = False
        if not enforced_gen:
            md_info = MdInfo(out_dir)
            md_info_path = md_info.get_md_info_path()
            pathname_s0_md = md_info.name_step_pathname(0)
            if (pathname_s0_md is None) or (not os.path.exists(pathname_s0_md)):
                gen_needed = True
        else:
            gen_needed = True

        if gen_needed:
            md_info_path = gen_md_llamaparse(doc_pathname, out_dir)
            if md_info_path is None:
                return None

        if mdcontrols is not None:
            md_info.update_mdcontrols(mdcontrols)
        return md_info_path

    @classmethod
    def need_followup_step(cls, step_name):
        if step_name == "fix_headings_plc_by_gpt":
            return True 
        return True

    @classmethod
    def does_support_doc_type(cls, doc_pathname):
        ctn_type = CTN_TYPE.get_ctn_type_by_doc_pathname(doc_pathname)
        if ctn_type in [CTN_TYPE.PDF, CTN_TYPE.PPT, CTN_TYPE.DOC, CTN_TYPE.XLS]:
            return True
        return False


if __name__ == "__main__":
    #doc_pathname = "datasrc/test/raw_docs/AIGC时代的人力资源管理进化(徐刚).pdf"
    #doc_pathname = "datasrc/test/raw_docs/业绩案例、上汽内外饰DRE外包框架服务合同.pdf"
    #doc_pathname = "datasrc/test/raw_docs/1. 座椅STO间隙 P1.pptx"
    #doc_pathname = "datasrc/test/raw_docs/管理者角色定位与认知课程大纲.docx"
    #doc_pathname = "datasrc/test/raw_docs/考勤修改统一规则.xlsx"
    #doc_pathname = "datasrc/test/raw_docs/5. back panel 与环境匹配工程校核_P2.pptx"
    
    #doc_pathname = "datasrc/exam/raw_docs/ChatGPT intimates a tantalizing future_compressed.pdf"
    doc_pathname = "datasrc/exam/raw_docs/深度学习在视电阻率快速反演中的研究.pdf"

    out_dir = MdInfo.get_suggested_out_dir(doc_pathname)

    setup_logger_handlers()
    os.makedirs(out_dir, exist_ok=True)
    md_info_path = gen_md_llamaparse(doc_pathname, out_dir)
    print(md_info_path)

    md_info = MdInfo(md_info_path)
    rich.print(md_info)
    print(md_info_path)