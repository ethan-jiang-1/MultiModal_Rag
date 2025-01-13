import re
from typing import List
from dotenv import load_dotenv
load_dotenv()

from ctn2md.gen_markitdown.img_ref.models import ImageReference, IMG_REF_PATTERN


class ImageReferenceScanner:
    """扫描markdown文件中的图片引用"""
    
    def __init__(self, context_chars: int = 200):
        """初始化扫描器
        
        Args:
            context_chars: 提取图片前后的上下文字符数
        """
        self.context_chars = context_chars
        self._pattern = IMG_REF_PATTERN
    
    def scan_file(self, file_path: str) -> List[ImageReference]:
        """扫描文件中的图片引用
        
        Args:
            file_path: markdown文件路径
            
        Returns:
            图片引用列表
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return self.scan_content(content)
    
    def scan_content(self, content: str) -> List[ImageReference]:
        """扫描文本内容中的图片引用
        
        Args:
            content: markdown文本内容
            
        Returns:
            图片引用列表
        """
        references = []
        line_positions = self._get_line_positions(content)
        
        for match in re.finditer(self._pattern, content):
            position = match.start()
            figure_name = match.group(1)
            ref_name = match.group(2)
            description = match.group(3) or ""
            
            line_number = self._get_line_number(position, line_positions)
            context_before = self._get_context(content, position - self.context_chars, position)
            context_after = self._get_context(content, position + len(match.group(0)), 
                                           position + len(match.group(0)) + self.context_chars)
            
            ref = ImageReference(
                ref_name=ref_name,
                position=position,
                context_before=context_before,
                context_after=context_after,
                line_number=line_number,
                figure_name=figure_name,
                image_description=description,
                relevance_score=0.0
            )
            references.append(ref)
            
        return references
    
    def _get_line_positions(self, content: str) -> List[int]:
        """获取每行的起始位置"""
        positions = [0]
        for match in re.finditer(r'\n', content):
            positions.append(match.end())
        return positions
    
    def _get_line_number(self, position: int, line_positions: List[int]) -> int:
        """根据位置获取行号"""
        for i, pos in enumerate(line_positions):
            if position < pos:
                return i
        return len(line_positions)
    
    def _get_context(self, content: str, start: int, end: int) -> str:
        """获取指定范围的上下文"""
        start = max(0, start)
        end = min(len(content), end)
        return content[start:end].strip() 
    
