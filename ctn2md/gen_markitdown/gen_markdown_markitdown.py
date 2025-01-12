import logging  
import os
import shutil
from dotenv import load_dotenv
load_dotenv()

from ctn2md.src.md_info_base import MdInfo, MIFN, FHL_QUALITY_TYPE
from mmbase.utils.util_logging import setup_logger_handlers
import rich

def gen_pages_markitdown(md_info:MdInfo):
    from markitdown import MarkItDown

    md = MarkItDown()

    unique_id = md_info.get_unique_job_id()
    src_pathname = md_info.get_doc_pathname()
    # 获取源文件的后缀名
    _, src_extension = os.path.splitext(src_pathname)
    dst_pathname = os.path.join(md_info.get_out_dir(), f"{unique_id}{src_extension}")
    shutil.copy(src_pathname, dst_pathname)
    
    result = md.convert(dst_pathname)
    print(result.text_content)

    out_path = md_info.name_step_pathname(0)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(result.text_content)
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

    md_info_path = "_output/ctn2md_mrag__1__座椅STO间隙_P1_px2m/_info.json"

    md_info = MdInfo(md_info_path)

    ret = generate_markdown_markitdown(md_info)
    rich.print(ret)