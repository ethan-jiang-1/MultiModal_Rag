"""
生成最终结果模块
负责生成最终的 Markdown 文件和相关信息
"""
from dotenv import load_dotenv
import os
import logging
import rich

load_dotenv()

from mmbase.utils.util_logging import setup_logger_handlers
from ctn2md.src.md_info_base import MdInfo, PUBLIC_MIFN
from ctn2md.src.final_result.md_file_handler import copy_last_step_as_final
from ctn2md.src.final_result.aux_file_manager import move_aux_files as move_aux_files_func
from ctn2md.src.final_result.final_info_generator import generate_final_result_json

def make_final_json(md_info_path:str)->str:
    logging.info(f"##MDFLOW##: make_final_md started...")
    md_info = MdInfo(md_info_path)

    move_aux_files = md_info.get_md_control("mctl_move_aux_files", True)
    if move_aux_files:
        move_aux_files_func(md_info)

    pathname_final_md = copy_last_step_as_final(md_info)
    md_info[PUBLIC_MIFN.FNAME_FINAL_MD] = os.path.basename(pathname_final_md)
    md_info.save()

    pathname_final_json = generate_final_result_json(md_info)
    logging.info(f"##MDFLOW##: make_final_md ended: move_aux_files: {move_aux_files}.")
    logging.info(f"##MDFLOW##: Final md can be found at: \'{pathname_final_md}\'")
    return pathname_final_json

if __name__ == "__main__":
    setup_logger_handlers()

    #md_info_path = "_output/ctn2md_业绩案例_上汽内外饰DRE外包框架服务合同_lp/_info.json"
    md_info_path = "_output/ctn2md_mrag__4__前后排座椅间距定义_P1_lp/_info.json"   

    pathname_final_json = make_final_json(md_info_path)
    print(pathname_final_json)

    md_info = MdInfo(pathname_final_json)
    rich.print(md_info)
    print(pathname_final_json)