import json
import re
#import time
from openai import AzureOpenAI
from dotenv import load_dotenv
import sys
import os
import logging
import shutil
#import re

if "./" not in sys.path:
    sys.path.append("./")

from HiQA.utils.util_file import get_root_dir
from HiQA.utils.util_logging import setup_logger_handlers
from HiQA.build_tool.pdf2md.llm_prompt_pdf2md import PROMPT_GET_CONTENT, PROMPT_MD_CORRECT
from HiQA.build_tool.util_md.llm_fix_ocr_md import fix_ocr_self_correct_markdown

load_dotenv()

SUBFOLDER_NAME_IMG = "img"

def get_pdfs_in_directory(directory):
    pdf_files = [f for f in os.listdir(directory) if f.endswith('.pdf')]
    return pdf_files

def _move_images_step0(out_dir, img_rel_root, img_fname_prefix, md_filepath):
    # 确保目标子目录存在
    target_dir = os.path.join(out_dir, img_rel_root)
    os.makedirs(target_dir, exist_ok=True)

    # 用于记录旧路径和新路径的映射，供后续更新 .md 文件使用
    path_mapping = {}

    # 定义支持的图片格式
    image_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.svg')

    # 遍历 out_dir 的内容
    for item in os.listdir(out_dir):
        item_path = os.path.join(out_dir, item)

        # 如果是文件且为图片文件
        if os.path.isfile(item_path) and item.lower().endswith(image_extensions):
            # 生成唯一的新文件名
            base_name, ext = os.path.splitext(item)
            count = 1
            new_name = img_fname_prefix + base_name + ext
            while os.path.exists(os.path.join(target_dir, new_name)):
                new_name = f"{img_fname_prefix}{base_name}_{count}{ext}"
                count += 1
            new_path = os.path.join(target_dir, new_name)

            try:
                shutil.move(item_path, new_path)
            except Exception as e:
                logging.error(f"Failed to move {item_path} to {new_path}: {e}")
                continue

            old_path = os.path.normpath(item)
            path_mapping[old_path.replace('\\', '/')] = os.path.join(img_rel_root, new_name).replace('\\', '/')

        # 如果是 figures 子目录
        elif os.path.isdir(item_path) and item == 'figures':
            # 遍历 figures 目录中的图片文件
            for root, _, files in os.walk(item_path):
                for file in files:
                    if file.lower().endswith(image_extensions):
                        # 生成唯一的新文件名
                        base_name, ext = os.path.splitext(file)
                        count = 1
                        new_name = img_fname_prefix + base_name + ext
                        while os.path.exists(os.path.join(target_dir, new_name)):
                            new_name = f"{img_fname_prefix}{base_name}_{count}{ext}"
                            count += 1
                        new_path = os.path.join(target_dir, new_name)

                        old_file_path = os.path.join(root, file)
                        try:
                            shutil.move(old_file_path, new_path)
                        except Exception as e:
                            logging.error(f"Failed to move {old_file_path} to {new_path}: {e}")
                            continue

                        old_path = os.path.relpath(old_file_path, out_dir)
                        old_path = os.path.normpath(old_path)
                        path_mapping[old_path.replace('\\', '/')] = os.path.join(img_rel_root, new_name).replace('\\', '/')

            # 删除 figures 目录
            try:
                shutil.rmtree(item_path)
            except Exception as e:
                logging.error(f"Failed to remove directory {item_path}: {e}")

    # 更新指定的 .md 文件中的图像引用
    if os.path.isfile(md_filepath):
        with open(md_filepath, 'r', encoding='utf-8') as md_file:
            content = md_file.read()

        # 替换 IMG 标签中的路径
        def replace_image_paths(match):
            alt_text = match.group(1)
            quote = match.group(2) or ''
            old_path = match.group(3)
            old_path_normalized = os.path.normpath(old_path).replace('\\', '/')
            if old_path_normalized in path_mapping:
                new_path = path_mapping[old_path_normalized]
                return f'![{alt_text}]({quote}{new_path}{quote})'
            return match.group(0)  # 不修改未匹配的内容

        # 匹配 IMG 标签，支持带引号的路径
        pattern = r'!\[([^\]]*)\]\((["\']?)([^"\')]+?\.(?:png|jpg|jpeg|gif|svg))\2\)'
        content = re.sub(pattern, replace_image_paths, content)

        # 保存更新后的内容
        with open(md_filepath, 'w', encoding='utf-8') as md_file:
            md_file.write(content)
    else:
        logging.warning(f"Markdown file {md_filepath} does not exist.")

def pdf2md_step0_pix2text(pdf_path, md_filename, out_dir):
    from pix2text import Pix2Text
    p2t = Pix2Text.from_config(enable_formula=False)
    doc = p2t.recognize_pdf(pdf_path)
    img_rel_root = SUBFOLDER_NAME_IMG
    img_fname_prefix = os.path.basename(md_filename).split(".")[0] + "_"
    doc.to_markdown(out_dir=out_dir, markdown_fn=md_filename)
    md_filepath = os.path.join(out_dir, md_filename)
    _move_images_step0(out_dir, img_rel_root, img_fname_prefix, md_filepath)
    return True

