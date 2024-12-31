from typing import Optional, Tuple
from dotenv import load_dotenv
import os
import sys
import logging
import rich

load_dotenv()

if "./" not in sys.path:
    sys.path.append("./")

from ctn2md.utils.util_logging import setup_logger_handlers
from ctn2md.src.md_info_base import MdInfo, MIFN, FHL_QUALITY_TYPE
from ctn2md.utils.util_ctn_type import CTN_TYPE
from ctn2md.src.ctn2md_gen_md_base import GenMd_Base


def gen_md_textin(doc_pathname:str, out_dir:str) -> str:
    from ctn2md.gen_ti.gen_markdown_textin import generate_markdown_textin
    logging.info(f"##MDFLOW##: gen_md_textin started...")

    md_info = MdInfo(out_dir)
    md_info.set_gen_engine(f"textin:ocr")
    md_info.set_doc_pathname(doc_pathname)
    md_info[MIFN.FHL_QUALITY] = FHL_QUALITY_TYPE.HIGH

    md_info_path = generate_markdown_textin(md_info)

    logging.info(f"##MDFLOW##: gen_md_textin end")
    return md_info_path


class GenMd_TextIn(GenMd_Base):
    SUPPORT_CNT_TYPES = [CTN_TYPE.PDF, CTN_TYPE.PPT, CTN_TYPE.DOC]
    OD_SUFFIX = "ti"

    @classmethod
    def does_gen_needed(cls, doc_pathname:str, out_dir:str, enforced_gen:bool) -> Tuple[MdInfo, bool]:
        md_info, gen_needed = GenMd_Base.does_gen_needed(doc_pathname, out_dir, enforced_gen)
        if not cls.if_all_md_pages_exist(md_info):
            gen_needed = True
        if cls.if_any_md_page_has_error(md_info):
            gen_needed = True
        if cls.is_final_md_info_outdated(md_info):
            gen_needed = True
        if cls.if_any_md_page_touched(md_info):
            gen_needed = True    
        return md_info, gen_needed
    
    @classmethod
    def if_any_md_page_has_error(cls, md_info:MdInfo) -> bool:
        from ctn2md.src.md_page_spe import SpecialPage 
        fnames_pages = md_info.get_fnames_pages()
        if isinstance(fnames_pages, list):
            out_dir = md_info.get_out_dir()
            for fname in fnames_pages:
                pname = os.path.join(out_dir, fname)
                if SpecialPage.does_page_have_failed_mark(pname):
                    logging.warning(f"page {pname} has error")
                    return True
        return False

    @classmethod
    def generate_markdown(cls,
                          doc_pathname:str, 
                          out_dir:str = None, 
                          enforced_gen: bool = False, 
                          mdcontrols:Optional[dict] = None) -> str:
        if not cls.does_support_doc_type(doc_pathname):
            raise ValueError(f"GenMd_TextIn does not support '{doc_pathname}'")

        md_info, gen_needed = cls.does_gen_needed(doc_pathname, out_dir, enforced_gen)

        if isinstance(mdcontrols, dict):
            md_info.update_mdcontrols(mdcontrols)
            md_info.save()

        if gen_needed:
            md_info_path = gen_md_textin(doc_pathname, out_dir)
            if md_info_path is None:
                return None

        return md_info.get_md_info_path()


if __name__ == "__main__":
    doc_pathname = "datasrc/exam/raw_docs/papers/ “AI+应用”百花齐放，新质生产力前景广阔pdf.pdf"

    out_dir = MdInfo.get_suggested_out_dir(doc_pathname, suffix=GenMd_TextIn.OD_SUFFIX)

    setup_logger_handlers()
    os.makedirs(out_dir, exist_ok=True)
    md_info_path = gen_md_textin(doc_pathname, out_dir)
    print(md_info_path)

    md_info = MdInfo(md_info_path)
    rich.print(md_info)
    print(md_info_path)