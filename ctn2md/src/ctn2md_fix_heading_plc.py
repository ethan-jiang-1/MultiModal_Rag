"""
标题层级修复主模块
"""
import os
import json
import logging
import rich
from mmbase.utils.util_logging import setup_logger_handlers
from ctn2md.utils.util_markdown import read_markdown_file
from ctn2md.md_info.md_info_base import MdInfo, MIFN

from ctn2md.src.fix_heading_plc.heading_collector import collect_fhl_info
from ctn2md.src.fix_heading_plc.heading_mapper import cal_new_fhl_map, get_cache_path
from ctn2md.src.fix_heading_plc.heading_updater import update_markdown_heading_content

def fix_headings_plc_by_llm(md_info_path: str, src_step_num: int = None, dst_step_num: int = None) -> str:
    """
    使用 LLM 修复 Markdown 文档的标题层级。

    参数:
        md_info_path: Markdown 信息文件路径
        src_step_num: 源步骤编号
        dst_step_num: 目标步骤编号

    返回:
        str: 处理后的 Markdown 信息文件路径
    """
    logging.info(f"##MDFLOW##: fix_headings_plc_by_llm started src_step_num:{src_step_num} dst_step_num:{dst_step_num}...")
    md_info = MdInfo(md_info_path)

    pathname_src_step_md, pathname_dst_step_md = md_info.name_src_n_dst_step_pathname(src_step_num, dst_step_num=dst_step_num)
    if pathname_src_step_md is None or pathname_dst_step_md is None:
        raise ValueError(f"no {pathname_src_step_md} and {pathname_dst_step_md}")

    md_full_text = read_markdown_file(pathname_src_step_md)

    # 收集和处理标题信息
    fhl_org, md_full_text_new = collect_fhl_info(md_info, md_full_text)

    # 计算新的标题映射
    fhl_map = cal_new_fhl_map(md_info, fhl_org)    

    # 更新文档内容
    optimized_heading_lines_map = fhl_map.get("optimized_heading_lines_map", None)
    if optimized_heading_lines_map is not None:
        o2n_map = {
            "org_heading_lines": [item["original_line"] for item in optimized_heading_lines_map],
            "new_heading_lines": [item["mapped_line"] for item in optimized_heading_lines_map]
        }
        rich.print(o2n_map)

        md_full_text_new1, unprocessed_heading_lines_map = update_markdown_heading_content(md_full_text_new, md_info, fhl_map)
        rich.print(unprocessed_heading_lines_map)

        logging.warning(f"fix_headings_plc_by_llm: pathname_dst_step_md: {pathname_dst_step_md}")
        with open(pathname_dst_step_md, "w+", encoding='utf-8') as f:
            f.write(md_full_text_new1)
        
        md_info[MIFN.FHL_MAP_O2N] = o2n_map
        md_info.add_step_into_md_info_mdflow(pathname_dst_step_md, actor="fix_headings_plc_by_llm")
        md_info_path = md_info.save()
    else:
        logging.error("failed to get optimized_heading_lines_map out of model!!")
        logging.warning(f"fix_headings_plc_by_llm: pathname_dst_step_md: {pathname_dst_step_md}")
        with open(pathname_dst_step_md, "w+", encoding='utf-8') as f:
            f.write(md_full_text)
        
        md_info.add_step_into_md_info_mdflow(pathname_dst_step_md, actor="fix_headings_plc_by_llm:failed")
        md_info_path = md_info.save()        
    
    logging.info(f"##MDFLOW##: fix_headings_plc_by_llm ended")
    return md_info_path 

if __name__ == "__main__":
    setup_logger_handlers()

    src_step_num = 0
    dst_step_num = 11
    md_info_path = "_output/ctn2md_mrag__4__前后排座椅间距定义_P1_lp/_info.json"

    # 第一次运行，应该会计算并缓存结果
    logging.info("First run - should compute and cache results")
    md_info_path = fix_headings_plc_by_llm(md_info_path, src_step_num=src_step_num, dst_step_num=dst_step_num)

    # 第二次运行，应该会使用缓存的结果
    logging.info("\nSecond run - should use cached results")
    md_info_path = fix_headings_plc_by_llm(md_info_path, src_step_num=src_step_num, dst_step_num=dst_step_num)

    # 查看缓存文件内容
    md_info = MdInfo(md_info_path)
    cache_path = get_cache_path(md_info)
    if os.path.exists(cache_path):
        logging.info(f"\nCache file exists at: {cache_path}")
        with open(cache_path, 'r', encoding='utf-8') as f:
            cache_content = json.load(f)
            logging.info(f"Cache timestamp: {cache_content.get('timestamp')}")
    
    rich.print(md_info)
    print(md_info_path)