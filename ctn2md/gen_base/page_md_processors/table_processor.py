"""
表格处理器 - 处理跨页表格的合并
"""

from typing import List, Dict
import logging
from dotenv import load_dotenv

load_dotenv()

from ctn2md.src.md_info_base import MdInfo
from ctn2md.gen_base.page_md_processors.base import BaseProcessor

logger = logging.getLogger(__name__)

class TableProcessor(BaseProcessor):
    """表格处理器：执行LLM分析得到的表格合并动作"""
    
    def process(self, pages: List[List[str]], actions: Dict) -> List[List[str]]:
        """处理跨页表格
        
        Args:
            pages: 所有页面的内容
            actions: LLM分析得到的动作指令
        
        Returns:
            处理后的页面内容
        """
        if not actions.get("merge_actions"):
            return pages
            
        processed_pages = pages.copy()
        
        # 处理每个合并动作
        for action in actions["merge_actions"]:
            if action["type"] == "table":
                processed_pages = self._merge_table(
                    processed_pages,
                    action
                )
                
        return processed_pages
    
    def _merge_table(self, pages: List[List[str]], action: Dict) -> List[List[str]]:
        """合并跨页表格"""
        # 1. 收集表格内容
        table_content = []
        for page_num, ranges in action["line_ranges"].items():
            page_idx = int(page_num) - 1
            page = pages[page_idx]
            for start, end in ranges:
                # 注意：行号是1-based，需要转换
                table_content.extend(page[start-1:end])
        
        # 2. 更新页面内容
        # 把完整表格放在第一页的开始位置
        first_page = int(action["pages"][0]) - 1
        first_range = action["line_ranges"][str(action["pages"][0])][0]
        start_line = first_range[0] - 1
        
        # 替换第一页的表格部分
        pages[first_page] = (
            pages[first_page][:start_line] +
            table_content +
            pages[first_page][first_range[1]:]
        )
        
        # 删除其他页的表格部分
        for page_num in action["pages"][1:]:
            page_idx = page_num - 1
            ranges = action["line_ranges"][str(page_num)]
            for start, end in ranges:
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
                    "1": [[2, 4]],  # 第1页的表格部分
                    "2": [[1, 2]]   # 第2页的表格部分
                }
            }
        ]
    }
    
    # 测试处理
    json_path = "_output/test_doc/_info.json"
    md_info = MdInfo.from_json(json_path)
    
    processor = TableProcessor(md_info)
    result = processor.process(test_pages, test_actions)
    
    # 打印结果
    for idx, page in enumerate(result, 1):
        print(f"\n=== 处理后的第{idx}页 ===")
        print("\n".join(page)) 