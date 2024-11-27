from dotenv import load_dotenv
import os
import sys
#import logging
import rich
#import random
#import json
import shutil

load_dotenv()

if "./" not in sys.path:
    sys.path.append("./")

from ctn2md.utils.util_logging import setup_logger_handlers
from ctn2md.src.md_info_base import MdInfo, MIFN

def _copy_last_step_as_final(md_info):
    last_step_num = md_info.get_last_step_num()
    pathname_step_md = md_info.name_step_pathname(last_step_num)
    pathname_final_md = md_info.name_step_pathname(-1)

    if os.path.isfile(pathname_final_md):
        os.unlink(pathname_final_md)
    shutil.copy(pathname_step_md, pathname_final_md)
    return pathname_final_md

def _move_aux_files_pages(md_info, out_dir, aux_dir):
    os.makedirs(aux_dir, exist_ok=True)
    fnames_pages = md_info.get_fnames_pages()
    if len(fnames_pages) == 0:
        return False 
    
    fnames_pages_aux = []
    for fname_page in fnames_pages:
        if aux_dir in fname_page:
            return 
        
        src_pathname = os.path.join(out_dir, fname_page)
        dst_pathname = os.path.join(aux_dir, fname_page)
        if os.path.isfile(src_pathname):
            shutil.move(src_pathname, dst_pathname)
            dst_fname = dst_pathname.replace(out_dir + "/", "")
            fnames_pages_aux.append(dst_fname)

    md_info[MIFN.FNAMES_PAGES] = fnames_pages_aux

def _move_aux_files_images(md_info, out_dir, aux_dir):
    os.makedirs(aux_dir, exist_ok=True)
    fnames_images = md_info.get(MIFN.FNAMES_IMGS, [])
    if len(fnames_images) == 0:
        return False 
    
    for ndx, fname_img in enumerate(fnames_images):
        if aux_dir in fnames_images:
            return 
        
        if fname_img in md_info[MIFN.IMG_FIGURES]:
            continue

        src_pathname = os.path.join(out_dir, fname_img)
        dst_pathname = os.path.join(aux_dir, fname_img)
        if os.path.isfile(src_pathname):
            shutil.move(src_pathname, dst_pathname)
            dst_fname = dst_pathname.replace(out_dir + "/", "")
            fnames_images[ndx] = dst_fname

def _move_aux_files_tables(md_info, out_dir, aux_dir):
    os.makedirs(aux_dir, exist_ok=True)
    fnames_tbls = md_info.get(MIFN.FNAMES_TBLS, [])
    if len(fnames_tbls) == 0:
        return False 
    
    for ndx, fname_tbl in enumerate(fnames_tbls):
        if aux_dir in fname_tbl:
            return 
        
        src_pathname = os.path.join(out_dir, fname_tbl)
        dst_pathname = os.path.join(aux_dir, fname_tbl)
        if os.path.isfile(src_pathname):
            shutil.move(src_pathname, dst_pathname)
            dst_fname = dst_pathname.replace(out_dir + "/", "")
            fnames_tbls[ndx] = dst_fname

def _move_aux_files(md_info):
    out_dir = md_info.get_out_dir()
    aux_dir = md_info.get_aux_dir()

    os.makedirs(aux_dir, exist_ok=True)
    _move_aux_files_pages(md_info, out_dir, aux_dir)
    _move_aux_files_images(md_info, out_dir, aux_dir)
    _move_aux_files_tables(md_info, out_dir, aux_dir)


def make_final_md(md_info_path):
    md_info = MdInfo(md_info_path)

    move_aux_files = md_info.get_md_control("mctl_move_aux_files", True)
    if move_aux_files:
        _move_aux_files(md_info)

    pathname_final_md = _copy_last_step_as_final(md_info)
    md_info[MIFN.FNAME_FINAL_MD] = os.path.basename(pathname_final_md)
    md_info.save()
    return pathname_final_md

if __name__ == "__main__":
    setup_logger_handlers()

    md_info_path = "_work/ctn2md_深度学习在视电阻率快速反演中的研究/_info.json"

    final_md_path = make_final_md(md_info_path)
    print(final_md_path)

    md_info = MdInfo(final_md_path)
    rich.print(md_info)
    print(final_md_path)