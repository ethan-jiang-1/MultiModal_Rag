from typing import Tuple, Optional
from dotenv import load_dotenv
import os
import logging


load_dotenv()

#from mmbase.utils.util_logging import setup_logger_handlers
from ctn2md.src.md_info_base import MdInfo
from ctn2md.src.md_page_spe import SpecialPage
from ctn2md.utils.util_ctn_type import CTN_TYPE


class GenMd_Base:
    SUPPORT_CNT_TYPES = []
    OD_SUFFIX = ""

    @classmethod
    def get_out_dir_suffix(cls) -> str:
        return cls.OD_SUFFIX
    
    @classmethod
    def does_gen_needed(cls, doc_pathname:str, out_dir:Optional[str], enforced_gen:bool) -> Tuple[MdInfo, bool]:
        if out_dir is None:
            out_dir = MdInfo.get_suggested_out_dir(doc_pathname, suffix=cls.OD_SUFFIX)

        gen_needed = False
        md_info = None

        if enforced_gen:
            # 如果强制生成，则需要生成 
            gen_needed = True 
        else:
            pname_md_info = os.path.join(out_dir, MdInfo.get_fname_md_info())
            if not os.path.isfile(pname_md_info):
                # 如果 md_info 文件不存在，则需要生成 
                gen_needed = True
            else:
                # 如果 pathname_s0_md 文件不存在，则要生成 
                md_info = MdInfo(out_dir)
                pathname_s0_md = md_info.name_step_pathname(0)
                if (pathname_s0_md is None) or (not os.path.exists(pathname_s0_md)):
                    gen_needed = True

        if md_info is None:
            md_info = MdInfo(out_dir)
        return md_info, gen_needed
    
    @classmethod
    def if_all_md_pages_processed(cls, md_info:MdInfo) -> bool:
        fnames_pages = md_info.get_fnames_pages()
        if isinstance(fnames_pages, list):
            if len(fnames_pages) == 0:
                return False 

            out_dir = md_info.get_out_dir()
            for fname in fnames_pages:
                pname = os.path.join(out_dir, fname)
                if cls.is_md_page_completed(pname):
                    logging.warning(f"page {pname} does not exist")
                    return False
        else:
            raise ValueError("fnames_pages ?!") 
        return True
    
    @classmethod
    def is_md_page_completed(cls, pname_md_page:str) -> bool:
        return os.path.isfile(pname_md_page)
    
    @classmethod
    def is_final_md_info_outdated(cls, md_info: MdInfo) -> bool:
        # 获取最终 JSON 文件的路径
        out_dir = md_info.get_out_dir()
        pname_final_info = os.path.join(out_dir, md_info.get_fname_final_json())
        
        # 检查 pname_final_info 文件是否存在
        if not os.path.isfile(pname_final_info):
            logging.info(f"Final JSON file '{pname_final_info}' does not exist.")
            return True
        
        # 获取 pname_final_info 的修改时间
        final_info_mtime = os.path.getmtime(pname_final_info)

        # 获取页面文件名列表
        fnames_pages = md_info.get_fnames_pages()
        if not isinstance(fnames_pages, list):
            logging.error("fnames_pages is not a valid list.")
            return True

        # 遍历页面文件并检查是否有文件修改时间更新
        for fname in fnames_pages:
            pname = os.path.join(out_dir, fname)

            # 检查文件是否存在
            if not os.path.isfile(pname):
                logging.warning(f"Page file '{pname}' does not exist.")
                return True
            
            # 获取文件的修改时间
            page_mtime = os.path.getmtime(pname)
            
            # 如果页面文件的修改时间比最终 JSON 文件晚，则说明有改动
            if page_mtime > final_info_mtime:
                logging.info(f"Page file '{pname}' is newer than final JSON file '{pname_final_info}'.")
                return True

        # 如果没有任何页面文件比最终 JSON 文件更新，则返回 False
        return False
    
    @classmethod
    def if_any_md_page_touched(cls, md_info:MdInfo) -> bool:
        fnames_pages = md_info.get_fnames_pages()
        if isinstance(fnames_pages, list):
            if len(fnames_pages) == 0:
                return False 

            out_dir = md_info.get_out_dir()
            for fname in fnames_pages:
                pname = os.path.join(out_dir, fname)
                if os.path.isfile(pname):
                    if SpecialPage.does_page_have_touched_mark(pname):
                        logging.warning(f"page {pname} has tourched")
                        return True
        return False

    @classmethod
    def migrate_md_info(cls, md_info:MdInfo):
        return 

    @classmethod
    def does_support_doc_type(cls, doc_pathname:str) -> bool:
        ctn_type = CTN_TYPE.get_ctn_type_by_doc_pathname(doc_pathname)
        if ctn_type in cls.SUPPORT_CNT_TYPES:
            return True
        return False

    @classmethod
    def need_followup_step(cls, step_name:str, doc_pathname:str) -> bool:
        if step_name == "fix_headings_plc_by_llm":
            return True 
        return True