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

def _select_meanful_image_by_size(fname_image, md_info):
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

def _find_closest_heading(image, headings, page, y_threshold_ratio=None, x_tolerance_ratio=None):
    """
    根据页面的尺寸和图像的位置动态计算 y_threshold 和 x_tolerance，寻找视觉上最近的 heading。

    :param image: 图像数据，包含 'x', 'y' 等信息
    :param headings: 所有的 headings，包含 'type', 'lvl', 'value', 'bBox' 等信息
    :param page: 页面数据，包含 'width', 'height' 等信息，用来计算动态阈值
    :param y_threshold_ratio: Y 坐标的容忍比例，决定图像上下可接受的距离
    :param x_tolerance_ratio: X 坐标的容忍比例，决定图像和标题在水平方向上的接近程度
    :return: 最近的 heading 对象
    """
    # 获取页面的宽度和高度
    page_width = page['width']
    page_height = page['height']
    
    # 计算页面的宽高比
    page_ratio = page_width / page_height

    # 根据页面类型调整阈值
    if page_ratio > 1:  # PPT类型页面，宽大于高
        y_threshold_ratio = y_threshold_ratio or 0.3  # 放宽y方向的容忍度
        x_tolerance_ratio = x_tolerance_ratio or 0.4  # 放宽x方向的容忍度
    else:  # A4类型页面，宽小于高
        y_threshold_ratio = y_threshold_ratio or 0.3  # 严格要求y方向的阈值
        x_tolerance_ratio = x_tolerance_ratio or 0.4  # 适中的x容忍度

    # 计算动态的 y_threshold 和 x_tolerance
    y_threshold = page_height * y_threshold_ratio  # 垂直方向阈值
    x_tolerance = page_width * x_tolerance_ratio   # 水平方向容忍度

    # 设置阈值的最大限制，避免过大的容忍度
    y_threshold = min(y_threshold, page_height * 0.5)  # 最大不超过页面的50%
    x_tolerance = min(x_tolerance, page_width * 0.4)  # 最大不超过页面的25%
    logging.info(f"FCH: y_threshold: {y_threshold}")
    logging.info(f"FCH: x_tolerance: {x_tolerance}")

    closest_heading = None
    min_distance = float('inf')  # 初始化最小距离为无穷大

    # 获取图像的上下边界坐标（仅使用图像的y坐标和页面高度来估算）
    image_y_top = image['y']
    image_x_left = image['x']
    if (image_y_top < page_height * 0.1) and (image_x_left < page_width * 0.1):
        return None

    for heading in headings:
        # 跳过没有 bBox 的 heading
        if 'bBox' not in heading:
            continue

        # 计算y方向的距离
        heading_y_top = heading['bBox']['y']
        y_distance = abs(image_y_top - heading_y_top)

        # 计算x方向的距离
        heading_x_left = heading['bBox']['x']
        x_distance = abs(image_x_left - heading_x_left)

        # 调试日志：记录y和x的距离
        logging.debug(f"Image '{image['name']}' vs Heading '{heading['value']}': "
                      f"y_distance={y_distance}, x_distance={x_distance}, "
                      f"y_threshold={y_threshold}, x_tolerance={x_tolerance}")

        # 如果y方向的距离小于阈值，检查x方向的容忍度
        if y_distance < y_threshold:
            if x_distance <= x_tolerance:
                total_distance = y_distance + x_distance  # 总距离：y 距离 + x 距离
                if total_distance < min_distance:
                    min_distance = total_distance
                    closest_heading = heading

    # 如果没有找到符合条件的heading，记录警告
    if closest_heading is None:
        logging.warning(f"No heading found for image '{image['name']}'. "
                        f"y_threshold={y_threshold}, x_tolerance={x_tolerance}. "
                        f"Try adjusting these thresholds.")

    return closest_heading


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

        self.ocr_all_text = " "
        self.ocr_all_confidence = 0
        self.ocr_text_ratio = 0

        self.images_selected_embd = []
        self.images_selected_page = []
        self.images_unselected_page = []

        if MIFN.LP_P2M_INFO not in md_info:
            md_info[MIFN.LP_P2M_INFO] = {}
        if self.page_no not in md_info[MIFN.LP_P2M_INFO]:
            md_info[MIFN.LP_P2M_INFO][self.page_no] = {}
        self.md_info_cur_page = md_info[MIFN.LP_P2M_INFO][self.page_no] 

        self.analysed = False
        self.analyse()

    def analyse(self):
        if self.analysed:
            return
        self.analyse_ocr()
        self.analyse_images()
        self.analyse_images_embd()
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

        logging.info(f"P2M: ocr_all_confidence: {self.ocr_all_confidence} for text_len:{len(self.ocr_all_text)} in a page with full_text_len:{len(all_page_text)} ocr_text_ratio:{self.ocr_text_ratio} ")
        logging.info(f"P2M: is_ocr_page: {self.is_ocr_page()}")
        if self.is_ocr_page() and (self.ocr_all_confidence < 0.6):
            logging.warning(f"P2M: is_ocr_page: {self.is_ocr_page()} with low ocr_all_confidence:{self.ocr_all_confidence}")

        self.md_info_cur_page["ocr_all_confidence"] = self.ocr_all_confidence
        self.md_info_cur_page["ocr_text_ratio"] = self.ocr_text_ratio
        self.md_info_cur_page["ocr_len_orc"] = len(self.ocr_all_text)
        self.md_info_cur_page["ocr_len_full"] = len(all_page_text)

    def is_ocr_page(self):
        if self.ocr_text_ratio > 0.90:
            return True
        return False

    def analyse_images(self):
        self.images_selected_embd = []
        self.images_selected_page = []
        self.images_unselected_page = []
        images = self.page.get("images", None)
        for image in images:
            name = image.get("name", None)
            image_copy = image.copy()
            ocr = image_copy.get("ocr", None)
            if ocr is not None:
                del image_copy["ocr"]
            full_name = f"{self.job_id}-{name}"
            val, reason = _select_meanful_image_by_size(full_name, self.md_info)
            if val:
                image_copy["name"] = full_name 
                if name.find("img_p") != -1:
                    self.images_selected_embd.append(image_copy)
                else:
                    self.images_selected_page.append(image_copy)
            else:
                image_copy["reason"] = reason
                self.images_unselected_page.append(image_copy)
        logging.info(f"P2M: images_selected_embd: {len(self.images_selected_embd)}")
        logging.info(f"P2M: images_selected_page: {len(self.images_selected_page)}")
        logging.info(f"P2M: images_unselected_page: {len(self.images_unselected_page)}")

    def analyse_images_embd(self):
        found = 0
        headings = [item.copy() for item in self.items if item["type"] == "heading"]
        rich.print(headings)
        for image in self.images_selected_embd:
            rich.print(image)
            closest_heading = _find_closest_heading(image, headings, self.page)
            if closest_heading is not None:
                image["closest_heading"] = closest_heading
                found +=1 
        logging.info(f"P2M: closet_heading founded: {found}")

        self.md_info_cur_page["images_selected_embd"] = self.images_selected_embd
        self.md_info_cur_page["images_selected_page"] = self.images_selected_page
        self.md_info_cur_page["images_unselected_page"] = self.images_unselected_page

    def save_page_markdown(self):
        #rich.print(self.page)

        mctl_need_image_ref = self.md_info.get_md_control("mctl_need_image_ref", True)
        md_page_plc = inject_plc_comment_to_page(self.md_page, self.page_no, self.total_pages, self.md_info)

        md_imgs_ref_at_end = ""
        if mctl_need_image_ref:
            # if self.is_ocr_page():
            #     md_imgs_ref_at_end = self.composite_all_images_ref_as_markdown()
            # else:
            md_page_plc = self.inject_images_at_right_position(md_page_plc)
            md_imgs_ref_at_end = self.composite_all_not_positioned_ref_as_markdown()

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
        img_refs = []
        for image in self.images_selected_embd:
            fname = image.get("name", None)
            if fname is not None:
                img_ref = self.get_img_ref_markdown(fname)
                img_refs.append(img_ref)
        for image in self.images_selected_page:
            fname = image.get("name", None)
            if fname is not None:
                img_ref = self.get_img_ref_markdown(fname)
                img_refs.append(img_ref)
        md_imgs = ""
        if len(img_refs) > 0:
            md_imgs = "\n\n" + "\n".join(img_refs) + "\n"
        return md_imgs 

    def composite_all_not_positioned_ref_as_markdown(self):
        img_refs = []
        for image in self.images_selected_embd:
            closest_heading = image.get("closest_heading", None)
            if closest_heading is None or closest_heading["md"].startswith("#"):
                fname = image.get("name", None)
                if fname is not None:
                    img_ref = self.get_img_ref_markdown(fname)
                    img_refs.append(img_ref)
        for image in self.images_selected_page:
            fname = image.get("name", None)
            if fname is not None:
                img_ref = self.get_img_ref_markdown(fname)
                img_refs.append(img_ref)
        md_imgs = ""
        if len(img_refs) > 0:
            md_imgs = "\n\n" + "\n".join(img_refs) + "\n"
        return md_imgs 

    def inject_images_at_right_position(self, md_page_plc):
        # 1. 按行切割 Markdown
        lines = md_page_plc.split('\n')
        
        # 2. 逐行加工处理
        processed_lines = []
        for line in lines:
            new_line = None
            if line.startswith("#"):
                for image in self.images_selected_embd:
                    closest_heading = image.get("closest_heading", None)
                    if closest_heading is not None:
                        if line.startswith(closest_heading["md"]):
                            fname = image.get("name", None)
                            if fname is not None:
                                closest_heading["md"] = "* " + closest_heading["md"]
                                new_line = line +" " + self.get_img_ref_markdown(fname)
                                break
            if new_line is not None:
                line = new_line
            processed_lines.append(line)

        # 3. 将加工后的行重新合并为 Markdown 字符串
        processed_md = '\n'.join(processed_lines)
        
        return processed_md

if __name__ == "__main__":
    setup_logger_handlers()

    #md_info_path = "_work/ctn2md_LongRAG/_info.json"
    #md_info_path = "_work/ctn2md_业绩案例_上汽内外饰DRE外包框架服务合同/_info.json"
    #md_info_path = "_work/ctn2md_业绩案例_上汽内外饰部CAD外包框架服务合同/_info.json"
    md_info_path = "_work/ctn2md_深度学习在视电阻率快速反演中的研究/_info.json"
    page_ndx = 3


    md_info = MdInfo(md_info_path)

    fname_json_result = md_info.get(MIFN.LP_FNAME_JSON_RESULT_NORMAL)

    with open(fname_json_result, 'r', encoding="utf8") as f:
        json_result = json.load(f)

    json_result0 = json_result[0]
    job_id = md_info.get_unique_job_id()
    pages = json_result0["pages"]
    page = pages[page_ndx]
    total_pages = len(pages)

    p2m = Page2Markdown(job_id, page, total_pages, md_info)
    p2m.analyse()
    fname_page = p2m.save_page_markdown()
    md_info.save()
    
    rich.print(fname_page)
