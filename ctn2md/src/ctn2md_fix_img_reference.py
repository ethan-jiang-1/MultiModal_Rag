from dotenv import load_dotenv
import os
import sys
import logging
import rich
import re
#import random
#import json
import json_repair
from PIL import Image

load_dotenv()

if "./" not in sys.path:
    sys.path.append("./")

from ctn2md.utils.util_logging import setup_logger_handlers
from ctn2md.src.md_info_base import MdInfo, MDFN
from ctn2md.utils_llm.llm_fix_vl_instruction import get_vllm_instruction
from ctn2md.utils_llm.vllm_description import generate_image_description


# 常量定义
MIN_WIDTH = 198   # 图像最小宽度（像素）
MIN_HEIGHT = 198  # 图像最小高度（像素）
MIN_AREA = 128 * 128 # 图像最小面积（像素）

MIN_IMG_RELEVANCE_SCORE = 2.0  # 0 - 10

FEATURE_PIC_DESP_IN_MD = True

g_page2inst = {}

g_question_num = 6000

def _get_page_instruction(doc_title, page_content):
    global g_page2inst
    global g_question_num
    key = f"{doc_title}##{page_content}"
    if key in g_page2inst:
        return g_page2inst[key]

    instruction = get_vllm_instruction(doc_title, page_content, question_num=g_question_num)
    g_question_num += 1
    g_page2inst[key] = instruction
    return instruction

def _gen_figure_info(md_info, doc_title, page_content, image_path):
    instruction = _get_page_instruction(doc_title, page_content)
    resp = generate_image_description(image_path, instruction=instruction)
    if resp is None:
        raise ValueError("resp is None")
    resp_json = json_repair.repair_json(resp, return_objects=True, ensure_ascii=True)
    rich.print(resp_json)
    return resp_json

def _analyze_image_content(md_info, md_page_file=None, pathname_org_doc=None, image_path=None):
    """
    模拟多模态处理函数，分析图像的内容是否有意义。
    
    :param md_page_file: 当前页的 MD 文件路径
    :param pathname_org_doc: 原始文档路径
    :param image_path: 图像的路径
    :return: (图像简洁说明, 新的图像路径) 或 (None, None) 如果图像无意义
    """
    # 1. 提取文档标题 (doc_title)
    # 从 pathname_org_doc 中去除目录和最后的扩展名
    doc_title = MdInfo.extract_doc_title(pathname_org_doc)

    # 2. 读取当前页的 Markdown 内容 (md_page)
    try:
        with open(md_page_file, 'r', encoding='utf-8') as md_file:
            page_content = md_file.read()
    except Exception as e:
        logging.error(f"AIC: 无法读取 Markdown 文件 {md_page_file}，错误: {e}")
        return None, None

    # 3. 多模态分析逻辑
    try:
        resp_json = _gen_figure_info(md_info, doc_title, page_content, image_path)
        figure_name = resp_json.get("FigureName")
        relevance_score = resp_json.get("RelevanceScore")
        picture_discription = resp_json.get("PictureDescription")
        if relevance_score is not None:
            relevance_score = float(relevance_score)
            if relevance_score < md_info.get_md_control("mc_min_img_relevance_score", MIN_IMG_RELEVANCE_SCORE): 
                logging.warning(f"AIC: relevance_score: {relevance_score}")
                return None, None 
        if figure_name is not None:
            if figure_name == "None":
                logging.warning(f"AIC: figure_name: {figure_name}")
                return None, None
    except Exception as e:
        logging.error(f"AIC: 处理多模态异常，错误: {e}")
        logging.exception(e)
        return None, None

    return relevance_score, (figure_name, picture_discription)

