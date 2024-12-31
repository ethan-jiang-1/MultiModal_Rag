import sys
import fitz  # PyMuPDF


if './' not in sys.path:
    sys.path.append("./")


def draw_redrect_on_page(page:fitz.Page, 
                         fitz_rect:fitz.Rect, 
                         fname_rect_name:str) -> str:
    # 计算文本起始位置
    text_x = fitz_rect.x0 + 4  # 增加一些左侧内边距
    text_y = fitz_rect.y0 + 14  # 增加顶部内边距

    # 动态计算文字的实际尺寸
    font_size = 12  # 调大字体大小
    color_red = (1, 0, 0)
    font_name = "helv"  # 默认字体

    # 使用 TextWriter 来测量文字宽度
    font = fitz.Font(fontname=font_name)  # 创建字体对象
    text_width = font.text_length(fname_rect_name, fontsize=font_size)  # 计算文本宽度
    text_height = font_size  # 字体大小基本等于高度

    # 动态设置白底矩形的大小，比红字大一些
    padding = 4  # 增加白底的间距
    text_rect = fitz.Rect(
        text_x - padding,  # 左侧扩展
        text_y - text_height - padding,  # 上侧扩展
        text_x + text_width + padding,  # 右侧扩展
        text_y + padding  # 下侧扩展
    )

    # 绘制白底
    page.draw_rect(text_rect, color=(1, 1, 1), fill=(1, 1, 1))  # 白色背景

    # 绘制白底的小红框，使上边和左边与大框重叠
    small_red_rect = fitz.Rect(
        fitz_rect.x0 - 1,  # 左侧对齐大框的左侧
        fitz_rect.y0 - 1,  # 上侧对齐大框的上侧
        text_rect.x1 + 1,  # 右侧略微扩展
        text_rect.y1 + 1   # 下侧略微扩展
    )
    page.draw_rect(small_red_rect, color=(1, 0, 0), width=1)  # 绘制小红框

    # 插入文字
    page.insert_text(
        (text_x, text_y),
        fname_rect_name,
        fontsize=font_size,
        color=color_red,
        fontname=font_name
    )

    # 最后绘制最外层红色矩形框
    big_fitz_rect = fitz.Rect(fitz_rect.x0 - 1, fitz_rect.y0 - 1, fitz_rect.x1 + 1, fitz_rect.y1 + 1)
    page.draw_rect(big_fitz_rect, color=(1, 0, 0), width=1)  # 绘制最外红框

    return fname_rect_name
