"""最终信息生成模块，负责生成和组织最终的JSON信息"""
from dotenv import load_dotenv
import json
import os
import logging

load_dotenv()

from ctn2md.md_info.md_info_base import MdInfo, PUBLIC_MIFN

def generate_final_result_json(md_info: MdInfo) -> str:
    """生成最终结果JSON文件"""
    md_final_info = {}
    _add_summary_to_final_info(md_info, md_final_info)
    _add_metadata_to_final_info(md_info, md_final_info)
    return _save_final_info(md_info, md_final_info)

def _add_summary_to_final_info(md_info: MdInfo, md_final_info: dict) -> None:
    """添加摘要信息到最终信息"""
    out_dir = md_info.get_out_dir()
    pname_final_sum = os.path.join(out_dir, md_info[PUBLIC_MIFN.FNAME_FINAL_SUM])
    with open(pname_final_sum, 'r', encoding="utf-8") as f:
        sum = json.load(f)
    md_final_info[PUBLIC_MIFN.DOC_SUMMARY] = {}
    for key, val in sum.items():
        md_final_info[PUBLIC_MIFN.DOC_SUMMARY][key] = val
        if key == "title":
            md_final_info[PUBLIC_MIFN.DOC_LOGIC_TITLE] = val 
            md_final_info[PUBLIC_MIFN.DOC_NAME_TITLE] = md_info.get_doc_title()

def _add_metadata_to_final_info(md_info: MdInfo, md_final_info: dict) -> None:
    """添加元数据到最终信息"""
    names = [
        PUBLIC_MIFN.VERSION,
        PUBLIC_MIFN.GEN_ENGINE,
        PUBLIC_MIFN.PATHNAME_ORG_DOC,
        PUBLIC_MIFN.PATHNAME_SRC_DOC,
        PUBLIC_MIFN.FNAME_ORG_DOC,
        PUBLIC_MIFN.DOC_UNIQUE_ID,
        PUBLIC_MIFN.DOC_CTN_TYPE,
        PUBLIC_MIFN.DOC_NAME_TITLE,
        PUBLIC_MIFN.DOC_LOGIC_TITLE,
        PUBLIC_MIFN.FNAME_FINAL_MD, 
        PUBLIC_MIFN.FNAME_FINAL_SUM, 
        PUBLIC_MIFN.FNAMES_SECS,
        PUBLIC_MIFN.FNAMES_IMGS,
        PUBLIC_MIFN.FNAMES_SNPS
    ]
    for name in names:
        if name in md_info:
            md_final_info[name] = md_info[name]

def _save_final_info(md_info: MdInfo, md_final_info: dict) -> str:
    """保存最终信息到JSON文件"""
    output_dir = md_info.get_out_dir()
    pathname_final_json = os.path.join(output_dir, md_info.get_fname_final_json())

    with open(pathname_final_json, 'w', encoding="utf-8") as f:
        json.dump(md_final_info, f, indent=4, ensure_ascii=False)
    logging.info(f"pathname_final_json: {pathname_final_json}")
    return pathname_final_json

if __name__ == "__main__":
    from mmbase.utils.util_logging import setup_logger_handlers
    setup_logger_handlers()
    
    # Test code
    md_info_path = "_output/ctn2md_业绩案例_上汽内外饰DRE外包框架服务合同_lp/_info.json"
    md_info = MdInfo(md_info_path)
    pathname_final_json = generate_final_result_json(md_info)
    print(f"Final JSON file: {pathname_final_json}") 