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
from ctn2md.src.md_info_ctrl import ENV_MODEL_FLOW, ENV_MODEL_GEN_TI
from ctn2md.src.ctn2md_fix_heading_plc import fix_headings_plc_by_llm
from ctn2md.src.ctn2md_inject_section_hierarchy import inject_section_hierarchy
from ctn2md.src.ctn2md_summarize_content import summarize_content_by_llm
from ctn2md.src.make_final_result import make_final_json
from ctn2md.src_gen.ctn2md_gen_md_textin import GenMd_TextIn

def _do_content2md_convert_core_ti(doc_pathname:str, 
                                   out_dir:Optional[str] = None, 
                                   enforced_gen:bool = False, 
                                   mdcontrols:Optional[dict] = None)->str:
    if out_dir is None:
        out_dir = MdInfo.get_suggested_out_dir(doc_pathname, suffix=GenMd_TextIn.OD_SUFFIX)
    logging.warning(f"DCCCTI: work out_dir: {out_dir} for {doc_pathname}")
    os.makedirs(out_dir, exist_ok=True)

    md_generator = GenMd_TextIn
    if md_generator is None:
        logging.error("")
        return None 

    md_info_path = md_generator.generate_markdown(doc_pathname, out_dir=out_dir, enforced_gen=enforced_gen, mdcontrols=mdcontrols)
    if md_info_path is None:
        logging.error(f"DCCCTI: failed {md_info_path} @initial_gen_md_by_textin")
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
        logging.error(f"DCCCTI: failed {md_info_path} @inject_section_hierarchy")
        return None

    src_step_num += 1
    md_info_path = summarize_content_by_llm(md_info_path, src_step_num=src_step_num)
    if md_info_path is None:
        logging.error(f"DCCCTI: failed {md_info_path} @summarize_content_by_llm")
        return None       

    pathname_final_json = make_final_json(md_info_path)
    logging.info(f"DCCCTI: final json: {pathname_final_json}")
    return pathname_final_json

def do_content2md_convert(doc_pathname:str, out_dir:str = None, enforced_gen:bool = False, mdcontrols: dict = None):
    pathname_final_json = None
    try:
        pathname_final_json = _do_content2md_convert_core_ti(doc_pathname,
                                                    out_dir=out_dir,
                                                    enforced_gen=enforced_gen,
                                                    mdcontrols=mdcontrols)
    except Exception as ex:
        logging.exception(ex)
        raise ex
    return pathname_final_json

if __name__ == "__main__":
    setup_logger_handlers()

    #doc_pathname = "datasrc/exam/raw_docs/mrag/AIGC时代的人力资源管理进化(徐刚).pdf"
    #doc_pathname = "datasrc/exam/raw_docs/mrag/业绩案例、上汽内外饰DRE外包框架服务合同.pdf"
    #doc_pathname = "datasrc/exam/raw_docs/mrag/业绩案例、上汽内外饰部CAD外包框架服务合同.pdf"
    doc_pathname = "datasrc/exam/raw_docs/mrag/业绩案例、比亚迪SJ项目低压线束设计技术服务合同（电子电器）.pdf"
    #doc_pathname = "datasrc/exam/raw_docs/mrag/业绩案例、比亚迪ST2H项目低压线束设计技术服务合同（电子电器）.pdf"
    #doc_pathname = "datasrc/exam/raw_docs/mrag/业绩案例、比亚迪车架总成技术服务合同.pdf"
    #doc_pathname = "datasrc/exam/raw_docs/mrag/业绩案例、比亚迪铝大梁式车架及副车架设计外包中标通知书.pdf"
    #doc_pathname = "datasrc/exam/raw_docs/mrag/业绩案例、比亚迪驻场线束设计技术服务合同（电子电器）.pdf"

    #doc_pathname = "datasrc/exam/raw_docs/papers/ “AI+应用”百花齐放，新质生产力前景广阔pdf.pdf"
    #doc_pathname = "datasrc/exam/raw_docs/papers/attention_is_all_you_need.pdf"
    #doc_pathname = "datasrc/exam/raw_docs/papers/Survey of different Large Language Model Architectures.pdf"
    #doc_pathname = "datasrc/exam/raw_docs/papers/Winning Solution For Meta KDD Cup’ 24 2410.00005v1.pdf"
    #doc_pathname = "datasrc/exam/raw_docs/papers/深度学习在视电阻率快速反演中的研究.pdf"
    #doc_pathname = "datasrc/exam/raw_docs/papers/DeepSeek_V3.pdf"
    #doc_pathname = "datasrc/exam/raw_docs/papers/Long-Context LLMs Meet RAG_compressed.pdf"

    #doc_pathname = "datasrc/exam/raw_docs/papers/ChatGPT intimates a tantalizing future_compressed.pdf"
    #doc_pathname = "datasrc/exam/raw_docs/papers/YOU ONLY 2409.13695v1.pdf"
    #doc_pathname = "datasrc/exam/raw_docs/papers/LongRAG.pdf"
    #doc_pathname = "datasrc/exam/raw_docs/papers/DIFFERENTIAL TRANSFORMER 2410.05258v1.pdf"
    #doc_pathname = "datasrc/exam/raw_docs/papers/A Coin Has Two Sides.pdf"

    #doc_pathname = "datasrc/exam/raw_docs/misc/0530-大模型微调培训-VisualGLM.pdf"
    #doc_pathname = "datasrc/exam/raw_docs/misc/ai602-波士顿咨询：银行业生成式AI应用报告（2023）.pdf"
    #doc_pathname = "datasrc/exam/raw_docs/misc/AI未来十年_大模型产业落地的机遇与挑战_大数据研究院.pptx"
    #doc_pathname = "datasrc/exam/raw_docs/misc/2024年 AI Agent行业报告-20240430-V8.pdf"
    #doc_pathname = "datasrc/exam/raw_docs/misc/202501-2024年中国AI创业者人群画像报告.pdf"

    #doc_pathname = "datasrc/exam/raw_docs/kmp/Regioselective hydroxylation of cholecalciferol.pdf"
    #doc_pathname = "datasrc/exam/raw_docs/kmp/3_20240131104523599_rearranged.pdf"
    #doc_pathname = "datasrc/exam/raw_docs/kmp/tianyang_1_20.pdf"

    #os.environ[ENV_MODEL_FLOW] = "ark"
    #os.environ[ENV_MODEL_GEN_TI] = "ark"
    os.environ[ENV_MODEL_FLOW] = "qwen"
    os.environ[ENV_MODEL_GEN_TI] = "qwen"
    mdcontrols = None

    out_dir = None
    enforced_gen = False 

    pathname_final_json = do_content2md_convert(doc_pathname, out_dir=out_dir, enforced_gen=enforced_gen,  mdcontrols=mdcontrols)
    print(pathname_final_json)

    md_info = MdInfo(pathname_final_json)
    rich.print(md_info)
    print(pathname_final_json)