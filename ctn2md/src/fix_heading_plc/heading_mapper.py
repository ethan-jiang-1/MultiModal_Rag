"""
标题映射和缓存管理模块
负责标题映射的计算和缓存管理
"""
import os
import json
import logging
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

from ctn2md.src.md_info_base import MdInfo, MIFN, FHL_QUALITY_TYPE
from ctn2md.utils_llm.llm_fix_heading_lvl_gpt import fix_heading_lvl_markdown_by_gpt
from ctn2md.utils_llm.llm_fix_heading_lvl_qwen import fix_heading_lvl_markdown_by_qwen
from ctn2md.utils_llm.llm_fix_heading_lvl_ark import fix_heading_lvl_markdown_by_ark

def _get_cache_path(md_info: MdInfo) -> str:
    """获取缓存文件路径"""
    aux_dir = md_info.get_aux_dir()
    return os.path.join(aux_dir, "fhl_cache.json")

def _load_cache(cache_path: str) -> dict:
    """加载缓存数据"""
    if os.path.exists(cache_path):
        try:
            logging.info(f"Loading cache from {cache_path}")
            with open(cache_path, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
                logging.info(f"Cache loaded successfully with keys: {list(cache_data.keys())}")
                return cache_data
        except Exception as e:
            logging.warning(f"Failed to load cache: {e}")
    else:
        logging.info(f"No cache file found at {cache_path}")
    return None

def _save_cache(cache_path: str, data: dict):
    """保存缓存数据"""
    try:
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        logging.warning(f"Failed to save cache: {e}")

def _check_cache_valid(cache: dict, fhl_org: dict, model: str) -> bool:
    """检查缓存是否有效
    
    主要比较:
    1. org_first_line 是否相同 (内容比较)
    2. org_heading_lines 中每个 tuple 的第一项(标题内容)是否相同
    """
    if not cache:
        logging.info("Cache validation failed: cache is empty")
        return False
    
    fhl_org_cached = cache.get('fhl_org')
    fhl_org_model = cache.get('model')
    
    # 检查 model
    if fhl_org_model != model:
        logging.info("Cache validation failed: model mismatch")
        return False
        
    # 检查基本结构
    if not fhl_org_cached or not isinstance(fhl_org_cached, dict):
        logging.info("Cache validation failed: invalid fhl_org structure")
        return False
        
    # 比较 org_first_line (内容比较)
    cached_first_line = fhl_org_cached.get('org_first_line', ['', ''])
    current_first_line = fhl_org.get('org_first_line', ['', ''])
    
    # 确保都是序列类型(list或tuple)且长度为2
    if not (isinstance(cached_first_line, (list, tuple)) and isinstance(current_first_line, (list, tuple))) or \
       len(cached_first_line) != 2 or len(current_first_line) != 2:
        logging.info("Cache validation failed: invalid org_first_line structure")
        return False
    
    # 分别比较两个元素的内容
    if str(cached_first_line[0]).strip() != str(current_first_line[0]).strip() or \
       str(cached_first_line[1]).strip() != str(current_first_line[1]).strip():
        logging.info("Cache validation failed: org_first_line content mismatch")
        return False
        
    # 比较 org_heading_lines 中的标题内容
    cached_headings = fhl_org_cached.get('org_heading_lines', [])
    current_headings = fhl_org.get('org_heading_lines', [])
    
    if len(cached_headings) != len(current_headings):
        logging.info("Cache validation failed: different number of headings")
        return False
        
    for cached_tuple, current_tuple in zip(cached_headings, current_headings):
        if not cached_tuple or not current_tuple or len(cached_tuple) < 2:
            logging.info("Cache validation failed: invalid heading tuple structure")
            return False
            
        # 比较标题内容（第一项）和PLC信息（第二项）
        if str(cached_tuple[0]).strip() != str(current_tuple[0]).strip():
            logging.info("Cache validation failed: heading content mismatch")
            return False
    
    logging.info("Cache validation passed")
    return True

def cal_new_fhl_map(md_info: MdInfo, fhl_org: dict) -> dict:
    """
    计算新的标题层级映射，支持缓存机制。

    参数:
        md_info (MdInfo): Markdown 文件信息对象
        fhl_org (dict): 原始标题层级信息

    返回:
        dict: 新的标题层级映射
    """
    fname_org_doc = md_info.get("fname_org_doc", "unknown")
    mctl_fix_heading_model = md_info.get_md_control("mctl_fix_heading_model", "gpt")
    
    logging.info(f"Starting cal_new_fhl_map for {fname_org_doc} using model {mctl_fix_heading_model}")
    
    # 只在缓存相关操作出现问题时记录日志
    cache_path = _get_cache_path(md_info)
    logging.info(f"Cache path: {cache_path}")
    
    cache = _load_cache(cache_path)
    if cache and _check_cache_valid(cache, fhl_org, mctl_fix_heading_model):
        logging.info(f"Using cached heading mapping for {fname_org_doc}")
        # 记录缓存内容的基本信息
        org_heading_lines = [h[0] for h in fhl_org.get('org_heading_lines', [])]
        new_heading_lines = cache['fhl_map'].get('new_heading_lines', [])
        logging.info(f"Cache content: {{\n    'org_heading_lines': {org_heading_lines},\n    'new_heading_lines': {new_heading_lines}\n}}")
        return cache['fhl_map']
    
    logging.info(f"Calculating new heading mapping for {fname_org_doc} using {mctl_fix_heading_model}")
    
    fhl_quality = md_info.get(MIFN.FHL_QUALITY, FHL_QUALITY_TYPE.MEDIUM)
    ctn_type = md_info.get_ctn_type()
    
    now = datetime.now()
    question_num = now.hour * 100 + now.minute
    
    if mctl_fix_heading_model == "gpt":
        model = "gpt-4o"  # so far, only gpt-4o can handle this well, gpt-4o-mini does not.
        fhl_map = fix_heading_lvl_markdown_by_gpt(fhl_org, fhl_quality=fhl_quality, ctn_type=ctn_type, model=model, question_num=question_num)
    elif mctl_fix_heading_model == "qwen":
        if fhl_quality in [FHL_QUALITY_TYPE.HIGH, FHL_QUALITY_TYPE.MEDIUM]:
            model = "qwen-plus" 
        else:
            model = "qwen-max"  # TODO: ethan_qwen_prompt qwen-max is not there yet, need to revisit the prompt
        fhl_map = fix_heading_lvl_markdown_by_qwen(fhl_org, fhl_quality=fhl_quality, ctn_type=ctn_type, model=model, question_num=question_num)
    elif mctl_fix_heading_model == "ark":
        model = "ep-20241220101727-tcdfv"
        fhl_map = fix_heading_lvl_markdown_by_ark(fhl_org, fhl_quality=fhl_quality, ctn_type=ctn_type, model=model, question_num=question_num)
    else:
        error_msg = f"[File: {fname_org_doc}] Not implemented yet for using {mctl_fix_heading_model} in fix_headings_plc_by_llm"
        logging.error(error_msg)
        raise ValueError(error_msg)
    
    if not fhl_map:
        logging.error(f"[File: {fname_org_doc}] Failed to generate heading mapping")
    else:
        # 保存新的缓存
        cache_data = {
            'fhl_org': fhl_org,
            'model': mctl_fix_heading_model,
            'fhl_map': fhl_map,
            'timestamp': datetime.now().isoformat(),
            'file_info': {
                'name': fname_org_doc,
                'type': ctn_type,
                'quality': fhl_quality
            }
        }
        _save_cache(cache_path, cache_data)
        logging.info(f"[File: {fname_org_doc}] Saved new cache to {cache_path}")
    
    return fhl_map

# 为了向后兼容，保留一个公开的获取缓存路径的函数
def get_cache_path(md_info: MdInfo) -> str:
    """获取缓存文件路径（公开接口，为了向后兼容）"""
    return _get_cache_path(md_info)
