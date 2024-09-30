import subprocess
import os
import glob
import re
import sys
import logging

if "./" not in sys.path:
    sys.path.append("./")

from HiQA.utils.util_file import get_root_dir
from HiQA.utils.util_logging import setup_logger_handlers

def convert_ppt2md(raw_folder="./raw", output_folder="./mds/s1_md_final"):

    os.makedirs(output_folder, exist_ok=True)
    # 遍历 raw 文件夹中的所有 .pptx 文件
    pptx_files = glob.glob(os.path.join(raw_folder, "*.pptx"))

    def clean_markdown_file(md_file):
        if os.path.isfile(md_file):
            with open(md_file, 'r', encoding='utf-8') as file:
                content = file.read()

            cleaned_content = re.sub(r'\|\s*[:-]+\s*\|', '|', content)
            cleaned_content = re.sub(r'\|\s*[:-]+\s*', '|', cleaned_content)
            cleaned_content = re.sub(r'^\|\s*\|\s*$', '', cleaned_content, flags=re.MULTILINE)
            cleaned_content = re.sub(r'(_{2,})', '', cleaned_content)
            cleaned_content = re.sub(r'\|\|\|', '', cleaned_content)
            cleaned_content = re.sub(r'\s*\|$', '', cleaned_content, flags=re.MULTILINE)

            with open(md_file, 'w', encoding='utf-8') as file:
                file.write(cleaned_content)

    for pptx_file in pptx_files:
        file_name = os.path.splitext(os.path.basename(pptx_file))[0]
        output_md = os.path.join(output_folder, f"{file_name}.md")

        try:
            # 运行 ppt2md 转换
            result = subprocess.run(
                ['pptx2md', pptx_file, '-o', output_md, '--disable-color', '--disable-escaping'],
                check=True, capture_output=True, text=True
            )
            logging.info(f"成功转换{pptx_file}!")
            logging.info(f"结果保存到{output_md}")
            logging.info(result)

            # 清理 markdown 文件
            clean_markdown_file(output_md)

        except subprocess.CalledProcessError as e:
            logging.info(f"转换{pptx_file}时出现错误.")
            logging.info(e.output)


if __name__ == "__main__":
    setup_logger_handlers()
    dir_root = get_root_dir()
    os.chdir(dir_root)

    kb_name = "test"

    raw_folder=f"./datasrc/{kb_name}/raw_docs"
    output_folder=f"./datasrc/{kb_name}/mds/test_s1_md_test"
    convert_ppt2md(raw_folder=raw_folder, output_folder=output_folder)
