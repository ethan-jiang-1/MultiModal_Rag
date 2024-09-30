import glob
import os
import sys
from dotenv import load_dotenv, find_dotenv

sys.path.append("./")

from HiQA.build_tool import md2csv
from HiQA.build_tool.section2embedding import section_to_embed
from HiQA.utils.util_logging import setup_logger_handlers

import logging
load_dotenv()

def _get_root_dir():
    root_dir = os.path.abspath(os.path.dirname(find_dotenv()))  
    return root_dir

def parse2md(kb_name):
    raw_folder=f"./datasrc/{kb_name}/raw_docs"
    output_folder=f"./datasrc/{kb_name}/mds/s1_md_final"

    errs = []
    try:
        from HiQA.build_tool.doc2md import docx2md
        docx2md.convert_docx2md(raw_folder=raw_folder,
                                output_folder=output_folder)
    except Exception as e:
        logging.exception(e)
        errs.append(str(e))

    try:
        from HiQA.build_tool.ppt2md import ppt2md
        ppt2md.convert_ppt2md(raw_folder=raw_folder,
                              output_folder=output_folder)
    except Exception as e:
        logging.exception(e)
        errs.append(str(e))

    try:
        from HiQA.build_tool.excel2md import xlsx2md                    
        xlsx2md.convert_xlsx2md(raw_folder=raw_folder,
                                output_folder=output_folder)
    except Exception as e:
        logging.exception(e)
        errs.append(str(e))

    err_msg = '\n'.join(errs)
    if len(err_msg):
        logging.error(err_msg)
        return False
    return True 

def md2section(kb_name):
    md_folder=f"./datasrc/{kb_name}/mds/s1_md_final"
    section_folder=f"./datasets/{kb_name}/sections"
    try:
        folder = f"{md_folder}/*.md"
        md_files = glob.glob(folder)
        md_files = sorted(md_files)
        if len(md_files) == 0:
            raise ValueError("no md_files")
        for ndx, md_file in enumerate(md_files):
            logging.info(f"转换{ndx}: {md_file}...")            
            md2csv.md2sections(md_file, section_folder)
        logging.info("成功转换!")
        logging.info(f"结果保存到{section_folder}")
    except Exception as e:
        logging.exception(e)
        logging.info("转换时出现错误.")
        logging.info(e.output)


def section2embbeding(kb_name):
    sec_folder=f"./datasets/{kb_name}/sections"
    emb_folder=f"./datasets/{kb_name}/embeddings"
    try:
        folder = f"{sec_folder}/*.csv"
        sec_files = glob.glob(folder)
        sec_files = sorted(sec_files)
        if len(sec_files) == 0:
            raise ValueError("no sec_files")
        for ndx, sec_file in enumerate(sec_files):
            logging.info(f"转换{ndx}: {sec_file}...")
            section_to_embed(sec_file, emb_folder)
        logging.info("成功转换!")
        logging.info(f"结果保存到{emb_folder}")
    except Exception as e:
        logging.exception(e)
        logging.info("转换时出现错误.")
        logging.info(e.output)


def build_embeddings(kb_name, reforced=False):
    os.makedirs(f"./datasrc/{kb_name}/mds/s1_md_final", exist_ok=True)
    os.makedirs(f"./datasets/{kb_name}/sections", exist_ok=True)
    os.makedirs(f"./datasets/{kb_name}/embeddings", exist_ok=True)

    if reforced:
        parse2md(kb_name)

    md2section(kb_name)
    section2embbeding(kb_name)

if __name__ == "__main__":
    dir_root = _get_root_dir()
    os.chdir(dir_root)

    setup_logger_handlers()

    #kb_name = "test"
    kb_name = "exam"
    build_embeddings(kb_name, reforced=False)

