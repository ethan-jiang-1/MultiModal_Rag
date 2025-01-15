"""
表格处理器 - 专注于处理跨页表格的合并

主要功能:
1. 验证表格是否需要跨页合并
2. 执行跨页表格的合并操作
3. 保持表格结构的完整性
"""

from typing import List, Dict, Union, Tuple
import logging
from dotenv import load_dotenv
import os

load_dotenv()

from ctn2md.md_info.md_info_base import MdInfo
from ctn2md.gen_base.page_md_fusion.base import BaseProcessor
from ctn2md.gen_base.page_md_fusion.llm.da_schemas import TableRange

logger = logging.getLogger(__name__)

class TableProcessor(BaseProcessor):
    """表格处理器：专注于处理跨页表格的合并
    
    主要职责:
    1. 判断表格是否需要跨页合并
    2. 验证表格的连续性
    3. 执行表格合并操作
    """
    
    def process(self, pages: List[List[str]], actions: Dict) -> List[List[str]]:
        """处理跨页表格
        
        Args:
            pages: 所有页面的内容，每个页面是一个字符串列表
            actions: LLM分析得到的动作指令
        
        Returns:
            处理后的页面内容
        """
        if not actions.get("merge_actions"):
            return pages
            
        processed_pages = pages.copy()
        
        # 处理每个合并动作
        for action in actions["merge_actions"]:
            if action["type"] == "table" and self._is_cross_page_table(action):
                processed_pages = self._merge_table(
                    processed_pages,
                    action
                )
                
        return processed_pages
    
    def _get_range_info(self, range_info: Union[List[int], TableRange]) -> Tuple[int, int]:
        """获取范围信息
        
        Args:
            range_info: 可能是[start, end]列表或TableRange对象
            
        Returns:
            (start, end)元组
        """
        if isinstance(range_info, list):
            return range_info[0], range_info[1]
        return range_info.start, range_info.end
    
    def _is_header_range(self, range_info: Union[List[int], TableRange]) -> bool:
        """判断是否为表头范围
        
        Args:
            range_info: 可能是[start, end]列表或TableRange对象
            
        Returns:
            是否为表头
        """
        if isinstance(range_info, TableRange):
            return range_info.is_header
        return False
        
    def _is_cross_page_table(self, action: Dict) -> bool:
        """判断是否为需要跨页合并的表格
        
        Args:
            action: 合并动作信息，包含页码和行范围
            
        Returns:
            是否需要跨页合并
        """
        # 检查是否跨页
        if len(action["pages"]) <= 1:
            return False
            
        # 验证表格的连续性
        return self._validate_table_continuity(action)
        
    def _validate_table_continuity(self, action: Dict) -> bool:
        """验证表格的跨页连续性
        
        Args:
            action: 合并动作信息，包含页码和行范围
            
        Returns:
            表格是否连续
        """
        # 获取所有页码
        pages = sorted(action["pages"])
        
        # 检查页码连续性
        for i in range(len(pages) - 1):
            if pages[i + 1] - pages[i] > 1:
                logger.warning(f"表格页码不连续: {pages[i]} -> {pages[i + 1]}")
                return False
                
        # 检查每页表格内容的连续性
        prev_end = None
        for page_num in pages:
            ranges = action["line_ranges"].get(str(page_num), [])
            if not ranges:
                logger.warning(f"页面 {page_num} 未找到表格内容")
                return False
                
            # 检查当前页内表格片段的连续性
            for range_info in ranges:
                start, end = self._get_range_info(range_info)
                if prev_end is not None and start <= prev_end:
                    logger.warning(f"表格内容重叠: {prev_end} -> {start}")
                    return False
                prev_end = end
                
        return True
    
    def _merge_table(self, pages: List[List[str]], action: Dict) -> List[List[str]]:
        """合并跨页表格
        
        Args:
            pages: 所有页面内容，每个页面是一个字符串列表
            action: 合并动作信息，包含页码和行范围
            
        Returns:
            处理后的页面内容
        """
        # 1. 收集表格内容
        table_content = []
        header_content = []
        
        # 先收集表头内容
        for page_num in sorted(action["pages"]):
            page_idx = page_num - 1
            page = pages[page_idx]
            ranges = action["line_ranges"].get(str(page_num), [])
            for range_info in ranges:
                start, end = self._get_range_info(range_info)
                content = page[start-1:end]
                if self._is_header_range(range_info):
                    header_content.extend(content)
                else:
                    table_content.extend(content)
        
        # 如果有表头，确保它只出现一次
        if header_content:
            table_content = header_content + table_content
        
        # 2. 更新页面内容
        # 把完整表格放在第一页的开始位置
        first_page = action["pages"][0] - 1
        first_range = action["line_ranges"][str(action["pages"][0])][0]
        start, end = self._get_range_info(first_range)
        
        # 替换第一页的表格部分
        pages[first_page] = (
            pages[first_page][:start-1] +
            table_content +
            pages[first_page][end:]
        )
        
        # 删除其他页的表格部分
        for page_num in action["pages"][1:]:
            page_idx = page_num - 1
            ranges = action["line_ranges"][str(page_num)]
            for range_info in ranges:
                start, end = self._get_range_info(range_info)
                pages[page_idx] = (
                    pages[page_idx][:start-1] +
                    pages[page_idx][end:]
                )
        
        return pages

if __name__ == "__main__":
    from mmbase.utils.util_logging import setup_logger_handlers
    setup_logger_handlers()
    
    # 测试数据
    test_pages = [
        [  # 第1页
            "正文内容",
            "| 表头1 | 表头2 |",
            "| --- | --- |",
            "| 数据1 | 数据2 |"
        ],
        [  # 第2页
            "| 数据3 | 数据4 |",
            "| 数据5 | 数据6 |",
            "正文继续"
        ]
    ]
    
    test_actions = {
        "merge_actions": [
            {
                "type": "table",
                "pages": [1, 2],
                "line_ranges": {
                    "1": [
                        TableRange(
                            start=2,
                            end=4,
                            is_header=True,
                            has_separator=True
                        )
                    ],
                    "2": [
                        TableRange(
                            start=1,
                            end=2,
                            is_header=False,
                            has_separator=False
                        )
                    ]
                },
                "confidence": 0.95,
                "is_cross_page": True
            }
        ]
    }
    
    # 创建测试目录
    test_dir = "_output/test_table_processor"
    os.makedirs(test_dir, exist_ok=True)
    
    # 初始化 MdInfo
    md_info = MdInfo(test_dir)
    
    processor = TableProcessor(md_info)
    result = processor.process(test_pages, test_actions)
    
    # 打印结果
    for idx, page in enumerate(result, 1):
        print(f"\n=== 处理后的第{idx}页 ===")
        print("\n".join(page)) 