def _process_image_reference(image_file, md_info):
    """
    检查图像的合理性，并返回描述和新图像路径。
    :param image_file: 图像文件名
    :param md_info: 上下文信息字典
    :return: (简洁说明, 新的图像文件名) 或 (None, None) 表示不合适的图像
    """
    out_dir = md_info.get_out_dir()
    image_path = os.path.join(out_dir, image_file)
    print(image_file)

    # 1. 图像是否存在
    if not os.path.exists(image_path):
        logging.warning(f"PIR: 无法读取图像 {image_path}")
        return None, None

    # 2. 检查图像尺寸
    try:
        with Image.open(image_path) as img:
            width, height = img.size
            if width < MIN_WIDTH or height < MIN_HEIGHT:
                logging.warning(f"PIR: 图像高宽太小 {os.path.basename(image_path)} {width, height}")
                return None, None  # 图像太小
            if width * height < MIN_AREA:
                logging.warning(f"PIR: 图像面积太小 {os.path.basename(image_path)} {width * height} < {MIN_AREA}")
                return None, None  # 图像太小
    except Exception as e:
        logging.warning(f"PIR: 无法读取图像 {image_path}，错误: {e}")
        return None, None

    # 3. 获取页号和对应的 MD 文件名
    page_match = re.search(r'_p(\d+)_', image_file)
    if not page_match:
        logging.warning(f"PIR: 无法读取图像 {os.path.basename(image_path)} 页号")
        return None, None  # 未找到页号

    page_number = page_match.group(1)
    md_page_file = next(
        (fname for fname in md_info.get_fnames_pages() if f'_p{page_number}' in fname),
        None
    )
    if not md_page_file:
        logging.warning(f"PIR: 无法找到  {os.path.basename(image_path)} 页号对应的页md")
        return None, None  # 未找到对应的 MD 文件

    # 4. 调用多模态处理逻辑
    relevance_score, figure_name_n_picture_discription = _analyze_image_content(md_info,
        md_page_file=os.path.join(out_dir, md_page_file),
        pathname_org_doc=md_info.get_doc_pathname(),
        image_path=image_path
    )
    if relevance_score and figure_name_n_picture_discription:
        return relevance_score, figure_name_n_picture_discription
    else:
        logging.warning(f"PIR: 无意义{os.path.basename(image_path)}")
        return None, None  # 图像被判断为无意义


def _filter_markdown_images(md_src_str, md_info):
    """
    处理 Markdown 中的图像引用，生成新的 Markdown 字符串。
    
    :param md_src_str: 原始 Markdown 字符串
    :param md_info: 上下文信息字典
    :return: 处理后的 Markdown 字符串
    """
    # 正则匹配 Markdown 图片引用语法 ![alt](image)\n
    image_pattern = r'!\[.*?\]\(([^)]+)\)(\r?\n)?'
    
    #out_dir = md_info.get_out_dir()
    aux_dir = md_info.get_aux_dir()
    md_info[MDFN.IMG_FIGURES] = {}

    def replace_image_reference(match):
        # 原始图像引用
        image_file = match.group(1)
        
        # 调用外部处理函数
        relevance_score, figure_name_n_picture_discription = _process_image_reference(image_file, md_info)
        
        if relevance_score and figure_name_n_picture_discription:
            figure_name, picture_discription = figure_name_n_picture_discription
            md_info[MDFN.IMG_FIGURES][image_file] = (relevance_score, figure_name, picture_discription)

            try:
                tmp_image_txt_path = os.path.join(aux_dir, image_file + ".pic_desp.txt")
                with open(tmp_image_txt_path, "w+", encoding="utf8") as f:
                    f.write(picture_discription)
            except Exception as ex:
                logging.exception(ex)
            
            if FEATURE_PIC_DESP_IN_MD:
                pic_desp = picture_discription.replace('"', '\"')
                md_pic = f"![{figure_name}]({image_file} \"{pic_desp}\")\n"
            else:
                md_pic = f"![{figure_name}]({image_file})\n"
            return md_pic
        else:
            # 返回空字符串表示移除不合适的图像引用
            return ""
    
    # 使用 re.sub 替换所有匹配的图像引用
    md_dst_str = re.sub(image_pattern, replace_image_reference, md_src_str)
    rich.print(md_dst_str)
    return md_dst_str


def fix_img_reference_by_lvlm(md_info_path, src_step_num=None):
    md_info = MdInfo(md_info_path)

    pathname_src_step_md, pathname_dst_step_md = md_info.name_src_n_dst_step_pathname(src_step_num)
    if pathname_src_step_md is None or pathname_dst_step_md is None:
        raise ValueError(f"no {pathname_src_step_md} and {pathname_dst_step_md}")

    with open(pathname_src_step_md, "r", encoding="utf8") as f:
        md_text = f.read()

    md_text_new = _filter_markdown_images(md_text, md_info)

    logging.warning(f"fix_img_reference_by_lvlm: pathname_dst_step_md: {pathname_dst_step_md}")
    with open(pathname_dst_step_md, "w+") as f:
        f.write(md_text_new)
    
    md_info.add_step_into_md_info_mdflow(pathname_dst_step_md, actor="fix_img_reference_by_lvlm")
    md_info_path = md_info.save()
    return md_info_path  


if __name__ == "__main__":
    setup_logger_handlers()

    src_step_num = 2
    #md_info_path = "_work/ctn2md_stream1/info.json"
    md_info_path = "_work/ctn2md_深度学习在视电阻率快速反演中的研究/_info.json"
    #src_step_num = 1

    md_info_path = fix_img_reference_by_lvlm(md_info_path, src_step_num=src_step_num)

    md_info = MdInfo(md_info_path)
    rich.print(md_info)
    print(md_info_path)