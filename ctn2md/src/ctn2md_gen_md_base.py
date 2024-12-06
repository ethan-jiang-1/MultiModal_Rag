from dotenv import load_dotenv
import os
import sys
#import logging
#import rich
#import random
#import re
#import shutil

load_dotenv()

if "./" not in sys.path:
    sys.path.append("./")

#from ctn2md.utils.util_logging import setup_logger_handlers
from ctn2md.src.md_info_base import MdInfo
from ctn2md.utils.util_ctn_type import CTN_TYPE


class GenMd_Base:
    _supported_cnt_types = []

    @classmethod
    def does_gen_needed(cls, doc_pathname, out_dir, enforced_gen):
        if out_dir is not None:
            out_dir = MdInfo.get_suggested_out_dir(doc_pathname)
        md_info = MdInfo(out_dir)

        #md_info_path = None
        gen_needed = False
        if not enforced_gen:
            #md_info_path = md_info.get_md_info_path()
            pathname_s0_md = md_info.name_step_pathname(0)
            if (pathname_s0_md is None) or (not os.path.exists(pathname_s0_md)):
                gen_needed = True
        else:
            gen_needed = True
        return md_info, gen_needed

    @classmethod
    def does_support_doc_type(cls, doc_pathname):
        ctn_type = CTN_TYPE.get_ctn_type_by_doc_pathname(doc_pathname)
        if ctn_type in cls._supported_cnt_types:
            return True
        return False

    @classmethod
    def need_followup_step(cls, step_name):
        if step_name == "fix_headings_plc_by_gpt":
            return True 
        return True