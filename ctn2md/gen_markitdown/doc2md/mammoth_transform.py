import logging
import re
from typing import Any, Optional, Tuple, Union
from dotenv import load_dotenv
from mammoth.documents import Document, Paragraph, Run, Text

from ctn2md.gen_markitdown.doc2md.mammoth_style_map import get_known_heading_map    
#from rich import print

load_dotenv()

from ctn2md.gen_markitdown.doc2md.mammoth_image_exporter import ImageExporter

logger = logging.getLogger(__name__)

# Type aliases
HeadingLevel = Optional[int]
HeadingInfo = Tuple[HeadingLevel, str]


class HeadingStack:
    """用于跟踪文档标题层级的栈结构"""
    
    def __init__(self):
        self._stack = []
        self.logger = logging.getLogger(__name__)
    
    def push(self, level: int, text: str):
        """将新的标题压入栈中"""
        while self._stack and self._stack[-1][0] >= level:
            self._stack.pop()
        self._stack.append((level, text))
        self.logger.debug(f"Pushed heading: {level} - {text}")
        self.logger.debug(f"Current stack: {self._stack}")
    
    def get_current_level(self) -> Optional[int]:
        """获取当前标题层级"""
        return self._stack[-1][0] if self._stack else None
    
    def get_parent_level(self) -> Optional[int]:
        """获取父标题层级"""
        return self._stack[-2][0] if len(self._stack) > 1 else None
    
    def suggest_next_level(self, text: str) -> int:
        """根据上下文建议下一个标题的层级"""
        current = self.get_current_level()
        parent = self.get_parent_level()
        
        if not current:
            return 1
        
        # 如果文本格式明显表明是某个层级，则使用该层级
        if re.match(r'^[一二三四五六七八九十]+、', text):
            return 1
        elif re.match(r'^（[一二三四五六七八九十]+）', text):
            return 2
        elif re.match(r'^\d+[、.]', text):
            return 3
        
        # 否则根据上下文推断
        if parent is None:
            return current + 1 if current < 6 else current
        else:
            return min(parent + 1, 6)

class ContentBasedHeadingParser:
    """基于内容的标题解析器，用于处理没有预定义样式的段落
    
    支持的标题格式:
    1. 一级标题: 中文数字 + "、" (如: 一、二、)
    2. 二级标题: 括号中文数字 (如: （一）（二）)
    3. 三级标题: 数字 + "、" 或 数字.数字 (如: 1、2、 或 1.1)
    4. 图表标题: "图"或"表" + 数字
    """
    
    _PATTERNS = {
        'level1': r'^[一二三四五六七八九十]+、',
        'level2': r'^（[一二三四五六七八九十]+）',
        'level3': r'^(?:\d+[、.]|\d+\.\d+)',
        'figure': r'^(图|表)\d+[\s\-_]*',
    }
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._heading_stack = HeadingStack()
    
    def extract_title_text(self, text: str) -> str:
        """提取标题文本，去除编号等前缀"""
        text = text.strip()
        # 如果包含换行或句号，只取第一部分
        parts = re.split(r'[。\n]', text)
        return parts[0].strip()
    
    def parse_heading(self, text: str) -> HeadingInfo:
        """解析文本，判断是否是标题以及标题级别"""
        if not text or not text.strip():
            return None, text
            
        text = text.strip()
        self.logger.debug(f"Parsing text for heading: {text}")
        
        # 检查是否是图表标题
        if re.match(self._PATTERNS['figure'], text):
            return 3, text
            
        # 检查其他标题模式
        clean_text = self.extract_title_text(text)
        
        if re.match(self._PATTERNS['level1'], text):
            level = 1
        elif re.match(self._PATTERNS['level2'], text):
            level = 2
        elif re.match(self._PATTERNS['level3'], text):
            level = 3
        else:
            return None, text
            
        self._heading_stack.push(level, clean_text)
        return level, clean_text
    
    def create_heading_paragraph(self, level: int, text: str) -> Paragraph:
        """创建标题段落"""
        self.logger.debug(f"Creating heading paragraph: level {level} - {text}")
        return Paragraph(
            children=[Run(
                children=[Text(text)],
                style_id=None,
                style_name=None,
                is_bold=False,
                is_italic=False,
                is_underline=False,
                is_strikethrough=False,
                is_all_caps=False,
                is_small_caps=False,
                vertical_alignment=None,
                font=None,
                font_size=None,
                highlight=None
            )],
            style_id=f"heading{level}",
            style_name=f"heading {level}",
            numbering=None,
            alignment=None,
            indent=None
        )
    
    def create_normal_paragraph(self, text: str) -> Paragraph:
        """创建普通段落"""
        self.logger.debug(f"Creating normal paragraph: {text}")
        return Paragraph(
            children=[Run(
                children=[Text(text)],
                style_id=None,
                style_name=None,
                is_bold=False,
                is_italic=False,
                is_underline=False,
                is_strikethrough=False,
                is_all_caps=False,
                is_small_caps=False,
                vertical_alignment=None,
                font=None,
                font_size=None,
                highlight=None
            )],
            style_id="normal",
            style_name="Normal",
            numbering=None,
            alignment=None,
            indent=None
        )
    
