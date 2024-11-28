from dotenv import load_dotenv
import os
import sys
#import logging
#import rich
#import random
#import re
import shutil

load_dotenv()

if "./" not in sys.path:
    sys.path.append("./")

from ctn2md.src.md_info_base import MIFN

def n2u_replace_fnames(md_info, mifn_fnames, unique_job_id, new_job_id):
    out_dir = md_info.get_out_dir()
    changed = 0
    md_info_mifn_fnames = md_info[mifn_fnames]
    for ndx, new_fname in enumerate(md_info_mifn_fnames):
        unique_fname = new_fname.replace(new_job_id, unique_job_id)
        if unique_fname != new_fname:

            src_fname = os.path.join(out_dir, new_fname)
            dst_fname = os.path.join(out_dir, unique_fname)
            if os.path.isfile(dst_fname):
                os.unlink(dst_fname)
    
            shutil.move(src_fname, dst_fname)
            md_info_mifn_fnames[ndx] = unique_fname
            changed += 1
    return changed

def _n2u_update_md_content(md_info, pathname_md, unique_job_id, new_job_id):
    with open(pathname_md, "r") as f: 
        md_text = f.read()

    with open(pathname_md, "w+") as f: 
        md_text_new = md_text.replace(new_job_id, unique_job_id)
        f.write(md_text_new)

def _n2u_stick_with_old_names_full(md_info, unique_job_id, new_job_id):
    if unique_job_id == new_job_id:
        return 
    
    out_dir = md_info.get_out_dir()
    n2u_replace_fnames(md_info, MIFN.FNAMES_PAGES, unique_job_id, new_job_id)
    n2u_replace_fnames(md_info, MIFN.FNAMES_IMGS, unique_job_id, new_job_id)
    n2u_replace_fnames(md_info, MIFN.FNAMES_TBLS, unique_job_id, new_job_id)

    for fname_md_page in md_info[MIFN.FNAMES_PAGES]:
        pathname_page = os.path.join(out_dir, fname_md_page)
        _n2u_update_md_content(md_info, pathname_page, unique_job_id, new_job_id)

def n2u_restore_unique_name_normal_full(md_info):
    cur_job_id = md_info.get(MIFN.LP_CUR_JOB_ID)
    unique_job_id = md_info.get_unique_job_id()
    _n2u_stick_with_old_names_full(md_info, unique_job_id, cur_job_id)

def n2u_restore_unique_name_premium(md_info, cur_job_id):
    unique_job_id = md_info.get_unique_job_id()
    if unique_job_id == cur_job_id:
        return 

    out_dir = md_info.get_out_dir()
    n2u_replace_fnames(md_info, MIFN.FNAMES_P_PAGES, unique_job_id, cur_job_id)
    n2u_replace_fnames(md_info, MIFN.FNAMES_P_TBLS, unique_job_id, cur_job_id)

    for fname_md_page in md_info[MIFN.FNAMES_P_PAGES]:
        pathname_page = os.path.join(out_dir, fname_md_page)
        _n2u_update_md_content(md_info, pathname_page, unique_job_id, cur_job_id)