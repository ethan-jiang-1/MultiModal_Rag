from dotenv import load_dotenv
import os
import sys
import logging
import rich
import re
#import random
#import json
import json_repair

load_dotenv()

if "./" not in sys.path:
    sys.path.append("./")

from HiQA.utils.util_logging import setup_logger_handlers
from HiQA.build_tool.ctn2md.md_info_base import save_md_info, load_md_info
from HiQA.build_tool.util_md.llm_fix_vl_instruction import get_vllm_instruction
from HiQA.build_tool.vl_description import generate_image_description
from PIL import Image

# 常量定义
MIN_WIDTH = 198   # 图像最小宽度（像素）
MIN_HEIGHT = 198  # 图像最小高度（像素）
MIN_AREA = 128 * 128 # 图像最小面积（像素）

FEATURE_PIC_DESP_IN_MD = True

def extract_doc_title(fname_org_doc):
    """
    提取文档标题，只去掉最后的后缀名和最后的 `.`。
    
    :param fname_org_doc: 原始文档路径
    :return: 文档标题（去掉后缀名和最后的 `.`）
    """
    # 获取文件名部分（不包括路径）
    file_name = os.path.basename(fname_org_doc)
    
    # 找到最后一个点的位置，确保只去掉最后的后缀
    last_dot_index = file_name.rfind('.')
    
    # 如果找到了点，去掉后缀和最后的点
    if last_dot_index != -1:
        return file_name[:last_dot_index]
    else:
        # 如果没有点，直接返回文件名
        return file_name

g_page2inst = {}

def get_page_instruction(doc_title, page_content):
    global g_page2inst
    key = f"{doc_title}##{page_content}"
    if key in g_page2inst:
        return g_page2inst[key]

    instruction = get_vllm_instruction(doc_title, page_content)
    g_page2inst[key] = instruction
    return instruction

def analyze_image_content(md_page_file, fname_org_doc, image_path):
    """
    模拟多模态处理函数，分析图像的内容是否有意义。
    
    :param md_page_file: 当前页的 MD 文件路径
    :param fname_org_doc: 原始文档路径
    :param image_path: 图像的路径
    :return: (图像简洁说明, 新的图像路径) 或 (None, None) 如果图像无意义
    """
    # 1. 提取文档标题 (doc_title)
    # 从 fname_org_doc 中去除目录和最后的扩展名
    doc_title = extract_doc_title(fname_org_doc)

    # 2. 读取当前页的 Markdown 内容 (md_page)
    try:
        with open(md_page_file, 'r', encoding='utf-8') as md_file:
            page_content = md_file.read()
    except Exception as e:
        logging.error(f"AIC: 无法读取 Markdown 文件 {md_page_file}，错误: {e}")
        return None, None

    # 3. 多模态分析逻辑
    try:
        instruction = get_page_instruction(doc_title, page_content)
        resp = generate_image_description(image_path, instruction=instruction)
        resp_json = json_repair.repair_json(resp, return_objects=True, ensure_ascii=True)
        rich.print(resp_json)
        figure_name = resp_json.get("FigureName")
        relevance_score = resp_json.get("RelevanceScore")
        picture_discription = resp_json.get("PictureDescription")
        if relevance_score is not None:
            relevance_score = float(relevance_score)
            if relevance_score < 5.0: 
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

def process_image_reference(out_dir, image_file, md_info):
    """
    检查图像的合理性，并返回描述和新图像路径。
    :param out_dir: 工作目录
    :param image_file: 图像文件名
    :param md_info: 上下文信息字典
    :return: (简洁说明, 新的图像文件名) 或 (None, None) 表示不合适的图像
    """
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
        (fname for fname in md_info["fnames_pages"] if f'_p{page_number}' in fname),
        None
    )
    if not md_page_file:
        logging.warning(f"PIR: 无法找到  {os.path.basename(image_path)} 页号对应的页md")
        return None, None  # 未找到对应的 MD 文件

    # 4. 调用多模态处理逻辑
    relevance_score, figure_name_n_picture_discription = analyze_image_content(
        md_page_file=os.path.join(out_dir, md_page_file),
        fname_org_doc=md_info["fname_org_doc"],
        image_path=image_path
    )
    if relevance_score and figure_name_n_picture_discription:
        return relevance_score, figure_name_n_picture_discription
    else:
        logging.warning(f"PIR: 无意义{os.path.basename(image_path)}")
        return None, None  # 图像被判断为无意义


def filter_markdown_images(md_src_str, out_dir, md_info):
    """
    处理 Markdown 中的图像引用，生成新的 Markdown 字符串。
    
    :param md_src_str: 原始 Markdown 字符串
    :param out_dir: 工作目录
    :return: 处理后的 Markdown 字符串
    """
    # 正则匹配 Markdown 图片引用语法 ![alt](image)\n
    #image_pattern = r'!\[.*?\]\(([^)]+)\)'
    #image_pattern = r'!\[.*?\]\(([^)]+)\)\n'
    image_pattern = r'!\[.*?\]\(([^)]+)\)(\r?\n)?'
    
    def replace_image_reference(match):
        # 原始图像引用
        image_file = match.group(1)
        
        # 调用外部处理函数
        relevance_score, figure_name_n_picture_discription= process_image_reference(out_dir, image_file, md_info)
        
        if relevance_score and figure_name_n_picture_discription:
            # 替换为新的 Markdown 图片引用
            if "figures" not in md_info:
                md_info["figures"] = {}
            figure_name, picture_discription = figure_name_n_picture_discription
            md_info["figures"][image_file] = (relevance_score, figure_name, picture_discription)
            image_txt_path = os.path.join(out_dir, extract_doc_title(image_file) + ".txt")
            with open(image_txt_path, "w+", encoding="utf8") as f:
                f.write(picture_discription)
            
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


def fix_img_content_by_lvlm(md_info_path):
    out_dir = os.path.dirname(md_info_path)
    md_info = load_md_info(md_info_path)
    if md_info is None:
        return None, None 

    fname_output_s1_md = md_info.get("fname_output_s1_md", None)
    if fname_output_s1_md is None:
        return None, None 

    pname_s1 = os.path.join(out_dir, fname_output_s1_md)
    with open(pname_s1, "r", encoding="utf8") as f:
        md_text = f.read()
        rich.print(md_text)

    md_text_new = filter_markdown_images(md_text, out_dir, md_info)

    fname_s2_md_name = os.path.basename(fname_output_s1_md).replace("_s1.md", "_s2.md")
    fname_output_s2_md = os.path.join(out_dir, fname_s2_md_name)
    with open(fname_output_s2_md, "w+") as f:
        f.write(md_text_new)

    logging.info(f"fname_s2_md_name: {fname_s2_md_name}")
    if isinstance(md_info, dict):
        md_info["fname_output_s2_md"] = os.path.basename(fname_output_s2_md)
        save_md_info(out_dir, md_info)
    return fname_output_s2_md, md_info    


if __name__ == "__main__":
    setup_logger_handlers()

    md_info_path = "_work/ctn2md_exam2/info.json"
    md_info_path, md_info = fix_img_content_by_lvlm(md_info_path)
    print(md_info_path)
    rich.print(md_info)