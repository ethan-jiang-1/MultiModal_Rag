import logging  
import os
from dotenv import load_dotenv
load_dotenv()

from ctn2md.utils.util_ctn_type import CTN_TYPE
from ctn2md.src.md_info_base import MdInfo, MIFN, FHL_QUALITY_TYPE
from mmbase.utils.util_logging import setup_logger_handlers
import rich


def gen_pages_markitdown(md_info:MdInfo):
    out_path = md_info.name_step_pathname(0)
    ctn_type = md_info.get_ctn_type()    
    if ctn_type == CTN_TYPE.DOC:
        from ctn2md.gen_markitdown.doc2md._gen_md_from_doc import gen_md_from_doc
        out_path = gen_md_from_doc(md_info)
    elif ctn_type == CTN_TYPE.XLS:
        from ctn2md.gen_markitdown.xls2md._gen_md_from_xls import gen_md_from_xls
        out_path = gen_md_from_xls(md_info)
    else:
        raise ValueError(f"unsupported ctn_type yet: {ctn_type}")

    return out_path

def generate_markdown_markitdown(md_info:MdInfo) -> str:
    logging.info(f"##MDFLOW##: gen_md_markitdown started...")
    doc_pathname = md_info.get_doc_pathname()
    if (doc_pathname is None) or (not os.path.isfile(doc_pathname)):
        raise ValueError(f"doc_pathname is not valid {doc_pathname}")

    out_dir = md_info.get_out_dir()
    os.makedirs(out_dir, exist_ok=True)

    gen_pages_markitdown(md_info)

    #out_dir = md_info.get_out_dir()
    md_info.set_gen_engine("markitdown")
    md_info[MIFN.FHL_QUALITY] = FHL_QUALITY_TYPE.MEDIUM

    pathname_step0 = md_info.name_step_pathname(0) # _construct_s0_md_from_pages(md_info)
    md_info.add_step_into_md_info_mdflow(pathname_step0, actor=f"generate_markdown_markitdown")

    logging.info(f"original doc: {doc_pathname}")
    logging.info(f"fname_output: {os.path.basename(pathname_step0)}")
    
    md_info.save()

    md_info_path = md_info.get_md_info_path()

    logging.info(f"##MDFLOW##: gen_md_markitdown end")
    return md_info_path


if __name__ == "__main__":
    setup_logger_handlers()

    #md_info_path = "_output/ctn2md_mrag__1__座椅STO间隙_P1_px2m/_info.json"
    #md_info_path = "_output/ctn2md_misc__成都交通局_华为说明_mid/_info.json"
    #md_info_path = "_output/ctn2md_mrag__业绩案例_比亚迪SJ项目低压线束设计技术服务合同_mid/_info.json"
    md_info_path = "_output/ctn2md_mrag__主管培训课程清单_mid/_info.json"

    md_info = MdInfo(md_info_path)

    ret = generate_markdown_markitdown(md_info)
    rich.print(ret)