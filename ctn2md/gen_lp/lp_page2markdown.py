from dotenv import load_dotenv
import os
import sys
import logging
import rich
#import random
#import re
#import shutil
import json
from PIL import Image

load_dotenv()

if "./" not in sys.path:
    sys.path.append("./")

from ctn2md.src.md_process_plc import inject_plc_comment_to_page
from ctn2md.src.md_info_base import MdInfo, MIFN
from ctn2md.utils.util_logging import setup_logger_handlers

# 常量定义
MIN_WIDTH = 198   # 图像最小宽度（像素）
MIN_HEIGHT = 198  # 图像最小高度（像素）
MIN_AREA = 128 * 128 # 图像最小面积（像素）

def _check_if_valuable_image_by_size(fname_image, md_info):
    """
    检查图像的合理性，并返回描述和新图像路径。
    :param image_file: 图像文件名
    :param md_info: 上下文信息字典
    :return: (简洁说明, 新的图像文件名) 或 (None, None) 表示不合适的图像
    """
    out_dir = md_info.get_out_dir()
    image_path = os.path.join(out_dir, fname_image)

    # 1. 图像是否存在
    if not os.path.exists(image_path):
        logging.warning(f"PIR: 无法读取图像 {image_path}")
        return None, "not exist"

    # 2. 检查图像尺寸
    try:
        with Image.open(image_path) as img:
            width, height = img.size
            if width < MIN_WIDTH or height < MIN_HEIGHT:
                logging.warning(f"PIR: 图像高宽太小 {os.path.basename(image_path)} {width, height}")
                return None, "too small"  # 图像太小
            if width * height < MIN_AREA:
                logging.warning(f"PIR: 图像面积太小 {os.path.basename(image_path)} {width * height} < {MIN_AREA}")
                return None, "too small"  # 图像太小
    except Exception as e:
        logging.warning(f"PIR: 无法读取图像 {image_path}，错误: {e}")
        return None, "access error"
    return True, None

# TODO: ethan_img_ref:   we removed fix_img_ref node,  and these logics should be absorb by Page2Markdown where the best place to have knowledge to get it right
class Page2Markdown():
    def __init__(self, job_id, page, total_pages, md_info):
        self.job_id = job_id
        self.page = page 
        self.total_pages = total_pages
        self.md_info = md_info

        self.page_no = page.get("page", None)
        self.page_width = page.get("width", None)
        self.page_height = page.get("height", None)

        self.md_page = page.get("md", None)
        self.items = page.get("items", None)
        self.images = page.get("images", None)

        self.analysed = False
        self.analyse()

    def analyse(self):
        if self.analysed:
            return
        self.analyse_ocr()
        self.analyse_images()
        self.analysed = True

    def analyse_ocr(self):
        self.ocr_all_text = " "
        tmc = 0
        for image in self.images:
            ocr = image.get("ocr", None)
            if ocr is None:
                continue 
            for oi in ocr:
                confidence = oi.get("confidence", None)
                text = oi.get("text", None)
                if confidence and text:
                    tmc += len(text) * float(confidence)
                    self.ocr_all_text += text
        self.ocr_all_confidence = round(float(tmc/len(self.ocr_all_text)), 2)
        all_page_text = self.page.get("text").replace(" ", "")
        self.ocr_text_ratio = round(len(self.ocr_all_text) /(len(all_page_text) + 1), 2)

        logging.info(f"ocr_all_confidence: {self.ocr_all_confidence} for text_len:{len(self.ocr_all_text)} in a page with full_text_len:{len(all_page_text)} ocr_text_ratio:{self.ocr_text_ratio} ")

    def is_ocr_page(self):
        if self.ocr_text_ratio > 0.90:
            return True
        return False

    def analyse_images(self):
        self.images_valuable = []
        images = self.page.get("images", None)
        for image in images:
            name = image.get("name", None)
            full_name = f"{self.job_id}-{name}"
            val, reason = _check_if_valuable_image_by_size(full_name, self.md_info)
            if val:
                self.images_valuable.append({"name": full_name,
                                             "path": full_name})
        return self.images_valuable

    def get_valuable_images(self):
        return self.images_valuable

    def save_page_markdown(self):
        #rich.print(self.page)

        mctl_need_image_ref = self.md_info.get_md_control("mctl_need_image_ref", True)
        md_page_plc = inject_plc_comment_to_page(self.md_page, self.page_no, self.total_pages, self.md_info)

        md_imgs_ref_at_end = ""
        if mctl_need_image_ref:
            if self.is_ocr_page():
                md_imgs_ref_at_end = self.composite_all_images_ref_as_markdown()
            else:
                md_page_plc = self.inject_images_at_right_position(md_page_plc)
                md_imgs_ref_at_end = self.composite_all_remain_ref_as_markdown()

        md_page_all = md_page_plc + md_imgs_ref_at_end
        fname_page = self.save_md_page(md_page_all)

        return fname_page

    def get_page_md_fname(self):
        return f"{self.job_id}-content_p{self.page_no}.md"

    def save_md_page(self, md_page_all):
        try:
            out_dir = self.md_info.get_out_dir()
            fname_page_md = self.get_page_md_fname()
            pname_page_md = os.path.join(out_dir, fname_page_md)
            with open(pname_page_md, "w", encoding="utf8") as f:
                f.write(md_page_all)
            return fname_page_md
        except Exception as ex:
            logging.exception(ex)
        return None

    def get_img_ref_markdown(self, path_image):
        # TODO: ethan_img_desc need description here
        basename = os.path.basename(path_image)
        return f"![]({basename})"    

    def composite_all_images_ref_as_markdown(self):
        md_imgs = ""
        images = self.get_valuable_images()
        if images is not None:
            img_refs = []
            for image in images:
                fname = image.get("name", None)
                if fname is not None:
                    img_ref = self.get_img_ref_markdown(fname)
                    img_refs.append(img_ref)
                else:
                    logging.warning(f"image file {fname} not found.")
            if len(img_refs) > 0:
                md_imgs = "\n\n" + "\n".join(img_refs) + "\n"
        return md_imgs 

    def composite_all_remain_ref_as_markdown(self):
        # TODO: ethan_positioned_img all image but not positioned
        return self.composite_all_images_ref_as_markdown()

    def inject_images_at_right_position(self, md_page_plc):
        # TODO: ethan_positioned_img any posisted image?
        return md_page_plc


if __name__ == "__main__":
    setup_logger_handlers()

    #md_info_path = "_work/ctn2md_LongRAG/_info.json"
    md_info_path = "_work/ctn2md_业绩案例_上汽内外饰DRE外包框架服务合同/_info.json"


    md_info = MdInfo(md_info_path)

    fname_json_result = md_info.get(MIFN.LP_FNAME_JSON_RESULT_NORMAL)

    with open(fname_json_result, 'r', encoding="utf8") as f:
        json_result = json.load(f)

    json_result0 = json_result[0]
    job_id = md_info.get_unique_job_id()
    pages = json_result0["pages"]
    page = pages[0]
    total_pages = len(pages)

    p2m = Page2Markdown(job_id, page, total_pages, md_info)
    p2m.analyse()
    fname_page = p2m.save_page_markdown()
    rich.print(fname_page)
