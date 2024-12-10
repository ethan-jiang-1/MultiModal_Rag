#import os
import sys
#import logging
#import rich

if './' not in sys.path:
    sys.path.append("./")

"""
返回是 bounds list, 每一个 bounds 如下：
(x_min, y_min, x_max, y_max)
#### **参数说明**
1. **`x_min`**: 
- 矩形左边界的 x 坐标。
- 表示该矩形区域在页面上的最左端位置。
2. **`y_min`**:
- 矩形下边界的 y 坐标。
- 表示该矩形区域在页面上的最下端位置。
3. **`x_max`**:
- 矩形右边界的 x 坐标。
- 表示该矩形区域在页面上的最右端位置。
4. **`y_max`**:
- 矩形上边界的 y 坐标。
- 表示该矩形区域在页面上的最上端位置。

#### **坐标系统**
- **绝对坐标**：
- 坐标基于 PDF 页面尺寸的绝对单位，通常是以点（point）为单位（1 点 = 1/72 英寸）。
- `(0, 0)` 通常是 PDF 页面左下角的起始点。
- `x` 值从左到右增加，`y` 值从下到上增加。
"""

def vllm_parse_non_text_rects_in_page_by_gpt(md_info, page, page_index, pname_page_name):
    return None 

def vllm_parse_non_text_rects_in_page_by_qwen(md_info, page, page_index, pname_page_name):
    return None
