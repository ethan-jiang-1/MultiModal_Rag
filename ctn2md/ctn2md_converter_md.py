from dotenv import load_dotenv
import os
import sys
import logging
import rich
#import random
#import json
#import shutil

load_dotenv()

if "./" not in sys.path:
    sys.path.append("./")

from ctn2md.utils.util_logging import setup_logger_handlers
from ctn2md.src.md_info_base import MdInfo
from ctn2md.src.ctn2md_fix_heading_plc import fix_headings_plc_by_gpt
from ctn2md.src.ctn2md_inject_section_hierarchy import inject_section_heirarchy
from ctn2md.src.ctn2md_summarize_content import summarize_content_by_gpt
from ctn2md.src.make_final_md import make_final_md, reset_md_flow
from ctn2md.src.ctn2md_gen_md_plain import GenMd_Plain

def _do_content2md_convert_core_md(doc_pathname, 
                                   out_dir=None, 
                                   enforced_gen=False, 
                                   mdcontrols=None):
    if out_dir is None:
        out_dir = MdInfo.get_suggested_out_dir(doc_pathname, suffix=GenMd_Plain.od_suffix)
    logging.warning(f"work out_dir: {out_dir}")
    os.makedirs(out_dir, exist_ok=True)

    md_generator = GenMd_Plain
    if md_generator is None:
        logging.error("")
        return None 

    md_info_path = md_generator.generate_markdown(doc_pathname, out_dir=out_dir, enforced_gen=enforced_gen, mdcontrols=mdcontrols)
    if md_info_path is None:
        logging.error(f"DCCCM: failed {md_info_path} @initial_gen_md_by_llamaparse")
        return None

    reset_md_flow(md_info_path)

    src_step_num = 0
    if md_generator.need_followup_step("fix_headings_plc_by_gpt"):
        md_info_path = fix_headings_plc_by_gpt(md_info_path, src_step_num=src_step_num)
        if md_info_path is None:
            logging.error(f"DCCCM: failed {md_info_path} @fix_headings_plc_by_gpt")
            return None 

    src_step_num += 1
    md_info_path = inject_section_heirarchy(md_info_path, src_step_num=src_step_num)
    if md_info_path is None:
        logging.error(f"DCCCM: failed {md_info_path} @inject_section_heirarchy")
        return None

    src_step_num += 1
    md_info_path = summarize_content_by_gpt(md_info_path, src_step_num=src_step_num)
    if md_info_path is None:
        logging.error(f"DCCCM: failed {md_info_path} @summarize_content_by_gpt")
        return None       

    final_md_path = make_final_md(md_info_path)

    return final_md_path

def do_content2md_convert(doc_pathname, out_dir=None, enforced_gen=False, mdcontrols=None):
    final_md_path = None
    try:
        final_md_path = _do_content2md_convert_core_md(doc_pathname,
                                                    out_dir=out_dir,
                                                    enforced_gen=enforced_gen,
                                                    mdcontrols=mdcontrols)
    except Exception as ex:
        logging.exception(ex)
        raise ex
    return final_md_path

if __name__ == "__main__":
    setup_logger_handlers()

    doc_pathname = "_work/ctn2md_深度学习在视电阻率快速反演中的研究_lp/深度学习在视电阻率快速反演中的研究___pdf.md"

    out_dir = None
    mdcontrols = None
    enforced_gen = False   

    final_md_path = do_content2md_convert(doc_pathname, out_dir=out_dir, enforced_gen=enforced_gen,  mdcontrols=mdcontrols)
    print(final_md_path)

    md_info = MdInfo(final_md_path)
    rich.print(md_info)
    print(final_md_path)