def pdf2md_step0(pdf_path, md_filename, out_dir):
    try:
        rc = pdf2md_step0_pix2text(pdf_path, md_filename, out_dir)
        return rc
    except Exception as ex:
        logging.warning(f"{pdf_path} exception: {str(ex)}")

    return False


def get_uns_content_step1(file_path):
    from unstructured.partition.pdf import partition_pdf
    elements = partition_pdf(file_path)
    str_list = [
        str(el).replace("保密信息", "").replace("技术服务合同 V5.0", "")
        for el in elements
    ]
    new_list = [re.sub(r'第\d+页/共\d+页', '', str) for str in str_list]
    return "\n".join(new_list)


def get_md_content_step1(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        md_text = file.read()
    file.close()
    return md_text

def _get_gpt_messages(prompt):
    messages=[
        {
            "role": "system",
            "content": "You are a helpful assistant."
        },
        {
            "role": "user",
            "content": prompt
        },
    ]
    return messages

def fix_ocr_content_step1(doc_pathname, md_file):
    client = AzureOpenAI(api_key=os.getenv("OPENAI_API_KEY"),
                         azure_endpoint=os.getenv("OPENAI_BASE_URL"),
                         api_version="2024-02-15-preview")
    md_text = get_md_content_step1(md_file)
    try:
        content = get_uns_content_step1(doc_pathname)
        prompt = PROMPT_GET_CONTENT.format(Content=content)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=_get_gpt_messages(prompt),
            temperature=0.1)
        text = response.choices[0].message.content
        res = json.loads(text.replace("```", "").replace("json", ""))
        text = res['content']

        prompt = PROMPT_MD_CORRECT.format(text1=text, markdown=md_text)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=_get_gpt_messages(prompt),
            temperature=0.1)
        text = response.choices[0].message.content
        res = json.loads(text.replace("```", "").replace("json", ""))
        return res['content']
    except Exception as ex: # noqa
        logging.warning(f"{md_file} exception: {ex}, ignore")

    doc_type = doc_pathname.split(".")[-1].lower()
    return fix_ocr_self_correct_markdown(md_text, doc_type)



def pdf2md_step1(fname, raw_folder, step_0_dir, output_folder):
    #获取更新后的md
    os.makedirs(output_folder, exist_ok=True)
    content = fix_ocr_content_step1(raw_folder + '/' + fname,
                                    step_0_dir + '/' + fname + '.step0.md')
    with open(output_folder + '/' + fname + '.step1.md',
              'w',
              encoding='utf-8') as file:
        file.write(content)

def _copy_img_from_step0_to_step1(step_0_dir, output_folder):
    img_folder = os.path.join(step_0_dir, SUBFOLDER_NAME_IMG)
    if os.path.isdir(img_folder):
        img_new_folder = os.path.join(output_folder, SUBFOLDER_NAME_IMG)
        os.makedirs(img_new_folder, exist_ok=True)
        names = os.listdir(img_folder)
        for name in names:
            if name.endswith(".png") or name.endswith(".jpg"):
                src_path = os.path.join(img_folder, name)
                dst_path = os.path.join(img_new_folder, name)
                shutil.copyfile(src_path, dst_path)

def pdf2md(raw_folder, output_folder, step_0_dir='mds/s0_md_unstructured'):
    #direcory_path: pdf目录
    #step_0_dir：step_0目录
    #step_1_dir:step_1目录
    #获取所有.pdf文件
    pdfs = get_pdfs_in_directory(raw_folder)
    #初步处理pdf2md
    base_path = os.getcwd()
    for fname in pdfs:
        rc = False
        try:
            pdf2md_step0(base_path + '/' + raw_folder + '/' + fname,
                        fname + '.step0.md',
                        step_0_dir)
            logging.info(fname + '.step0.md 已生成')

            pdf2md_step1(fname, raw_folder, step_0_dir, output_folder)
            logging.info(fname + '.step1.md 已生成')
            rc = True
        except Exception as ex:
            logging.exception(f"{fname} exception: {str(ex)}")
            raise ex
        logging.info(f"pdf2md result: {fname} rc:{rc}")

    _copy_img_from_step0_to_step1(step_0_dir, output_folder)
    

if __name__ == "__main__":
    setup_logger_handlers()
    dir_root = get_root_dir()
    os.chdir(dir_root)

    kb_name = "test"

    raw_folder=f"./datasrc/{kb_name}/raw_docs"
    output_folder=f"./datasrc/{kb_name}/mds/test_s1_md_test"
    step_0_dir = f"./datasrc/{kb_name}/mds/test_s0_md_test"
    pdf2md(raw_folder=raw_folder, output_folder=output_folder, step_0_dir=step_0_dir)