def convert_heading_paragraph_with_style_name(element: Paragraph) -> Paragraph:
    # 对于有style_name的段落，我们想办法映射到 style_id 为 heading1, heading2, heading3 等  
    style_name = element.style_name
    # 如果 style_id 为 heading1, heading2, heading3 等，则保持原样  
    # 否则，我们尝试映射到 style_id 为 heading1, heading2, heading3 等
    # 尝试从style_name映射到heading1-6的style_id
    # 常见的标题样式名称映射

    # 尝试从映射表中获取对应的style_id
    known_heading_map = get_known_heading_map()
    if style_name.lower() in known_heading_map:
        style_id = known_heading_map[style_name.lower()]
    elif style_name in known_heading_map:
        style_id = known_heading_map[style_name]
    if style_name.startswith("heading"):
        style_id = style_name
    else:
        style_id = None
    if style_id is not None:
        element.style_id = style_id
    return element

# 创建全局实例
_heading_parser = ContentBasedHeadingParser()

def mammoth_transform_document(element: Union[Document, Paragraph, Any]) -> Document:
    """转换文档元素，处理标题层级和内容转换
    
    Args:
        element: 要转换的文档元素，可以是 Document、Paragraph 或其他类型
        
    Returns:
        转换后的文档元素
    """
    logger = logging.getLogger(__name__)
    
    if isinstance(element, Document):
        logger.info("Processing document")
        return Document(
            children=[mammoth_transform_document(child) for child in element.children],
            notes=[],
            comments=[]
        )
    elif isinstance(element, Paragraph):
        # 提取段落中的所有文本和图片
        text_parts = []
        has_image = False
        image_paragraph = None
        
        for child in element.children:
            if isinstance(child, Run):
                for text_element in child.children:
                    if isinstance(text_element, Text):
                        text_parts.append(text_element.value)
                    elif hasattr(text_element, 'alt_text'):  # 检测到Word文档中的内嵌图片
                        has_image = True
                        # ImageExporter.export_image() 处理内嵌图片，应返回以下格式的 Paragraph 对象:
                        # - 如果成功导出图片:
                        #   返回包含图片Markdown语法的段落，格式为: ![alt_text](new_image_path)
                        #   其中 new_image_path 是导出后的图片相对路径
                        # - 如果导出失败:
                        #   返回 None，这样后续代码会继续处理其他内容
                        image_paragraph = ImageExporter.export_image(text_element)
                        if image_paragraph:
                            # 如果成功获得图片段落，立即返回，不再处理该段落中的其他内容
                            # 这是因为mammoth将每个图片都视为独立段落处理
                            return image_paragraph
        
        # 如果这是包含图片的段落且已成功处理，避免重复处理
        if has_image and image_paragraph:
            return image_paragraph
            
        # 处理普通文本段落
        text = "".join(text_parts)
        logger.info(f"Processing text: {text}")
        
        # 如果段落有预定义样式，保持原样
        if element.style_name and element.style_name != "dingdocnormal":
            logger.debug(f"Keeping original style: {element.style_name}")
            return convert_heading_paragraph_with_style_name(element)
            
        # 否则尝试解析标题
        level, title_text = _heading_parser.parse_heading(text)
        if level is not None:
            logger.info(f"Found heading level {level}: {title_text}")
            return _heading_parser.create_heading_paragraph(level, title_text)
        else:
            logger.info(f"Regular paragraph: {text}")
            return _heading_parser.create_normal_paragraph(text)
    
    # 保持其他元素不变
    return element