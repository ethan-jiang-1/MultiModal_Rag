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


def get_rect_list_paints(page: fitz.Page) -> List[sg.box]:
    """
    提取 PDF 页面中可能是绘制图片（如图表、柱状图）的区域。

    综合以下特征：
    - 检测填充颜色的矩形。
    - 分析多边形或路径的复杂性。
    - 检测宽度一致的相邻矩形（柱状图）。
    - 基于绘图密集度的区域识别。

    参数:
        page (fitz.Page): PDF 的单页对象。
    
    返回:
        List[sg.box]: 可能是绘制图片的矩形区域列表。
    """
    drawings = page.get_drawings()
    
    # 忽略掉长度小于30的水平直线
    is_short_line = lambda x: abs(x['rect'][3] - x['rect'][1]) < 1 and abs(x['rect'][2] - x['rect'][0]) < 30 # noqa
    drawings = [drawing for drawing in drawings if not is_short_line(drawing)]

    detected_rects = []

    # 方法 1: 检测填充颜色的矩形
    filled_rects = [sg.box(*drawing['rect']) for drawing in drawings if drawing.get('fill') is not None]
    detected_rects.extend(filled_rects)

    # 方法 2: 检测复杂路径
    complex_drawings = [sg.box(*drawing['rect']) for drawing in drawings if len(drawing.get('points', [])) > 10]
    detected_rects.extend(complex_drawings)

    # 方法 3: 检测宽度一致的相邻矩形（柱状图特征）
    bar_charts = _rlp_detect_bar_charts([sg.box(*drawing['rect']) for drawing in drawings])
    detected_rects.extend(bar_charts)

    # 方法 4: 检测高密度的区域
    dense_regions = _rlp_detect_dense_regions([sg.box(*drawing['rect']) for drawing in drawings], drawings)
    detected_rects.extend(dense_regions)

    # 合并所有矩形区域，去除重叠或靠近的矩形
    merged_rects = _rlp_merge_rects(detected_rects, distance=10)

    # 返回最终的矩形列表
    return merged_rects


def _rlp_detect_bar_charts(rect_list: List[sg.box]) -> List[sg.box]:
    """
    检测柱状图区域：通过检测宽度一致且相邻的矩形。
    """
    bar_charts = []
    for rect in rect_list:
        widths = [r.bounds[2] - r.bounds[0] for r in rect_list]
        width_set = set(widths)
        if len(width_set) == 1 and len(rect_list) > 5:  # 宽度一致且矩形较多
            bar_charts.extend(rect_list)
            break
    return bar_charts


def _rlp_detect_dense_regions(rect_list: List[sg.box], drawings: List) -> List[sg.box]:
    """
    检测高密度区域：根据一个区域内的绘图元素密集度。
    """
    dense_regions = []
    for rect in rect_list:
        # 统计每个矩形内的绘图元素数量
        density = sum(1 for drawing in drawings if rect.contains(sg.box(*drawing['rect'])))
        if density > 10:  # 假设密度阈值为 10
            dense_regions.append(rect)
    return dense_regions


def _rlp_merge_rects(rect_list: List[sg.box], distance: float = 10) -> List[sg.box]:
    """
    合并相邻或重叠的矩形区域。
    """
    merged = True
    while merged:
        merged = False
        new_rect_list = []
        while rect_list:
            rect = rect_list.pop(0)
            for other_rect in rect_list:
                if rect.distance(other_rect) < distance or rect.intersects(other_rect):
                    rect = sg.box(*(rect.union(other_rect).bounds))
                    rect_list.remove(other_rect)
                    merged = True
            new_rect_list.append(rect)
        rect_list = new_rect_list
    return rect_list
