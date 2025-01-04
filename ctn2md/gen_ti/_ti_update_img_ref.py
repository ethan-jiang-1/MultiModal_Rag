import os
import sys
from typing import List
import logging
import re


if './' not in sys.path:
    sys.path.append("./")


from ctn2md.src.md_info_base import MIFN, MdInfo
from ctn2md.utils_gen.gen_base import get_job_id

from ctn2md.gen_ti._ti_img_description import get_img_alt_text_and_description
from ctn2md.gen_ti._ti_get_image import download_remote_image_ti


def update_page_md_with_ref_imgs(md_info:MdInfo, page_index:int, pname_page_md:str) -> List[str]:
    """更新markdown文件中的图片引用，下载远程图片到本地
    
    Args:
        md_info: markdown信息对象
        page_index: 页码
        pname_page_md: markdown文件路径
    
    Returns:
        List[str]: 下载的图片文件名列表
    """
    job_id = md_info[MIFN.TI_CUR_JOB_ID]
    if job_id is None:
        job_id = get_job_id(md_info.get_unique_job_id())
    output_dir = md_info.get_out_dir()
    
    # 1. 读取markdown内容
    with open(pname_page_md, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 2. 扫描查找所有图片markdown格式
    # 匹配 ![alt](url "description") 格式，description 是可选的
    img_pattern = r'!\[(.*?)\]\((.*?)(?:\s+"(.*?)")?\)'
    matches = re.finditer(img_pattern, content)
    
    local_ref_image_paths = []
    new_content = content
    
    # 3. 处理每个找到的图片
    img_ndx = 0
    for match in matches:
        alt_text = match.group(1)
        img_url = match.group(2)
        description = match.group(3) or ""  # 如果没有描述，使用空字符串
        
        img_ndx += 1

        # 跳过已经是本地路径的图片
        if not img_url.startswith(('http://', 'https://')):
            if os.path.exists(os.path.join(output_dir, img_url)):
                local_ref_image_paths.append(img_url)
            continue
            
        try:
            # 生成本地文件名
            img_ext = os.path.splitext(img_url)[1] or '.png'  # 如果没有扩展名，默认用.png
            local_fname = f"{job_id}_p{page_index}_{img_ndx}{img_ext}"
            local_path = os.path.join(output_dir, local_fname)
            
            download_remote_image_ti(img_url, local_path)
            
            alt_text, description = get_img_alt_text_and_description(md_info, img_url, content)
            # 更新markdown中的图片引用，保留描述信息
            old_img_md = match.group(0)  # 使用完整的原始匹配文本
            new_img_md = f'![{alt_text}]({local_fname}{" \""+description+"\"" if description else ""})'
            new_content = new_content.replace(old_img_md, new_img_md)
            
            local_ref_image_paths.append(local_fname)
            logging.info(f"Downloaded image: {img_url} -> {local_fname}")
            
        except Exception as e:
            logging.error(f"Failed to download image {img_url}: {str(e)}")
            logging.exception(e)
            continue
    
    # 5. 保存更新后的markdown内容
    if new_content != content:
        with open(pname_page_md, 'w', encoding='utf-8') as f:
            f.write(new_content)
        logging.info(f"Updated markdown file: {pname_page_md}")
    
    return local_ref_image_paths