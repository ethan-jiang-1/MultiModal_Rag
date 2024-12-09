#import os
import sys
#import re
from typing import List # , Tuple, Optional  # , Dict
#import logging
#import rich

import fitz  # PyMuPDF
import shapely.geometry as sg
#from shapely.geometry.base import BaseGeometry
#from shapely.validation import explain_validity

if './' not in sys.path:
    sys.path.append("./")

def detect_table_regions(page: fitz.Page) -> List[sg.box]:
    """
    检测由线段构成的表格区域，通过线段聚合识别网格结构。

    参数:
        page (fitz.Page): PDF 的单页对象。

    返回:
        List[sg.box]: 表格区域的矩形列表。
    """
    drawings = page.get_drawings()
    
    # 忽略掉长度小于30的水平直线
    is_short_line = lambda x: abs(x['rect'][3] - x['rect'][1]) < 1 and abs(x['rect'][2] - x['rect'][0]) < 30 # noqa
    drawings = [drawing for drawing in drawings if not is_short_line(drawing)]

    # 提取短线条（表格线段）
    short_lines = [
        sg.box(*drawing['rect']) for drawing in drawings
        if abs(drawing['rect'][3] - drawing['rect'][1]) < 5 or abs(drawing['rect'][2] - drawing['rect'][0]) < 5
    ]

    # 合并短线条形成表格区域
    table_regions = _merge_all_rects_for_tables(short_lines)
    return table_regions

def _merge_all_rects_for_tables(short_lines: List[sg.box], distance: float = 5) -> List[sg.box]:
    """
    合并短线段形成表格区域矩形。

    参数:
        short_lines (List[sg.box]): 表示线段的矩形列表。
        distance (float): 两条线段间的最大距离阈值，用于判断是否需要合并。

    返回:
        List[sg.box]: 合并后的表格区域矩形列表。
    """
    merged = True
    while merged:
        merged = False
        new_rect_list = []

        while short_lines:
            current = short_lines.pop(0)
            to_merge = []

            for other in short_lines:
                # 判断是否接近或相交
                if current.distance(other) < distance or current.intersects(other):
                    to_merge.append(other)

            # 合并当前矩形和需要合并的矩形
            for rect in to_merge:
                short_lines.remove(rect)
                current = sg.box(*current.union(rect).bounds)
                merged = True

            new_rect_list.append(current)

        short_lines = new_rect_list

    return short_lines
