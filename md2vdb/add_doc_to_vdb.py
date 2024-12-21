from typing import List
from dotenv import load_dotenv
import sys
import logging
import os
#import rich


load_dotenv()

if "./" not in sys.path:
    sys.path.append("./")

from md2vdb.utils.util_logging import setup_logger_handlers
from md2vdb.build.doc2vdb import upsert_doc_to_vdb

def upsert_docs_to_vdb(pnames_final_info: List[str]):
    for ndx, pname_final_info in enumerate(pnames_final_info):
        logging.info(f"{ndx} updata doc to vdb: {pname_final_info}")
        if os.path.isfile(pname_final_info):
            upsert_doc_to_vdb(pname_final_info)
        else:
            logging.error(f"failed to find {pname_final_info}")

if __name__ == "__main__":
    setup_logger_handlers()

    pnames_final_info = ["_work/ctn2md_深度学习在视电阻率快速反演中的研究_lvlm/_final_info.json", 
                         "_work/ctn2md_Survey_of_different_Large_Language_Model_Architectures_lvlm/_final_info.json",
                         "_work/ctn2md_attention_is_all_you_need_lvlm/_final_info.json",
                         "_work/ctn2md_Winning_Solution_For_Meta_KDD_Cup__24_2410_00005v1_lvlm/_final_info.json"]

    #pname_final_info = "_output/ctn2md_AIGC时代的人力资源管理进化(徐刚)_lvlm/_final_info.json"
    #pname_final_info = "_output/ctn2md_业绩案例_上汽内外饰DRE外包框架服务合同_lp/_final_info.json"

    upsert_docs_to_vdb(pnames_final_info)

