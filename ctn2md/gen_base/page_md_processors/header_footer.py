"""
页眉页脚处理器 - 基于LLM分析结果执行清理
"""

from typing import List, Dict
import logging
from dotenv import load_dotenv

load_dotenv()

from ctn2md.md_info.md_info_base import MdInfo
from ctn2md.gen_base.page_md_processors.base import BaseProcessor

logger = logging.getLogger(__name__)

class HeaderFooterProcessor(BaseProcessor):
    """页眉页脚处理器：执行LLM分析得到的删除动作"""
    
    def process(self, pages: List[List[str]], actions: Dict) -> List[List[str]]:
        """处理页眉页脚
        
        Args:
            pages: 所有页面的内容
            actions: LLM分析得到的动作指令
        
        Returns:
            处理后的页面内容
        """
        if not actions.get("remove_actions"):
            return pages
            
        processed_pages = pages.copy()
        
        # 执行删除动作
        for action in actions["remove_actions"]:
            if action["reason"] in ["页眉", "页脚"]:
                page_idx = action["page"] - 1
                # 删除指定行
                processed_pages[page_idx] = [
                    line for idx, line in enumerate(processed_pages[page_idx], 1)
                    if idx not in action["lines"]
                ]
                
        return processed_pages

if __name__ == "__main__":
    from mmbase.utils.util_logging import setup_logger_handlers
    setup_logger_handlers()
    
    # 测试代码
    json_path = "_output/test_doc/_info.json"
    md_info = MdInfo.from_json(json_path)
    
    # 测试数据
    test_pages = [
        [  # 第1页
            "页眉",
            "正文内容",
            "页脚"
        ],
        [  # 第2页
            "页眉",
            "更多内容",
            "页脚"
        ]
    ]
    
    test_actions = {
        "remove_actions": [
            {
                "page": 1,
                "lines": [1, 3],
                "reason": "页眉"
            },
            {
                "page": 2,
                "lines": [1, 3],
                "reason": "页眉"
            }
        ]
    }
    
    # 测试处理
    processor = HeaderFooterProcessor(md_info)
    result = processor.process(test_pages, test_actions)
    
    # 打印结果
    for idx, page in enumerate(result, 1):
        print(f"\n=== 处理后的第{idx}页 ===")
        print("\n".join(page)) 