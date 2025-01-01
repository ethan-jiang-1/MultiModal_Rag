import os
import sys
from typing import List, Optional, Tuple # , Dict
import logging
import requests
import re
import rich
import json_repair

if './' not in sys.path:
    sys.path.append("./")

from ctn2md.utils.util_logging import setup_logger_handlers
from ctn2md.src.md_info_base import MIFN, MdInfo
from ctn2md.src.md_page_spe import SpecialPage
from ctn2md.gen_ti._ti_gen_md import convert_image_to_md
from ctn2md.utils_gen.gen_base import get_job_id

from ctn2md.utils_llm.llm_gen_vllm_instruction_gpt import gen_vllm_instruction_by_gpt
from ctn2md.utils_llm.llm_gen_vllm_instruction_qwen import gen_vllm_instruction_by_qwen
from ctn2md.utils_llm.llm_gen_vllm_instruction_ark import gen_vllm_instruction_by_ark
from ctn2md.utils_vllm.vllm_img_description_qwen import generate_image_description_by_qwen
from ctn2md.utils_vllm.vllm_img_description_gpt import generate_image_description_by_gpt
from ctn2md.utils_vllm.vllm_img_description_ark import generate_image_description_by_ark

g_question_num = 9000

def _does_page_need_gen(pname_page_md:str, md_info:MdInfo) -> bool:
    if not os.path.isfile(pname_page_md):
        return True

    if SpecialPage.does_page_have_failed_mark(pname_page_md):
        return True

    return False

def _gen_page_md_by_ti(pname_image:str, pname_page_md:str):
    logging.info(f"GPMBL: generate page {os.path.basename(pname_page_md)}...")

    md_page = convert_image_to_md(pname_image)

    with open(pname_page_md, "w", encoding="utf-8") as f:
        f.write(md_page)

def _download_remote_image(img_url:str, local_path:str):
    response = requests.get(img_url, timeout=10)
    response.raise_for_status()
    with open(local_path, 'wb') as f:
        f.write(response.content)


def _get_page_instruction(md_info:MdInfo, doc_title:str, content_around:str) -> str:
    global g_question_num
    mctl_ti_img_relevance_model = md_info.get_md_control("mctl_ti_img_relevance_model", "ark")
    if mctl_ti_img_relevance_model == "qwen":
        instruction = gen_vllm_instruction_by_qwen(doc_title, content_around, question_num=g_question_num)
    elif mctl_ti_img_relevance_model == "gpt":
        instruction = gen_vllm_instruction_by_gpt(doc_title, content_around, question_num=g_question_num)
    elif mctl_ti_img_relevance_model == "ark":
        instruction = gen_vllm_instruction_by_ark(doc_title, content_around, question_num=g_question_num)
    else:
        raise ValueError(f"unsupport model {mctl_ti_img_relevance_model}")
    g_question_num += 1
    return instruction

def _gen_figure_info(md_info:MdInfo, doc_title:str, content_around:str, image_path_or_url:str) -> dict:
    instruction = _get_page_instruction(md_info, doc_title, content_around)
    mctl_ti_img_caption_model = md_info.get_md_control("mctl_ti_img_caption_model", "ark")
    if mctl_ti_img_caption_model == "qwen":
        resp = generate_image_description_by_qwen(image_path_or_url, instruction=instruction)
    elif mctl_ti_img_caption_model == "gpt":
        resp = generate_image_description_by_gpt(image_path_or_url, instruction=instruction)        
    elif mctl_ti_img_caption_model == "ark":
        resp = generate_image_description_by_ark(image_path_or_url, instruction=instruction)     
    else:
        raise ValueError(f"unsupport model: {mctl_ti_img_caption_model}")   
    if resp is None:
        raise ValueError("resp is None")
    resp_json = json_repair.repair_json(resp, return_objects=True, ensure_ascii=True)
    #rich.print(resp_json)
    return resp_json

def _get_img_alt_text_and_description(md_info:MdInfo, img_url:str, content:str) -> Tuple[str, str]:
    doc_title = md_info.get_doc_title()
    resp = _gen_figure_info(md_info, doc_title, content, img_url)
    rich.print(resp)
    return resp["FigureName"], resp["PictureDescription"]

def _update_page_md_with_ref_imgs(md_info:MdInfo, page_index:int, pname_page_md:str) -> List[str]:
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
            
            _download_remote_image(img_url, local_path)
            
            alt_text, description = _get_img_alt_text_and_description(md_info, img_url, content)
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

def convert_images_to_mds(md_info:MdInfo, fnames_page_image: List[str], sel_page_ndxs:Optional[List[int]] = None) -> int:
    output_dir = md_info.get_out_dir()
    aux_dir = md_info.get_aux_dir()

    if fnames_page_image is None or len(fnames_page_image) == 0:
        fnames_page_image = md_info.get(MIFN.FNAMES_SNPS, [])

    pnames_page_md = []
    fnames_imgs = []
    fnames_snps = []
    fnames_page_md_gen = []

    logging.info(f"GITM: generate pages from images")
    cnt_page_gen = 0
    map_page2ref_imgs = {}
    for ndx, fname_page_name in enumerate(fnames_page_image):
        page_index = ndx + 1

        if sel_page_ndxs is not None:
            if page_index not in sel_page_ndxs:
                continue

        pname_image = os.path.join(output_dir, fname_page_name)

        fname_page_md = f"page_{page_index}.md"
        pname_page_md = os.path.join(aux_dir, fname_page_md)
        if _does_page_need_gen(pname_page_md, md_info): 
            if not SpecialPage.does_page_have_touched_mark(pname_page_md):
                _gen_page_md_by_ti(pname_image, pname_page_md)
                cnt_page_gen += 1
                fnames_ref_name = _update_page_md_with_ref_imgs(md_info, page_index, pname_page_md)  
                map_page2ref_imgs[page_index] = [fnames_ref_name]
            fnames_page_md_gen.append(fname_page_md)
        else:
            logging.info(f"skip gen {pname_page_md}")
            fnames_page_md_gen.append(fname_page_md)

        if sel_page_ndxs is None:
            fnames_imgs.extend(fnames_ref_name) 
            fnames_snps.append(fname_page_name) 
            pnames_page_md.append(pname_page_md[len(output_dir) + 1:])

    if MIFN.TI_MAP_PAGE2REF_IMGS not in md_info:
        md_info[MIFN.TI_MAP_PAGE2REF_IMGS] = {}
    for key, value in map_page2ref_imgs.items():
        md_info[MIFN.TI_MAP_PAGE2REF_IMGS][key] = value

    logging.info(f"GITM: pages have been generated: {fnames_page_md_gen} from images")
    
    if sel_page_ndxs is None:
        md_info[MIFN.FNAMES_MD_PAGES] = pnames_page_md
        md_info[MIFN.FNAMES_IMGS] = fnames_imgs
        md_info[MIFN.FNAMES_SNPS] = fnames_snps
        md_info.save()
    return cnt_page_gen

if __name__ == "__main__":
    setup_logger_handlers()

    pname_md_info = "_output/ctn2md_papers__深度学习在视电阻率快速反演中的研究_ti/_info.json"
    sel_page_ndxs = [12]

    md_info = MdInfo(pname_md_info)  
    ret = convert_images_to_mds(md_info, None, sel_page_ndxs=sel_page_ndxs)  
    print("page generated:", ret)


