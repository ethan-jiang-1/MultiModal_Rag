import os
from dotenv import load_dotenv

load_dotenv()

from ctn2md.utils.util_file import get_root_dir
from mmbase.utils_llm.llm_diag import do_diag_reproduce
from mmbase.utils.util_logging import setup_logger_handlers


if __name__ == "__main__":
    setup_logger_handlers()
    
    # 诊断文件路径
    debug_filename = "_work/md_samples/llm_gvi_vllminst_q31.txt"
    # debug_filename = "_work/md_samples/llm_fhl_heading_q11.txt"
    # debug_filename = "_work/md_samples/llm_gvi_vllminst_q6000.txt"

    dir_root = get_root_dir()
    llm_diag_pathname = os.path.join(dir_root, debug_filename)

    do_diag_reproduce(llm_diag_pathname)

