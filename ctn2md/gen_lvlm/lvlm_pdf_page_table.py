
import sys
from typing import List # , Tuple, Optional  # , Dict
#import logging
#import rich

import fitz  # PyMuPDF
import shapely.geometry as sg
#from shapely.geometry.base import BaseGeometry
#from shapely.validation import explain_validity

if './' not in sys.path:
    sys.path.append("./")

from ctn2md.src.md_info_base import MdInfo

def detect_table_regions(
    md_info: MdInfo,
    page: fitz.Page,
    line_distance_ratio: float = 0.03,  # 线段合并的默认比例
    text_x_distance_ratio: float = 0.02,  # 水平方向文字吸附比例
    text_y_distance_ratio: float = 0.02,  # 垂直方向文字吸附比例
    short_line_ratio: float = 0.03       # 短线段的长度比例
) -> List[sg.box]:
    """
    检测由线段构成的表格区域，并吸附周围文字形成完整表格矩形。

    参数:
        page (fitz.Page): PDF 的单页对象。
        line_distance_ratio (float): 两条线段间的最大距离阈值（相对于页面宽度）。
        text_x_distance_ratio (float): 表格区域与文字块之间水平方向的最大吸附比例（相对于页面宽度）。
        text_y_distance_ratio (float): 表格区域与文字块之间垂直方向的最大吸附比例（相对于页面高度）。
        short_line_ratio (float): 用于过滤短线段的长度比例（相对于页面宽度）。

    返回:
        List[sg.box]: 包含文字的表格区域的矩形列表。
    """
    # 获取页面宽度和高度
    page_width, page_height = page.mediabox_size

    # 短线段长度的绝对阈值
    short_line_threshold = page_width * short_line_ratio

    # **步骤 1：提取绘制线段**
    drawings = page.get_drawings()

    # 忽略掉长度小于短线段阈值的水平直线
    def is_short_line(x): 
        return abs(x['rect'][3] - x['rect'][1]) < 1 and abs(x['rect'][2] - x['rect'][0]) < short_line_threshold 

    drawings = [drawing for drawing in drawings if not is_short_line(drawing)]

    # 提取短线条（表格线段）
    short_lines = [
        sg.box(*drawing['rect']) for drawing in drawings
        if abs(drawing['rect'][3] - drawing['rect'][1]) < 5 or abs(drawing['rect'][2] - drawing['rect'][0]) < 5
    ]

    # **步骤 2：合并短线条形成初步的表格区域**
    merged = True
    while merged:
        merged = False
        new_rect_list = []

        while short_lines:
            current = short_lines.pop(0)
            to_merge = []

            for other in short_lines:
                # 判断是否接近或相交
                if current.distance(other) < page_width * line_distance_ratio or current.intersects(other):
                    to_merge.append(other)

            # 合并当前矩形和需要合并的矩形
            for rect in to_merge:
                short_lines.remove(rect)
                current = sg.box(*current.union(rect).bounds)
                merged = True

            new_rect_list.append(current)

        short_lines = new_rect_list

    table_regions = short_lines  # 合并完成后，所有表格核心区域

    # **步骤 3：提取文字块并吸附到表格区域**
    text_blocks = [sg.box(*block[:4]) for block in page.get_text("blocks")]

    expanded_table_regions = []
    for table_rect in table_regions:
        # 扩展表格区域的边界
        expanded_table_rect = sg.box(
            table_rect.bounds[0] - page_width * text_x_distance_ratio,
            table_rect.bounds[1] - page_height * text_y_distance_ratio,
            table_rect.bounds[2] + page_width * text_x_distance_ratio,
            table_rect.bounds[3] + page_height * text_y_distance_ratio
        )
        
        # 合并扩展边界范围内的文字块
        for text_block in text_blocks:
            if expanded_table_rect.intersects(text_block):
                table_rect = sg.box(*table_rect.union(text_block).bounds)
        expanded_table_regions.append(table_rect)

    # 返回扩展后的表格区域
    return expanded_table_regions
