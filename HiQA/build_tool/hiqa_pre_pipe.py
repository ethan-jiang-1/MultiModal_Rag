import subprocess
import os
import glob
import re
import sys
sys.path.append("./")
from HiQA.build_tool.doc2md import docx2md
from HiQA.build_tool.ppt2md import ppt2md
from HiQA.build_tool.excel2md import xlsx2md
from HiQA.build_tool.pdf2md import pdf2md

from HiQA.build_tool import md2csv 
from HiQA.build_tool.section2embedding import section_to_embed

def parse2md(raw_folder="./raw", output_folder="./mds/s1_md_final"):
    try:
        doc_process = docx2md.convert_docx2md(raw_folder=raw_folder, output_folder=output_folder)
        ppt_process = ppt2md.convert_ppt2md(raw_folder=raw_folder, output_folder=output_folder)
        xlsx_process = xlsx2md.convert_xlsx2md(raw_folder=raw_folder, output_folder=output_folder)
        pdf_process= pdf2md.pdf2md(raw_folder=raw_folder, output_folder=output_folder)

        print(f"成功转换!")
        print(f"结果保存到{output_folder}")
    except Exception as e:
        print(f"转换时出现错误.")
        print(e.output)

def md2section(md_folder="./mds/s1_md_final", section_folder="./HiQA/datasets/test/sections"):
    try:
        md_files = glob.glob(f"{md_folder}/*.md")
        for md_file in md_files:
            md2csv.md2sections(md_file, section_folder)
        print(f"成功转换!")
        print(f"结果保存到{section_folder}")
    except Exception as e:
        print(f"转换时出现错误.")
        print(e.output)

def section2embbeding(sec_folder="./HiQA/datasets/test/sections", emb_folder="./HiQA/datasets/test/embeddings"):
    try:
        sec_files = glob.glob(f"{sec_folder}/*.csv")
        for sec_file in sec_files:
            section_to_embed(sec_file, emb_folder)
        print(f"成功转换!")
        print(f"结果保存到{emb_folder}")
    except Exception as e:
        print(f"转换时出现错误.")
        print(e.output)
# md2section()
section2embbeding()