
from dotenv import load_dotenv
#import os
import sys
#import logging
#import rich

load_dotenv()

if "./" not in sys.path:
    sys.path.append("./")

class PAGE_IMG_STATUS:
    REMOVED = "removed"
    POSITIONED = "positioned"

def _del_attr(image_copy, att_name):
    att = image_copy.get(att_name, None)
    if att is not None:
        del image_copy[att_name]

def prepare_pages_images(pages, md_info):
    pages_images = []
    job_id = md_info.get_unique_job_id()
    for page in pages:
        cur_page_images = page.get("images")
        if cur_page_images is not None:
            for image in cur_page_images:
                image_copy = image.copy()
                for name in ["ocr", "height", "width", "original_width", "original_height", "job_id"]:
                    _del_attr(image_copy, name)
                name = image['name']
                if job_id in name:
                    name = name.replace(job_id + "-", "")
                    image['name'] = name
                image_copy["page_no"] = page.get("page", None)
                pages_images.append(image_copy)

    mctl_lp_img_to_heading = md_info.get_md_control("mctl_lp_img_to_heading", None)
    if mctl_lp_img_to_heading is not None:
        for img_name, plc_id in mctl_lp_img_to_heading.items():
            for image in pages_images:
                image_name = image["name"]
                image_name = image_name.split(".")[0]
                if image_name.endswith(img_name):
                    image["plc_id"] = plc_id      
    return pages_images


def get_page_images(pages_images, page_no, total_pages):
    images =[]
    for image in pages_images:
        image_page_no = image["page_no"]
        if (image_page_no >= page_no - 1) and (image_page_no <= page_no +1):
            if not image.get("pi_status", None):
                images.append(image)
    return images
