import os
import shutil
import re
import logging
from typing import Any, Optional, Tuple, Union
from dotenv import load_dotenv
import rich
import mammoth
from mammoth.documents import Document, Paragraph, Run, Text
from ctn2md.src.md_info_base import MdInfo
from mmbase.utils.util_logging import setup_logger_handlers
from pathlib import Path

load_dotenv()

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

# 创建全局解析器实例
_heading_parser = ContentBasedHeadingParser()

class ImageExporter:
    """处理文档中的图片导出"""
    _output_dir: str = ""
    _doc_unique_id: str = ""
    _image_counter:int = 0
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def export_image(self, image_element: Any) -> Optional[Paragraph]:
        """导出图片并返回对应的 Markdown 图片引用段落
        
        Args:
            image_element: 文档中的图片元素
            output_dir: 输出目录
            doc_name: 文档名称（用于创建图片子目录）
            
        Returns:
            包含图片引用的段落，如果处理失败则返回 None
        """
        try:
            # 确保图片目录存在
            image_dir = Path(self.output_dir) 
            
            # 生成图片文件名
            self._image_counter += 1
            image_filename = f"{self._doc_unique_id}_{self._image_counter}{self._get_image_extension(image_element)}"
            image_path = image_dir / image_filename
            
            # 保存图片
            with image_element.open() as image_bytes, open(image_path, 'wb') as f:
                f.write(image_bytes.read())
            
            self.logger.info(f"Exported image to: {image_path}")
            
            # 创建图片引用段落
            relative_path = f"{image_filename}"
            alt_text = image_element.alt_text or f"image_{self._image_counter}"
            
            return Paragraph(
                children=[Run(
                    children=[Text(f"![{alt_text}]({relative_path})")],
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
            
        except Exception as e:
            self.logger.error(f"Failed to export image: {e}")
            return None
    
    def _get_image_extension(self, image_element: Any) -> str:
        """根据图片内容类型获取扩展名"""
        content_type = image_element.content_type
        if content_type == "image/png":
            return ".png"
        elif content_type == "image/jpeg":
            return ".jpg"
        elif content_type == "image/gif":
            return ".gif"
        else:
            return ".png"  # 默认使用 png

# 创建全局实例
_image_exporter = ImageExporter()

def _mammoth_transform_document(element: Union[Document, Paragraph, Any]) -> Document:
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
            children=[_mammoth_transform_document(child) for child in element.children],
            notes=[],
            comments=[]
        )
    elif isinstance(element, Paragraph):
        # 提取段落中的所有文本
        text_parts = []
        for child in element.children:
            if isinstance(child, Run):
                for text_element in child.children:
                    if isinstance(text_element, Text):
                        text_parts.append(text_element.value)
                    elif hasattr(text_element, 'alt_text'):  # 处理图片
                        # 保持图片的处理
                        return element
        
        text = "".join(text_parts)
        logger.info(f"Processing text: {text}")
        
        # 如果段落有预定义样式，保持原样
        if element.style_name and element.style_name != "dingdocnormal":
            logger.debug(f"Keeping original style: {element.style_name}")
            return element
            
        # 否则尝试解析标题
        level, title_text = _heading_parser.parse_heading(text)
        if level is not None:
            logger.info(f"Found heading level {level}: {title_text}")
            return _heading_parser.create_heading_paragraph(level, title_text)
        else:
            logger.info(f"Regular paragraph: {text}")
            return _heading_parser.create_normal_paragraph(text)
    
    # 保持其他元素不变（包括图片）
    return element


def gen_md_from_doc(md_info: 'MdInfo', pname_unique_doc: str) -> str:
    """从Word文档生成Markdown文件
    
    Args:
        md_info: Markdown信息对象
        pname_unique_doc: 唯一的文档路径
        
    Returns:
        生成的Markdown文件路径
    """
    logger = logging.getLogger(__name__)
    
    # 设置样式映射
    style_map = """
    p[style-name='heading 1'] => h1:fresh
    p[style-name='heading 2'] => h2:fresh
    p[style-name='heading 3'] => h3:fresh
    p[style-name='heading 4'] => h4:fresh
    p[style-name='heading 5'] => h5:fresh
    p[style-name='heading 6'] => h6:fresh
    p[style-name='标题 1'] => h1:fresh
    p[style-name='标题 2'] => h2:fresh
    p[style-name='标题 3'] => h3:fresh
    p[style-name='标题 4'] => h4:fresh
    p[style-name='标题 5'] => h5:fresh
    p[style-name='标题 6'] => h6:fresh
    p[style-name='Title'] => h1:fresh
    p[style-name='Subtitle'] => h2:fresh
    p[style-name='Normal'] => p:fresh
    p[style-name='dingdocnormal'] => p:fresh
    """
    
    # 转换文档
    logger.info(f"Converting document: {pname_unique_doc}")
    logger.info(f"Using style map:\n{style_map}")

    ImageExporter._image_counter = 0
    ImageExporter._doc_unique_id = md_info.get_unique_job_id()
    ImageExporter._output_dir = md_info.get_out_dir()
    
    result = mammoth.convert_to_markdown(
        pname_unique_doc,
        transform_document=_mammoth_transform_document,
        style_map=style_map
    )
    
    # 处理警告
    for warning in result.messages:
        logger.warning(warning)
    
    # 写入结果
    pathname_step0 = md_info.name_step_pathname(0) 
    with open(pathname_step0, "w", encoding="utf-8") as f:
        f.write(result.value)
    
    logger.info(f"Markdown file generated: {pathname_step0}")
    return pathname_step0

def generate_markdown_markitdown(md_info:MdInfo) -> str:
    setup_logger_handlers()

    pname_unique_doc = os.path.join(
        md_info.get_out_dir(),
        f"{md_info.get_unique_job_id()}.docx"
    )
    shutil.copy(md_info.get_doc_pathname(), pname_unique_doc)

    # 生成Markdown
    pathname_step0 = gen_md_from_doc(md_info, pname_unique_doc)
    md_info.add_step_into_md_info_mdflow(pathname_step0, "markitdown")
    return pathname_step0


if __name__ == "__main__":
    # 设置日志
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    setup_logger_handlers()

    # 获取文档信息
    md_info = MdInfo("_output/ctn2md_misc__成都交通局_华为说明_mid/_info.json")

    # 生成Markdown
    ret = generate_markdown_markitdown(md_info)
    rich.print(ret)