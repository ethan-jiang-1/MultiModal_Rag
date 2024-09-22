import openpyxl as oxl
import os
import glob
import re

def convert_xlsx2md(raw_folder="./raw", output_folder="./mds/s1_md_final"):

    os.makedirs(output_folder, exist_ok=True)

    # 遍历 raw 文件夹中的所有 .xlsx 文件
    xlsx_files = glob.glob(os.path.join(raw_folder, "*.xlsx"))

    def write_md(file_name: str, headers: list, rows: list):
        try:
            with open(file_name, encoding="utf_8_sig", mode="w", newline="\n") as f:
                if headers:
                    f.write("| " + " | ".join(headers) + " |\n")
                    f.write("| " + " | ".join(["---" for _ in headers]) + " |\n")  # 表格分隔符
                for row in rows:
                    f.write("| " + " | ".join(row) + " |\n")
        except Exception as e:
            print("CSV/Markdown 写入错误:", e)

    def clean_markdown_file(md_file):
        with open(md_file, 'r', encoding='utf-8') as file:
            content = file.read()


        cleaned_content = re.sub(r'\|\s*[---]+\s*\|', '|', content)
        cleaned_content = re.sub(r'\|\s*[---]+\s*', '|', cleaned_content)
        cleaned_content = re.sub(r'^\|\s*\|\s*$', '', cleaned_content, flags=re.MULTILINE)
        cleaned_content = re.sub(r'<br>', '', cleaned_content)

        with open(md_file, 'w', encoding='utf-8') as file:
            file.write(cleaned_content)

    for xlsx_file in xlsx_files:
        file_name = os.path.splitext(os.path.basename(xlsx_file))[0]
        output_md = os.path.join(output_folder, f"{file_name}.md")

        try:
            _wb = oxl.load_workbook(filename=xlsx_file, read_only=True, data_only=True)
            _sheet = _wb.worksheets[0] 
            # 获取所有行的数据，并替换换行符
            _rows = [[str(x).replace("\n", "<br>") if x is not None else '' for x in row] for row in _sheet.values]
            headers = _rows[0] if _rows else [] 
            data_rows = _rows[1:] if len(_rows) > 1 else [] 
            
            _wb.close()
            write_md(output_md, headers, data_rows)

            # 清理 markdown 文件
            clean_markdown_file(output_md)
            print(f"转换完成，Markdown 文件已保存到: {output_md}")

        except Exception as e:
            print(f"在转换 {xlsx_file} 时发生错误。")
            print(e)