import copy
from datetime import datetime 
import logging
from typing import Tuple
from dotenv import load_dotenv
import rich
import os
import json

load_dotenv()

from mmbase.utils.util_logging import setup_logger_handlers
from ctn2md.utils_llm.llm_fix_heading_lvl_gpt import fix_heading_lvl_markdown_by_gpt
from ctn2md.utils_llm.llm_fix_heading_lvl_qwen import fix_heading_lvl_markdown_by_qwen
from ctn2md.utils_llm.llm_fix_heading_lvl_ark import fix_heading_lvl_markdown_by_ark
from ctn2md.src.md_info_base import MdInfo, MIFN, FHL_QUALITY_TYPE
from ctn2md.src.md_process_plc import inject_plc_comment_to_page, separate_heading_and_plc_comment, get_all_normalized_headings_with_plc_info, has_injected_plc_comment
from ctn2md.utils.util_markdown import read_markdown_file

def _normalize_markdown_heading_plc(md_text:str, md_info:MdInfo) -> str:
    """
    规整化 Markdown 的 heading 写法，确保所有 heading 的 # 与内容之间仅有一个空格。

    参数:
        md_text (str): 输入的 Markdown 字符串流。
        md_info (str): 输出文件的名称信息。

    返回:
        str: 规整化后的 Markdown 字符串。
    """

    normalized_lines, heading_n_plc_lines, first_line_no_heading = get_all_normalized_headings_with_plc_info(md_text)

    # 生成规整化的 Markdown 内容
    normalized_md = "\n".join(normalized_lines)

    heading_first_line, plc_comment_first_line = "", ""
    if first_line_no_heading is not None and len(first_line_no_heading) > 0:
        heading_first_line, plc_comment_first_line = separate_heading_and_plc_comment(first_line_no_heading)

    md_info[MIFN.FHL_ORG] = {"org_doc_title": md_info.get_doc_title(),
                             "org_doc_type": md_info.get_ctn_type(),
                             "org_first_line": (heading_first_line, plc_comment_first_line),
                             "org_heading_lines": heading_n_plc_lines}
    md_info.save()
                
    return normalized_md

def _fix_markdown_with_no_heading(md_text:str, md_info:MdInfo) -> str:
    doc_title = md_info.get_doc_title()
    heading_line = "# " + doc_title + "\n\n"
    new_md_text = heading_line + md_text
    return inject_plc_comment_to_page(new_md_text, 1, 1, md_info)


def _update_markdown_heading_content(md_text:str, md_info:MdInfo, fhl_map:dict) -> Tuple[str, list]:
    """
    替换 Markdown 文本中的标题内容，根据 fhl_map 提供的替换规则。

    :param md_text: Markdown 文本
    :param md_info: Markdown 文件的基本信息
    :param fhl_map: 包含映射规则的 JSON 字典
    :return: 替换后的 Markdown 文本 new_md_text 和未处理的 fhl_map 副本
    """

    # 创建 fhl_map 的副本以进行替换操作
    fhl_map_copy = copy.deepcopy(fhl_map)

    # 提取映射规则
    heading_lines_map = fhl_map_copy.get("optimized_heading_lines_map", [])
    if len(heading_lines_map) == 0:
        raise ValueError("UMHC: heading_lines_map == [] ?!")

    # 初始化结果 Markdown 文本
    lines = md_text.splitlines()
    new_lines = []

    # 标记哪些 heading_lines_map 的项已被处理
    used_indices = set()

    for line in lines:
        stripped_line = line.strip()
        replaced = False

        if stripped_line.startswith("#"):
            for i, item in enumerate(heading_lines_map):
                if i in used_indices:
                    continue
                if stripped_line.startswith(item["original_line"]):
                    new_line = item["mapped_line"]
                    if new_line is None:
                        new_line = ""
                    new_lines.append(new_line)
                    used_indices.add(i)
                    replaced = True
                    break

        if not replaced:
            new_lines.append(line)

    # 检查未处理的 heading_lines_map 项
    unprocessed_heading_lines_map = [
        item for i, item in enumerate(heading_lines_map) if i not in used_indices
    ]
    fhl_map_copy["unprocessed_heading_lines_map"] = unprocessed_heading_lines_map

    # 生成新的 Markdown 文本
    new_md_text = "\n".join(new_lines)

    return new_md_text, unprocessed_heading_lines_map


def _collect_fhl_info(md_info:MdInfo, md_full_text:str) -> Tuple[dict, str]:
    md_full_text_new = _normalize_markdown_heading_plc(md_full_text, md_info)
    fhl_org = md_info[MIFN.FHL_ORG]

    org_heading_lines = fhl_org["org_heading_lines"]
    if (len(org_heading_lines)) == 0 or (not has_injected_plc_comment(md_full_text)):
        md_full_text_new = _fix_markdown_with_no_heading(md_full_text_new, md_info)

        md_full_text_new = _normalize_markdown_heading_plc(md_full_text_new, md_info)
        fhl_org = md_info[MIFN.FHL_ORG]

    return fhl_org, md_full_text_new

