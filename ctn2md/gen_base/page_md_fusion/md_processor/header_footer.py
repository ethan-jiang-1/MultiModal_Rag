"""
页眉页脚处理器 - 处理文档页眉页脚
"""

from typing import List, Optional
import logging
from dotenv import load_dotenv

load_dotenv()

from ctn2md.md_info.md_info_base import MdInfo
from ctn2md.gen_base.page_md_fusion.llm_heading.da_schemas_heading import HeadingRemoveInfo

logger = logging.getLogger(__name__)

class HeaderFooterProcessor:
    """页眉页脚处理器：处理文档页眉页脚"""
    
    def __init__(self, md_info: MdInfo):
        """初始化
        
        Args:
            md_info: MD信息对象
        """
        self.md_info = md_info
            
    def process(self, pages_content: List[List[str]], remove_infos: List[HeadingRemoveInfo]) -> Optional[List[List[str]]]:
        """处理页眉页脚
        
        Args:
            pages_content: 所有页面的内容
            remove_infos: 需要删除的页眉页脚信息
                
        Returns:
            处理后的页面内容,如果处理失败则返回None
        """
        try:
            # 1. 创建页面内容副本
            processed_pages = []
            for page in pages_content:
                processed_pages.append(page.copy())
                
            # 2. 如果没有需要删除的内容,直接返回
            if not remove_infos:
                return processed_pages
                
            # 3. 处理每个删除请求
            for info in remove_infos:
                page_idx = info.page - 1
                
                # 3.1 检查页码是否有效
                if page_idx < 0 or page_idx >= len(processed_pages):
                    logger.warning(f"Invalid page index {page_idx + 1}")
                    continue
                    
                # 3.2 删除指定行
                for line_idx in sorted(info.lines, reverse=True):
                    # 调整为0-based索引
                    line_idx = line_idx - 1
                    
                    # 检查行号是否有效
                    if line_idx < 0 or line_idx >= len(processed_pages[page_idx]):
                        logger.warning(f"Invalid line index {line_idx + 1} in page {page_idx + 1}")
                        continue
                        
                    # 删除该行
                    del processed_pages[page_idx][line_idx]
                    
            return processed_pages
            
        except Exception as e:
            logger.error(f"Error during header/footer processing: {e}", exc_info=True)
            return None

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
    
    # 构造删除信息
    test_remove_infos = [
        HeadingRemoveInfo(
            page=1,
            lines=[1, 3],
            reason="header"
        ),
        HeadingRemoveInfo(
            page=2,
            lines=[1, 3],
            reason="footer"
        )
    ]
    
    # 测试处理
    processor = HeaderFooterProcessor(md_info)
    result = processor.process(test_pages, test_remove_infos)
    
    # 打印结果
    for idx, page in enumerate(result, 1):
        print(f"\n=== 处理后的第{idx}页 ===")
        print("\n".join(page)) 