from dotenv import load_dotenv
import os
import sys
import logging
import rich
#import random
#import json
#import shutil

load_dotenv()

if "./" not in sys.path:
    sys.path.append("./")

from ctn2md.utils.util_logging import setup_logger_handlers
from ctn2md.src.md_info_base import MdInfo, MIFN
from ctn2md.src.ctn2md_gen_md_llamaparse import gen_md_llamaparse
from ctn2md.src.ctn2md_fix_heading_plc import fix_headings_plc_by_gpt
from ctn2md.src.ctn2md_inject_section_hierarchy import inject_section_heirarchy
from ctn2md.src.ctn2md_summarize_content import summarize_content_by_gpt
from ctn2md.src.make_final_md import make_final_md

def initial_gen_md_by_llamaparse(ctn_pathname, 
                                 out_dir=None, 
                                 enforced_gen=False, 
                                 mdcontrols=None):
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
        md_info_path = gen_md_llamaparse(ctn_pathname, out_dir)
        if md_info_path is None:
            return None

    if mdcontrols is not None:
        md_info.update_mdcontrols(mdcontrols)
    return md_info_path

def _reset_md_flow(md_info_path):
    md_info = MdInfo(md_info_path)
    dict_md_flow = md_info[MIFN.MDFLOW]
    for key in list(dict_md_flow.keys()): 
        if key != "0":
            del dict_md_flow[key]
    md_info.save()

def _do_content2md_convert_core(ctn_pathname, 
                                out_dir=None, 
                                enforced_gen=False, 
                                mdcontrols=None):
    if out_dir is None:
        out_dir = MdInfo.get_suggested_out_dir(ctn_pathname)
    logging.warning(f"work out_dir: {out_dir}")
    os.makedirs(out_dir, exist_ok=True)

    md_info_path = initial_gen_md_by_llamaparse(ctn_pathname, out_dir=out_dir, enforced_gen=enforced_gen, mdcontrols=mdcontrols)
    if md_info_path is None:
        logging.error(f"DCCC: failed {md_info_path} @initial_gen_md_by_llamaparse")
        return None

    _reset_md_flow(md_info_path)

    md_info_path = fix_headings_plc_by_gpt(md_info_path, src_step_num=0)
    if md_info_path is None:
        logging.error(f"DCCC: failed {md_info_path} @fix_headings_plc_by_gpt")
        return None 

    md_info_path = inject_section_heirarchy(md_info_path, src_step_num=1)
    if md_info_path is None:
        logging.error(f"DCCC: failed {md_info_path} @inject_section_heirarchy")
        return None

    md_info_path = summarize_content_by_gpt(md_info_path, src_step_num=2)
    if md_info_path is None:
        logging.error(f"DCCC: failed {md_info_path} @summarize_content_by_gpt")
        return None       

    final_md_path = make_final_md(md_info_path)

    return final_md_path

def do_content2md_convert(ctn_pathname, out_dir=None, enforced_gen=False, mdcontrols=None):
    final_md_path = None
    try:
        final_md_path = _do_content2md_convert_core(ctn_pathname,
                                                    out_dir=out_dir,
                                                    enforced_gen=enforced_gen,
                                                    mdcontrols=mdcontrols)
    except Exception as ex:
        logging.exception(ex)
        raise ex
    return final_md_path

if __name__ == "__main__":
    setup_logger_handlers()

    doc_pathname = "datasrc/test/raw_docs/AIGC时代的人力资源管理进化(徐刚).pdf"
    #doc_pathname = "datasrc/test/raw_docs/业绩案例、上汽内外饰DRE外包框架服务合同.pdf"
    #doc_pathname = "datasrc/test/raw_docs/业绩案例、上汽内外饰部CAD外包框架服务合同.pdf"
    #doc_pathname = "datasrc/test/raw_docs/业绩案例、比亚迪SJ项目低压线束设计技术服务合同（电子电器）.pdf"
    #doc_pathname = "datasrc/test/raw_docs/业绩案例、比亚迪ST2H项目低压线束设计技术服务合同（电子电器）.pdf"
    #doc_pathname = "datasrc/test/raw_docs/业绩案例、比亚迪车架总成技术服务合同.pdf"
    #doc_pathname = "datasrc/test/raw_docs/业绩案例、比亚迪铝大梁式车架及副车架设计外包中标通知书.pdf"
    #doc_pathname = "datasrc/test/raw_docs/业绩案例、比亚迪驻场线束设计技术服务合同（电子电器）.pdf"
    #doc_pathname = "datasrc/test/raw_docs/1. 座椅STO间隙 P1.pptx"
    #doc_pathname = "datasrc/exam/raw_docs/2. 座垫与钢丝间隙 P1.pptx"
    #doc_pathname = "datasrc/exam/raw_docs/3. 头枕杆圆角定义 P1.pptx"
    #doc_pathname = "datasrc/exam/raw_docs/4. 前后排座椅间距定义 P1.pptx"
    #doc_pathname = "datasrc/test/raw_docs/5. back panel 与环境匹配工程校核_P2.pptx"
    #doc_pathname = "datasrc/exam/raw_docs/6. 前后排座椅H点距离要求 P1.pptx"
    #doc_pathname = "datasrc/test/raw_docs/管理者角色定位与认知课程大纲.docx"
    #doc_pathname = "datasrc/test/raw_docs/考勤修改统一规则.xlsx"
    #doc_pathname = "datasrc/test/raw_docs/高效沟通之黄金三角模型课程大纲.docx"

    #doc_pathname = "datasrc/exam/raw_docs/深度学习在视电阻率快速反演中的研究.pdf"
    #doc_pathname = "datasrc/exam/raw_docs/ChatGPT intimates a tantalizing future_compressed.pdf"
    #doc_pathname = "datasrc/exam/raw_docs/Long-Context LLMs Meet RAG_compressed.pdf"
    #doc_pathname = "datasrc/exam/raw_docs/0530-大模型微调培训-VisualGLM.pdf"
    #doc_pathname = "datasrc/exam/raw_docs/ai602-波士顿咨询：银行业生成式AI应用报告（2023）.pdf"
    #doc_pathname = "datasrc/exam/raw_docs/AI未来十年_大模型产业落地的机遇与挑战_大数据研究院.pptx"
    #doc_pathname = "datasrc/exam/raw_docs/YOU ONLY 2409.13695v1.pdf"
    #doc_pathname = "datasrc/exam/raw_docs/LongRAG.pdf"
    #doc_pathname = "datasrc/exam/raw_docs/DIFFERENTIAL TRANSFORMER 2410.05258v1.pdf"

    out_dir = None
    mdcontrols = None
    enforced_gen = False   

    final_md_path = do_content2md_convert(doc_pathname, out_dir=out_dir, enforced_gen=enforced_gen,  mdcontrols=mdcontrols)
    print(final_md_path)

    md_info = MdInfo(final_md_path)
    rich.print(md_info)
    print(final_md_path)