def _get_cache_path(md_info: MdInfo) -> str:
    """获取缓存文件路径"""
    aux_dir = md_info.get_aux_dir()
    return os.path.join(aux_dir, "fhl_cache.json")

def _load_cache(cache_path: str) -> dict:
    """加载缓存数据"""
    if os.path.exists(cache_path):
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logging.warning(f"Failed to load cache: {e}")
    return None

def _save_cache(cache_path: str, data: dict):
    """保存缓存数据"""
    try:
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        logging.warning(f"Failed to save cache: {e}")

def _check_cache_valid(cache: dict, fhl_org: dict, model: str) -> bool:
    """检查缓存是否有效"""
    if not cache:
        return False
    
    return (cache.get('fhl_org') == fhl_org and 
            cache.get('model') == model)

def _cal_new_fhl_map(md_info:MdInfo, fhl_org:dict) -> dict:
    """计算新的标题层级映射，支持缓存机制"""
    now = datetime.now()
    question_num = now.hour * 100 + now.minute
    logging.info(f"question_num: {question_num}")
    
    # 获取缓存路径
    cache_path = _get_cache_path(md_info)
    
    # 获取当前使用的模型
    mctl_fix_heading_model = md_info.get_md_control("mctl_fix_heading_model", "gpt")
    
    # 加载缓存
    cache = _load_cache(cache_path)
    
    # 检查缓存是否有效
    if _check_cache_valid(cache, fhl_org, mctl_fix_heading_model):
        logging.info("Using cached fhl_map result")
        return cache['fhl_map']
    
    # 如果缓存无效，重新计算
    fhl_quality = md_info.get(MIFN.FHL_QUALITY, FHL_QUALITY_TYPE.MEDIUM)
    ctn_type = md_info.get_ctn_type()
    
    if mctl_fix_heading_model == "gpt":
        model = "gpt-4o" # so far, only gpt-4o can handle this well,  gpt-4o-mini does not.
        fhl_map = fix_heading_lvl_markdown_by_gpt(fhl_org, fhl_quality=fhl_quality, ctn_type=ctn_type, model=model, question_num=question_num)
    elif mctl_fix_heading_model == "qwen":
        model = "qwen-max"  # TODO: ethan_qwen_prompt qwen-max is not there yet, need to revisit the prompt
        fhl_map = fix_heading_lvl_markdown_by_qwen(fhl_org, fhl_quality=fhl_quality, ctn_type=ctn_type, model=model, question_num=question_num)
    elif mctl_fix_heading_model == "ark":
        model = "ep-20241220101727-tcdfv"
        fhl_map = fix_heading_lvl_markdown_by_ark(fhl_org, fhl_quality=fhl_quality, ctn_type=ctn_type, model=model, question_num=question_num)
    else:
        raise ValueError(f"not implemented yet for using {mctl_fix_heading_model} in fix_headings_plc_by_llm")
    
    # 保存新的缓存
    cache_data = {
        'fhl_org': fhl_org,
        'model': mctl_fix_heading_model,
        'fhl_map': fhl_map,
        'timestamp': datetime.now().isoformat()
    }
    _save_cache(cache_path, cache_data)
    
    return fhl_map

def fix_headings_plc_by_llm(md_info_path:str, src_step_num:int = None, dst_step_num:int = None) -> str:
    logging.info(f"##MDFLOW##: fix_headings_plc_by_llm started src_step_num:{src_step_num} dst_step_num:{dst_step_num}...")
    md_info = MdInfo(md_info_path)

    pathname_src_step_md, pathname_dst_step_md = md_info.name_src_n_dst_step_pathname(src_step_num, dst_step_num=dst_step_num)
    if pathname_src_step_md is None or pathname_dst_step_md is None:
        raise ValueError(f"no {pathname_src_step_md} and {pathname_dst_step_md}")

    md_full_text = read_markdown_file(pathname_src_step_md)

    fhl_org, md_full_text_new = _collect_fhl_info(md_info, md_full_text)

    fhl_map = _cal_new_fhl_map(md_info, fhl_org)    

    optimized_heading_lines_map = fhl_map.get("optimized_heading_lines_map", None)
    if optimized_heading_lines_map is not None:
        o2n_map = {"org_heading_lines": [item["original_line"] for item in optimized_heading_lines_map],
                   "new_heading_lines": [item["mapped_line"] for item in optimized_heading_lines_map]}
        rich.print(o2n_map)

        md_full_text_new1, unprocessed_heading_lines_map = _update_markdown_heading_content(md_full_text_new, md_info, fhl_map)
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
    cache_path = _get_cache_path(md_info)
    if os.path.exists(cache_path):
        logging.info(f"\nCache file exists at: {cache_path}")
        with open(cache_path, 'r', encoding='utf-8') as f:
            cache_content = json.load(f)
            logging.info(f"Cache timestamp: {cache_content.get('timestamp')}")
    
    rich.print(md_info)
    print(md_info_path)