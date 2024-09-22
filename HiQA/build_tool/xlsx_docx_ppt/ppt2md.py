import subprocess
import os
import glob
import re
import sys

sys.path.append("./")

def convert_ppt2md(raw_folder="./raw", output_folder="./mds/s1_md_final"):

    os.makedirs(output_folder, exist_ok=True)
    # 遍历 raw 文件夹中的所有 .pptx 文件
    pptx_files = glob.glob(os.path.join(raw_folder, "*.pptx"))

    def clean_markdown_file(md_file):
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
            print(f"成功转换{pptx_file}!")
            print(f"结果保存到{output_md}")

            # 清理 markdown 文件
            clean_markdown_file(output_md)

        except subprocess.CalledProcessError as e:
            print(f"转换{pptx_file}时出现错误.")
            print(e.output)
