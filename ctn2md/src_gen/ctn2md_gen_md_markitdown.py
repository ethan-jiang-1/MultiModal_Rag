from typing import Optional, Tuple
from dotenv import load_dotenv
import os
import logging
import rich

load_dotenv()

#from ctn2md.src.md_page_spe import SpecialPage
from mmbase.utils.util_logging import setup_logger_handlers
from ctn2md.src.md_info_base import MdInfo, MIFN, FHL_QUALITY_TYPE
from ctn2md.utils.util_ctn_type import CTN_TYPE
from ctn2md.src_gen._ctn2md_gen_md_base import GenMd_Base

class GenMd_Markitdown(GenMd_Base):
    SUPPORT_CNT_TYPES = [CTN_TYPE.DOC, CTN_TYPE.PDF, CTN_TYPE.PPT, CTN_TYPE.XLS]
    OD_SUFFIX = "mid"

    @classmethod
    def does_gen_needed(cls, doc_pathname:str, out_dir:str, enforced_gen:bool) -> Tuple[MdInfo, bool]:
        md_info, gen_needed = GenMd_Base.does_gen_needed(doc_pathname, out_dir, enforced_gen)
        if not gen_needed:
            if not cls.if_all_md_pages_processed(md_info):
                gen_needed = True
            if cls.is_final_md_info_outdated(md_info):
                gen_needed = True  
        return md_info, gen_needed

    @classmethod
    def generate_markdown(cls,
                          doc_pathname:str, 
                          out_dir:str = None, 
                          enforced_gen: bool = False, 
                          mdcontrols:Optional[dict] = None) -> str:
        if not cls.does_support_doc_type(doc_pathname):
            raise ValueError(f"GenMd_Pptx2md does not support '{doc_pathname}'")

        md_info, gen_needed = cls.does_gen_needed(doc_pathname, out_dir, enforced_gen)

        if isinstance(mdcontrols, dict):
            md_info.update_mdcontrols(mdcontrols)
            md_info.save()

        if gen_needed:
            md_info_path = cls._gen_md_core(doc_pathname, out_dir)
            if md_info_path is None:
                return None

        return md_info.get_md_info_path()

    @classmethod
    def need_followup_step(cls, step_name:str, doc_pathname:str) -> bool:
        if step_name == "fix_headings_plc_by_llm":
            ctn_type = CTN_TYPE.get_ctn_type_by_doc_pathname(doc_pathname)
            if ctn_type == CTN_TYPE.XLS:
                return False 
        return True
    
    @classmethod
    def _gen_md_core(cls, doc_pathname:str, out_dir:str) -> str:
        from ctn2md.gen_markitdown.gen_markdown_markitdown import generate_markdown_markitdown
        logging.info(f"##MDFLOW##: gen_md_markitdown started...")

        md_info = MdInfo(out_dir)
        md_info.set_gen_engine(f"pptx2md")
        md_info.set_doc_pathname(doc_pathname)
        md_info[MIFN.FHL_QUALITY] = FHL_QUALITY_TYPE.HIGH

        md_info_path = generate_markdown_markitdown(md_info)

        logging.info(f"##MDFLOW##: gen_md_markitdown")
        return md_info_path


if __name__ == "__main__":
    #doc_pathname = "datasrc/exam/raw_docs/mrag/1. 座椅STO间隙 P1.pptx"
    doc_pathname = "datasrc/exam/raw_docs/mrag/主管培训课程清单.xlsx"

    out_dir = MdInfo.get_suggested_out_dir(doc_pathname, suffix=GenMd_Markitdown.OD_SUFFIX)

    setup_logger_handlers()
    os.makedirs(out_dir, exist_ok=True)
    md_info_path = GenMd_Markitdown._gen_md_core(doc_pathname, out_dir)
    print(md_info_path)

    md_info = MdInfo(md_info_path)
    rich.print(md_info)
    print(md_info_path)