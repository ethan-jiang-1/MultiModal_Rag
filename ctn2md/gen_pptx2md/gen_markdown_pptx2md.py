import logging
from dotenv import load_dotenv
load_dotenv()

from ctn2md.src.md_info_base import MdInfo, MIFN, FHL_QUALITY_TYPE

def generate_markdown_pptx2md(md_info:MdInfo) -> str:
    logging.info(f"##MDFLOW##: gen_md_pptx2md started...")

    #out_dir = md_info.get_out_dir()
    md_info.set_gen_engine("pptx2md")
    md_info[MIFN.FHL_QUALITY] = FHL_QUALITY_TYPE.MEDIUM


    md_info.save()

    md_info_path = md_info.get_md_info_path()

    logging.info(f"##MDFLOW##: gen_md_pptx2md end")
    return md_info_path
