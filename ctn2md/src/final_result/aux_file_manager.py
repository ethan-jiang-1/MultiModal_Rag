"""辅助文件管理模块，负责处理所有类型的辅助文件移动和组织"""
from dotenv import load_dotenv
import os
import shutil
import logging

load_dotenv()

from ctn2md.src.md_info_base import MdInfo, MIFN, PUBLIC_MIFN
from ctn2md.utils.util_markdown import find_all_image_refs

def move_aux_files(md_info: MdInfo) -> None:
    """移动所有辅助文件到指定目录"""
    out_dir = md_info.get_out_dir()
    aux_dir = md_info.get_aux_dir()
    logging.info(f"Moving auxiliary files to: {aux_dir}")

    os.makedirs(aux_dir, exist_ok=True)
    _move_pages(md_info, out_dir, aux_dir)
    _filter_images(md_info, out_dir, aux_dir)
    _move_tables(md_info, out_dir, aux_dir)

def _move_pages(md_info: MdInfo, out_dir: str, aux_dir: str) -> None:
    """移动页面文件到辅助目录"""
    fnames_pages = md_info.get_fnames_pages()
    if len(fnames_pages) == 0:
        return
    
    moved_count = 0
    fnames_pages_aux = []
    for fname_page in fnames_pages:
        if aux_dir in fname_page:
            continue 
        if len(os.path.dirname(fname_page)) != 0:
            continue
        src_pathname = os.path.join(out_dir, fname_page)
        dst_pathname = os.path.join(aux_dir, fname_page)
        if os.path.isfile(src_pathname):
            shutil.move(src_pathname, dst_pathname)
            dst_fname = dst_pathname.replace(out_dir + "/", "")
            fnames_pages_aux.append(dst_fname)
            moved_count += 1

    if moved_count > 0:
        logging.info(f"Moved {moved_count} page files")

    # update to reflex the move
    md_info_fanems_pages = md_info[MIFN.FNAMES_MD_PAGES]
    for ndx, fname_page in enumerate(md_info_fanems_pages):
        for fname_page_aux in fnames_pages_aux:
            if fname_page in fname_page_aux:
                md_info_fanems_pages[ndx] = fname_page_aux

def _filter_images(md_info: MdInfo, out_dir: str, aux_dir: str) -> None:
    """移动图片文件到辅助目录"""
    last_step_num = md_info.get_last_step_num()
    pathname_step_md = md_info.name_step_pathname(last_step_num)
    image_refs = find_all_image_refs(pathname_step_md)

    fnames_images = md_info.get(PUBLIC_MIFN.FNAMES_IMGS, [])
    if len(fnames_images) == 0:
        return
    
    fnames_images_kept = []
    fnames_images_filtered = []
    filtered_count = 0
    for ndx, fname_img in enumerate(fnames_images):
        if aux_dir in fname_img:
            continue 
        if len(os.path.dirname(fname_img)) != 0:
            continue

        if fname_img in image_refs:
            fnames_images_kept.append(fname_img)
            continue
        
        fnames_images_filtered.append(fname_img)
        filtered_count += 1

    md_info[MIFN.FNAMES_IMGS] = fnames_images_kept
    md_info[MIFN.FNAMES_IMGS_FILTERED] = fnames_images_filtered

    if filtered_count > 0:
        logging.info(f"Filtered {filtered_count} unused image files")


def _move_tables(md_info: MdInfo, out_dir: str, aux_dir: str) -> None:
    """移动表格文件到辅助目录"""
    fnames_tbls = md_info.get(MIFN.FNAMES_MD_TBLS, [])
    if len(fnames_tbls) == 0:
        return
    
    moved_count = 0
    for ndx, fname_tbl in enumerate(fnames_tbls):
        if aux_dir in fname_tbl:
            continue 
        if len(os.path.dirname(fname_tbl)) != 0:
            continue
        
        src_pathname = os.path.join(out_dir, fname_tbl)
        dst_pathname = os.path.join(aux_dir, fname_tbl)
        if os.path.isfile(src_pathname):
            shutil.move(src_pathname, dst_pathname)
            dst_fname = dst_pathname.replace(out_dir + "/", "")
            fnames_tbls[ndx] = dst_fname
            moved_count += 1
    
    if moved_count > 0:
        logging.info(f"Moved {moved_count} table files")

if __name__ == "__main__":
    from mmbase.utils.util_logging import setup_logger_handlers
    setup_logger_handlers()
    
    # Test code
    md_info_path = "_output/ctn2md_业绩案例_上汽内外饰DRE外包框架服务合同_lp/_info.json"
    md_info = MdInfo(md_info_path)
    move_aux_files(md_info)
    print("Auxiliary files moved successfully") 