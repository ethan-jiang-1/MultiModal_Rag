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
from ctn2md.src.md_info_base import MdInfo, MIFN, FHL_QUALITY_TYPE
from ctn2md.utils.util_ctn_type import CTN_TYPE
from ctn2md.src.ctn2md_gen_md_base import GenMd_Base

def _gen_md_lvlm(doc_pathname, out_dir, lvlm_model="gpt-4o"):
    from ctn2md.gen_lvlm.gen_markdown_lvml import generate_markdown_lvlm
    logging.info(f"##MDFLOW##: gen_md_lvlm started...")

    md_info = MdInfo(out_dir)
    md_info.set_gen_engine(f"lvlm@{lvlm_model}")
    md_info.set_doc_pathname(doc_pathname)
    md_info[MIFN.FHL_QUALITY] = FHL_QUALITY_TYPE.HIGH
    
    md_info.save()

    md_info_path = generate_markdown_lvlm(md_info, lvlm_model=lvlm_model)

    logging.info(f"##MDFLOW##: gen_md_lvlm end")
    return md_info_path


class GenMd_Lvlm(GenMd_Base):
    SUPPORT_CNT_TYPES = [CTN_TYPE.PDF, CTN_TYPE.DOC]
    OD_SUFFIX = "lvlm"


    @classmethod
    def does_gen_needed(cls, doc_pathname, out_dir, enforced_gen):
        md_info, gen_needed = GenMd_Base.does_gen_needed(doc_pathname, out_dir, enforced_gen)
        mctl_lvlm_repair_pages = md_info.get_md_control("mctl_lvlm_repair_pages", [])
        if len(mctl_lvlm_repair_pages) != 0:
            gen_needed = True
        if not cls.if_all_md_pages_exist(md_info):
            gen_needed = True
        return md_info, gen_needed

    @classmethod
    def generate_markdown(cls,
                          doc_pathname, 
                          out_dir=None, 
                          enforced_gen=False, 
                          mdcontrols=None):
        if not cls.does_support_doc_type(doc_pathname):
            raise ValueError(f"GenMd_Lvlm does not support '{doc_pathname}'")

        md_info, gen_needed = cls.does_gen_needed(doc_pathname, out_dir, enforced_gen)

        if isinstance(mdcontrols, dict):
            md_info.update_mdcontrols(mdcontrols)
            md_info.save()

        if gen_needed:
            md_info_path = _gen_md_lvlm(doc_pathname, out_dir)
            if md_info_path is None:
                return None
        return md_info.get_md_info_path()


if __name__ == "__main__":
    doc_pathname = "datasrc/exam/raw_docs/papers/ “AI+应用”百花齐放，新质生产力前景广阔pdf.pdf"

    out_dir = MdInfo.get_suggested_out_dir(doc_pathname, suffix=GenMd_Lvlm.OD_SUFFIX)

    setup_logger_handlers()
    os.makedirs(out_dir, exist_ok=True)
    md_info_path = GenMd_Lvlm.generate_markdown(doc_pathname, out_dir=out_dir)
    print(md_info_path)

    md_info = MdInfo(md_info_path)
    rich.print(md_info)
    print(md_info_path)