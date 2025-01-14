from typing import Callable, Tuple
from dotenv import load_dotenv
import os
import rich

load_dotenv()

from ctn2md.md_info.md_info_ctrl import ENV_MODEL_FLOW, ENV_MODEL_GEN_LP, ENV_MODEL_GEN_LVLM, ENV_MODEL_GEN_TI
from ctn2md.utils.util_ctn_type import CTN_TYPE
from ctn2md.src_gen._ctn2md_gen_md_base import GenMd_Base
from ctn2md.md_info.md_info_base import MdInfo
from ctn2md.utils.util_file import normalize_path

def select_converter_func(doc_pathname:str) -> Tuple[Callable, GenMd_Base]:
    ctn_type = CTN_TYPE.get_ctn_type_by_doc_pathname(doc_pathname)
    if ctn_type == CTN_TYPE.PDF:
        from ctn2md.converters.converter_pdf_lvlm import do_content2md_convert, GenMd_Lvlm
        return do_content2md_convert, GenMd_Lvlm
    elif ctn_type == CTN_TYPE.DOC:
        from ctn2md.converters.converter_all_markitdown import do_content2md_convert, GenMd_Markitdown
        return do_content2md_convert, GenMd_Markitdown
    elif ctn_type == CTN_TYPE.XLS:
        from ctn2md.converters.converter_all_markitdown import do_content2md_convert, GenMd_Markitdown
        return do_content2md_convert, GenMd_Markitdown
    elif ctn_type == CTN_TYPE.PPT:
        from ctn2md.converters.converter_ppt_pptx2md import do_content2md_convert, GenMd_Pptx2md
        return do_content2md_convert, GenMd_Pptx2md
    elif ctn_type == CTN_TYPE.MD:
        from ctn2md.converters.converter_md_plain import do_content2md_convert, GenMd_Plain
        return do_content2md_convert, GenMd_Plain
    else:
        from ctn2md.src_gen.ctn2md_gen_md_llamaparse import GenMd_LlamaParse
        if GenMd_LlamaParse.does_support_doc_type(doc_pathname):
            from ctn2md.converters.converter_all_llamaparse import do_content2md_convert, GenMd_LlamaParse
            return do_content2md_convert, GenMd_LlamaParse
        else:
            raise ValueError(f"Unsupported content type: {ctn_type}")
        
def convert_document(doc_pathname:str):
    os.environ[ENV_MODEL_FLOW] = "qwen"
    os.environ[ENV_MODEL_GEN_LP] = "qwen"
    os.environ[ENV_MODEL_GEN_LVLM] = "qwen"
    os.environ[ENV_MODEL_GEN_TI] = "qwen"

    doc_pathname = normalize_path(doc_pathname)
    cvt_func, gen_md_base = select_converter_func(doc_pathname)
    rich.print(cvt_func)
    rich.print(gen_md_base)

    out_dir = MdInfo.get_suggested_out_dir(doc_pathname, suffix=gen_md_base.get_out_dir_suffix())
    out_dir = normalize_path(out_dir)
    os.makedirs(out_dir, exist_ok=True)
    return cvt_func(doc_pathname, out_dir=out_dir)

if __name__ == "__main__":
    from mmbase.utils.util_logging import setup_logger_handlers
    setup_logger_handlers()

    #doc_pathname = "datasrc/exam/raw_docs/mrag/AIGC时代的人力资源管理进化(徐刚).pdf"
    #doc_pathname = "datasrc/exam/raw_docs/mrag/AIGC时代的人力资源管理进化(徐刚).pdf"
    #doc_pathname = "datasrc/exam/raw_docs/mrag/业绩案例、上汽内外饰DRE外包框架服务合同.pdf"
    #doc_pathname = "datasrc/exam/raw_docs/mrag/业绩案例、上汽内外饰部CAD外包框架服务合同.pdf"
    #doc_pathname = "datasrc/exam/raw_docs/mrag/业绩案例、比亚迪SJ项目低压线束设计技术服务合同（电子电器）.pdf"
    #doc_pathname = "datasrc/exam/raw_docs/mrag/业绩案例、比亚迪ST2H项目低压线束设计技术服务合同（电子电器）.pdf"
    #doc_pathname = "datasrc/exam/raw_docs/mrag/业绩案例、比亚迪车架总成技术服务合同.pdf"
    #doc_pathname = "datasrc/exam/raw_docs/mrag/业绩案例、比亚迪铝大梁式车架及副车架设计外包中标通知书.pdf"
    #doc_pathname = "datasrc/exam/raw_docs/mrag/业绩案例、比亚迪驻场线束设计技术服务合同（电子电器）.pdf"
    #doc_pathname = "datasrc/exam/raw_docs/mrag/1. 座椅STO间隙 P1.pptx"
    #doc_pathname = "datasrc/exam/raw_docs/mrag/2. 座垫与钢丝间隙 P1.pptx"
    #doc_pathname = "datasrc/exam/raw_docs/mrag/3. 头枕杆圆角定义 P1.pptx"
    #doc_pathname = "datasrc/exam/raw_docs/mrag/4. 前后排座椅间距定义 P1.pptx"
    doc_pathname = "datasrc/exam/raw_docs/mrag/5. back panel 与环境匹配工程校核_P2.pptx"
    #doc_pathname = "datasrc/exam/raw_docs/mrag/6. 前后排座椅H点距离要求 P1.pptx"
    #doc_pathname = "datasrc/exam/raw_docs/mrag/管理者角色定位与认知课程大纲.docx"
    #doc_pathname = "datasrc/exam/raw_docs/mrag/考勤修改统一规则.xlsx"
    #doc_pathname = "datasrc/exam/raw_docs/mrag/高效沟通之黄金三角模型课程大纲.docx"

    #doc_pathname = "datasrc/exam/raw_docs/papers/深度学习在视电阻率快速反演中的研究.pdf"
    #doc_pathname = "datasrc/exam/raw_docs/papers/ChatGPT intimates a tantalizing future_compressed.pdf"
    #doc_pathname = "datasrc/exam/raw_docs/papers/Long-Context LLMs Meet RAG_compressed.pdf"
    #doc_pathname = "datasrc/exam/raw_docs/papers/YOU ONLY 2409.13695v1.pdf"
    #doc_pathname = "datasrc/exam/raw_docs/papers/LongRAG.pdf"
    #doc_pathname = "datasrc/exam/raw_docs/papers/DIFFERENTIAL TRANSFORMER 2410.05258v1.pdf"
    #doc_pathname = "datasrc/exam/raw_docs/papers/Winning Solution For Meta KDD Cup’ 24 2410.00005v1.pdf"
    #doc_pathname = "datasrc/exam/raw_docs/papers/Survey of different Large Language Model Architectures.pdf"
    #doc_pathname = "datasrc/exam/raw_docs/papers/A Coin Has Two Sides.pdf"
    #doc_pathname = "datasrc/exam/raw_docs/papers/attention_is_all_you_need.pdf"

    #doc_pathname = "datasrc/exam/raw_docs/misc/0530-大模型微调培训-VisualGLM.pdf"
    #doc_pathname = "datasrc/exam/raw_docs/misc/ai602-波士顿咨询：银行业生成式AI应用报告（2023）.pdf"
    #doc_pathname = "datasrc/exam/raw_docs/misc/AI未来十年_大模型产业落地的机遇与挑战_大数据研究院.pptx"


    ret = convert_document(doc_pathname)
    rich.print(ret)