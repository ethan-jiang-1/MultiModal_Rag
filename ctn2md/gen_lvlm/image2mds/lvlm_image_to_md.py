import os
from typing import List
import logging
import zlib

from dotenv import load_dotenv
load_dotenv()

from ctn2md.md_info.md_info_base import MdInfo
from ctn2md.utils_vllm.vllm_img2md_gpt import generate_full_mds_from_image_gpt
from ctn2md.utils_vllm.vllm_img2md_qwen import generate_full_mds_from_image_qwen
from ctn2md.utils_vllm.vllm_img2md_ark import generate_full_mds_from_image_ark
from ctn2md.src.page_spe_md import SpecialPage

def _calculate_cache_name(pname_image: str, rects_img: List[str], model: str) -> str:
    # 1. 获取基础文件名（去掉路径和扩展名）
    base_name = os.path.splitext(os.path.basename(pname_image))[0]
    
    # 2. 计算主图片的crc32
    with open(pname_image, 'rb') as f:
        image_crc32 = format(zlib.crc32(f.read()), '08x')
    
    # 3. 如果有区域图片列表，计算它们的组合crc32
    if rects_img:
        sorted_names = sorted(rects_img)
        rects_crc32 = format(zlib.crc32(''.join(sorted_names).encode()), '08x')
        return f"{base_name}_{model}_{image_crc32}_{rects_crc32}.md"
    else:
        return f"{base_name}_{model}_{image_crc32}.md"

def gen_page_md_by_lvlm(md_info:MdInfo, mctl_lvlm_img2md_model:str, pname_image:str, rects_img:List[str], pname_page_md:str):
    logging.info(f"GPMBL: generate page {os.path.basename(pname_page_md)}...")

    cache_dir = md_info.get_cache_dir()
    os.makedirs(cache_dir, exist_ok=True)
    
    # 计算缓存文件名
    cache_name = _calculate_cache_name(pname_image, rects_img, mctl_lvlm_img2md_model)
    cache_path = os.path.join(cache_dir, cache_name)
    
    # 检查缓存是否存在且内容有效
    should_generate = True
    if os.path.exists(cache_path):
        with open(cache_path, 'r', encoding='utf-8') as f:
            cached_content = f.read()
            if not SpecialPage.does_page_have_failed_mark(cached_content):
                logging.info(f"Cache hit! Using cached result from: {cache_name}")
                md_page = cached_content
                should_generate = False
            else:
                logging.info(f"Cache exists but contains error mark, regenerating content...")
    
    if should_generate:
        logging.info(f"Generating new content with model: {mctl_lvlm_img2md_model}")
        try:
            if mctl_lvlm_img2md_model == "qwen":
                md_page = generate_full_mds_from_image_qwen(pname_image, rects_img)
            elif mctl_lvlm_img2md_model == "gpt":
                md_page = generate_full_mds_from_image_gpt(pname_image, rects_img)
            elif mctl_lvlm_img2md_model == "ark":
                md_page = generate_full_mds_from_image_ark(pname_image, rects_img)
            else:
                raise ValueError(f"unsupported model {mctl_lvlm_img2md_model}")
            
            # 保存到缓存
            os.makedirs(os.path.dirname(cache_path), exist_ok=True)
            with open(cache_path, 'w', encoding='utf-8') as f:
                f.write(md_page)
            logging.info(f"Cached result saved to: {cache_name}")
            
        except Exception as ex:
            md_page = f"\n{SpecialPage.PAGE_FAILED_GEN_CONTENT_MARK}\n\n {os.path.basename(pname_page_md)}\n\n reason: {str(ex)}\n\n"
            # 不缓存错误结果
    
    # 写入目标文件
    with open(pname_page_md, "w", encoding="utf-8") as f:
        f.write(md_page)   


