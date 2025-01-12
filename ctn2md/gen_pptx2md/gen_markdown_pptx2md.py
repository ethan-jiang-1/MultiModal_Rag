import logging  
import os
import shutil
from dotenv import load_dotenv
load_dotenv()

from ctn2md.src.md_info_base import MdInfo, MIFN, FHL_QUALITY_TYPE
from mmbase.utils.util_logging import setup_logger_handlers
import rich

def gen_pages_pptx2md(md_info:MdInfo):
    from pptx2md import convert, ConversionConfig
    from pathlib import Path

    unique_id = md_info.get_unique_job_id()
    dst_pathname = os.path.join(md_info.get_out_dir(), f"{unique_id}.pptx")
    src_pathname = md_info.get_doc_pathname()
    shutil.copy(src_pathname, dst_pathname)

    pptx_path = Path(dst_pathname)
    #out_dir = Path(md_info.get_out_dir())
    img_dir = Path(md_info.get_out_dir())

    out_path = md_info.name_step_pathname(0)

    cfg = ConversionConfig(
            pptx_path=pptx_path,
            output_path=out_path,
            image_dir=img_dir,
            disable_notes=True,
            disable_color=True,
        )
    # Basic usage
    ret = convert(cfg)
    rich.print(ret)
    return ret

def generate_markdown_pptx2md(md_info:MdInfo) -> str:
    logging.info(f"##MDFLOW##: gen_md_pptx2md started...")
    doc_pathname = md_info.get_doc_pathname()
    if (doc_pathname is None) or (not os.path.isfile(doc_pathname)):
        raise ValueError(f"doc_pathname is not valid {doc_pathname}")

    out_dir = md_info.get_out_dir()
    os.makedirs(out_dir, exist_ok=True)

    gen_pages_pptx2md(md_info)

    #out_dir = md_info.get_out_dir()
    md_info.set_gen_engine("pptx2md")
    md_info[MIFN.FHL_QUALITY] = FHL_QUALITY_TYPE.MEDIUM

    pathname_step0 = md_info.name_step_pathname(0) # _construct_s0_md_from_pages(md_info)
    md_info.add_step_into_md_info_mdflow(pathname_step0, actor=f"generate_markdown_pptx2md")

    logging.info(f"original doc: {doc_pathname}")
    logging.info(f"fname_output: {os.path.basename(pathname_step0)}")
    
    md_info.save()

    md_info_path = md_info.get_md_info_path()

    logging.info(f"##MDFLOW##: gen_md_pptx2md end")
    return md_info_path


if __name__ == "__main__":
    setup_logger_handlers()

    md_info_path = "_output/ctn2md_mrag__1__座椅STO间隙_P1_px2m/_info.json"

    md_info = MdInfo(md_info_path)

    ret = generate_markdown_pptx2md(md_info)
    rich.print(ret)