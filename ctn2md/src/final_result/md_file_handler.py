"""
Markdown文件处理模块，负责最终MD文件的生成和处理
"""
from dotenv import load_dotenv
import os
import shutil
import logging

load_dotenv()

from ctn2md.src.md_info_base import MdInfo

def copy_last_step_as_final(md_info:MdInfo)->str:
    """复制最后一步的MD文件作为最终文件"""
    last_step_num = md_info.get_last_step_num()
    pathname_step_md = md_info.name_step_pathname(last_step_num)
    pathname_final_md = md_info.name_step_pathname(-1)

    if os.path.isfile(pathname_final_md):
        os.unlink(pathname_final_md)
    shutil.copy(pathname_step_md, pathname_final_md)
    logging.info(f"Final MD copied from step {last_step_num}: {pathname_final_md}")
    return pathname_final_md

if __name__ == "__main__":
    from mmbase.utils.util_logging import setup_logger_handlers
    setup_logger_handlers()
    
    # Test code
    md_info_path = "_output/ctn2md_业绩案例_上汽内外饰DRE外包框架服务合同_lp/_info.json"
    md_info = MdInfo(md_info_path)
    pathname_final_md = copy_last_step_as_final(md_info)
    print(f"Final MD file: {pathname_final_md}") 