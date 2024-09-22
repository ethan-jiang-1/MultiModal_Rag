import subprocess
import os
import glob
import re
import sys

sys.path.append("./")

def convert_docx2md(raw_folder="./raw", output_folder="./mds/s1_md_final"):

    os.makedirs(output_folder, exist_ok=True)

    # 遍历 raw 文件夹中的所有 .docx 文件
    docx_files = glob.glob(os.path.join(raw_folder, "*.docx"))

    def clean_markdown_file(md_file):
        with open(md_file, 'r', encoding='utf-8') as file:
            content = file.read()


        cleaned_content = re.sub(r'\|\s*[:-]+\s*\|', '|', content)
        cleaned_content = re.sub(r'\|\s*[:-]+\s*', '|', cleaned_content)
        cleaned_content = re.sub(r'^\|\s*\|\s*$', '', cleaned_content, flags=re.MULTILINE)

        with open(md_file, 'w', encoding='utf-8') as file:
            file.write(cleaned_content)

    for docx_file in docx_files:
        file_name = os.path.splitext(os.path.basename(docx_file))[0]
        output_md = os.path.join(output_folder, f"{file_name}.md")

        try:
            # 运行 docx2md 转换
            result = subprocess.run(
                ['python', '-m', 'docx2md', docx_file, output_md],
                check=True, capture_output=True, text=True, encoding='utf-8'
            )
            print(f"成功转换{docx_file}!")
            print(f"结果保存到{output_md}")

            # 清理 markdown 文件
            clean_markdown_file(output_md)

        except subprocess.CalledProcessError as e:
            print(f"转换{docx_file}时出现错误.")
            print(e.output)
