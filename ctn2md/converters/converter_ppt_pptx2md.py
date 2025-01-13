from typing import Optional
from dotenv import load_dotenv
import os
import logging
import rich

load_dotenv()

if __name__ == "__main__":
    from dotenv import find_dotenv
    _root_dir = os.path.abspath(os.path.dirname(find_dotenv()))
    os.chdir(_root_dir)

from mmbase.utils.util_logging import setup_logger_handlers
from ctn2md.src.md_info_base import MdInfo
from ctn2md.src.md_info_ctrl import ENV_MODEL_FLOW # , ENV_MODEL_GEN_TI
from ctn2md.src.ctn2md_fix_heading_plc import fix_headings_plc_by_llm
from ctn2md.src.ctn2md_inject_section_hierarchy import inject_section_hierarchy
from ctn2md.src.ctn2md_summarize_content import summarize_content_by_llm
from ctn2md.src.make_final_result import make_final_json
from ctn2md.src_gen.ctn2md_gen_md_pptx2md import GenMd_Pptx2md

def _do_content2md_convert_core_p2m(doc_pathname:str, 
                                   out_dir:Optional[str] = None, 
                                   enforced_gen:bool = False, 
                                   mdcontrols:Optional[dict] = None)->str:
    if out_dir is None:
        out_dir = MdInfo.get_suggested_out_dir(doc_pathname, suffix=GenMd_Pptx2md.OD_SUFFIX)
    logging.warning(f"DCCPPT: work out_dir: {out_dir} for {doc_pathname}")
    os.makedirs(out_dir, exist_ok=True)

    md_generator = GenMd_Pptx2md
    if md_generator is None:
        logging.error("")
        return None 

    md_info_path = md_generator.generate_markdown(doc_pathname, out_dir=out_dir, enforced_gen=enforced_gen, mdcontrols=mdcontrols)
    if md_info_path is None:
        logging.error(f"DCCPPT: failed {md_info_path} @initial_gen_md_by_pptx2md")
        return None

    md_info = MdInfo(md_info_path)
    md_info.reset_md_flow()

    src_step_num = 0
    if md_generator.need_followup_step("fix_headings_plc_by_llm", doc_pathname):
        md_info_path = fix_headings_plc_by_llm(md_info_path, src_step_num=src_step_num)
        if md_info_path is None:
            logging.error(f"DCCCTI: failed {md_info_path} @fix_headings_plc_by_llm")
            return None 
        src_step_num += 1

    md_info_path = inject_section_hierarchy(md_info_path, src_step_num=src_step_num)
    if md_info_path is None:
        logging.error(f"DCCPPT: failed {md_info_path} @inject_section_hierarchy")
        return None

    src_step_num += 1
    md_info_path = summarize_content_by_llm(md_info_path, src_step_num=src_step_num)
    if md_info_path is None:
        logging.error(f"DCCPPT: failed {md_info_path} @summarize_content_by_llm")
        return None       

    pathname_final_json = make_final_json(md_info_path)
    logging.info(f"DCCPPT: final json: {pathname_final_json}")
    return pathname_final_json

def do_content2md_convert(doc_pathname:str, out_dir:str = None, enforced_gen:bool = False, mdcontrols: dict = None):
    pathname_final_json = None
    try:
        pathname_final_json = _do_content2md_convert_core_p2m(doc_pathname,
                                                    out_dir=out_dir,
                                                    enforced_gen=enforced_gen,
                                                    mdcontrols=mdcontrols)
    except Exception as ex:
        logging.exception(ex)
        raise ex
    return pathname_final_json

if __name__ == "__main__":
    setup_logger_handlers()

    #doc_pathname = "datasrc/exam/raw_docs/mrag/1. 座椅STO间隙 P1.pptx"
    #doc_pathname = "datasrc/exam/raw_docs/mrag/2. 座垫与钢丝间隙 P1.pptx"
    #doc_pathname = "datasrc/exam/raw_docs/mrag/3. 头枕杆圆角定义 P1.pptx"
    #doc_pathname = "datasrc/exam/raw_docs/mrag/4. 前后排座椅间距定义 P1.pptx"
    #doc_pathname = "datasrc/exam/raw_docs/mrag/5. back panel 与环境匹配工程校核_P2.pptx"
    #doc_pathname = "datasrc/exam/raw_docs/mrag/6. 前后排座椅H点距离要求 P1.pptx"

    doc_pathname = "datasrc/exam/raw_docs/misc/AI未来十年_大模型产业落地的机遇与挑战_大数据研究院.pptx"

    #os.environ[ENV_MODEL_FLOW] = "ark"
    #os.environ[ENV_MODEL_GEN_TI] = "ark"
    os.environ[ENV_MODEL_FLOW] = "qwen"
    #os.environ[ENV_MODEL_GEN_TI] = "qwen"
    mdcontrols = None

    out_dir = None
    enforced_gen = False 

    pathname_final_json = do_content2md_convert(doc_pathname, out_dir=out_dir, enforced_gen=enforced_gen,  mdcontrols=mdcontrols)
    print(pathname_final_json)

    md_info = MdInfo(pathname_final_json)
    rich.print(md_info)
    print(pathname_final_json)