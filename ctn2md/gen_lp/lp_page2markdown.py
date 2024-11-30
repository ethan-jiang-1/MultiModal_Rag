from dotenv import load_dotenv
import os
import sys
import logging
import rich
#import random
#import re
#import shutil

load_dotenv()

if "./" not in sys.path:
    sys.path.append("./")

from ctn2md.src.md_process_plc import inject_plc_comment_to_page

def dump_images_ref_by_page(page, ensure_exist=False):
    md_imgs = ""
    images = page.get("images", None)
    if images is not None:
        img_refs = []
        for image in images:
            path = image.get("path", None) or image.get("name", None)
            if path is not None:
                basename = os.path.basename(path)
                img_refs.append(f"![]({basename})")
            else:
                logging.warning(f"image file {path} not found.")
        if len(img_refs) > 0:
            md_imgs = "\n\n" + "\n".join(img_refs) + "\n"
    return md_imgs 

def save_md_page(out_dir, job_id, page_no, md_page, md_imgs):
    try:
        md_page_all = md_page + md_imgs
        fname_page = f"{job_id}-content_p{page_no}.md"
        fname_page_md = os.path.join(out_dir, fname_page)
        with open(fname_page_md, "w", encoding="utf8") as f:
            f.write(md_page_all)
        return fname_page
    except Exception as ex:
        logging.exception(ex)
    return None

class Page2Markdown():
    def __init__(self, job_id, page, total_pages, md_info):
        self.job_id = job_id
        self.page = page 
        self.total_pages = total_pages
        self.md_info = md_info

        self.page_no = page.get("page", None)
        self.md_page = page.get("md", None)

    def save_page_markdown(self):
        rich.print(self.page)

        md_page_modified = inject_plc_comment_to_page(self.md_page, self.page_no, self.total_pages, self.md_info)

        md_imgs = dump_images_ref_by_page(self.page)

        out_dir = self.md_info.get_out_dir()
        fname_page = save_md_page(out_dir, self.job_id, self.page_no, md_page_modified, md_imgs)

        return fname_page