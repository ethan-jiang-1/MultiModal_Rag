"""
页眉页脚处理器 - 处理文档页眉页脚
"""

import logging
from typing import List, Optional
from dotenv import load_dotenv

load_dotenv()

from ctn2md.md_info.md_info_base import MdInfo
from ctn2md.gen_base.page_md_fusion.llm_heading.da_schemas_heading import HeadingRemoveInfo, HeadingHeaderPattern

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
    import os
    import json
    from mmbase.utils.util_logging import setup_logger_handlers
    from ctn2md.md_info.md_info_base import MIFN
    from ctn2md.md_info.md_info_ctrl import _MIB_INFO_VER
    
    # 设置日志
    setup_logger_handlers()
    logger.info("Starting header/footer processor test...")
    
    # 准备测试目录
    test_dir = "_output/test_header_footer"
    info_path = os.path.join(test_dir, "_info.json")
    os.makedirs(test_dir, exist_ok=True)
    
    # 创建测试用的 _info.json
    test_info = {
        MIFN.VERSION: _MIB_INFO_VER,
        MIFN.GEN_ENGINE: "test",
        MIFN.PATHNAME_ORG_DOC: os.path.join(test_dir, "test.md"),
        MIFN.PATHNAME_SRC_DOC: os.path.join(test_dir, "test.md"),
        MIFN.FNAME_ORG_DOC: "test.md",
        MIFN.DOC_UNIQUE_ID: "test_123",
        MIFN.DOC_CTN_TYPE: "markdown",
        MIFN.DOC_NAME_TITLE: "Test Document",
        MIFN.FNAMES_MD_PAGES: ["page_1.md", "page_2.md", "page_3.md", "page_4.md"]
    }
    with open(info_path, "w", encoding="utf-8") as f:
        json.dump(test_info, f, ensure_ascii=False, indent=2)
    logger.info(f"Created test info file at: {info_path}")
    
    # 创建测试数据
    test_pages = [
        [  # 第1页 - 标题页（带版权信息）
            "机密文件",           # 页眉1
            "内部文档 v2.0",      # 页眉2
            "",
            "# 系统设计方案",
            "版本: 1.0",
            "",
            "Copyright © 2024",  # 页脚1
            "页码: 1/8"          # 页脚2
        ],
        [  # 第2页 - 目录页（带分隔线）
            "系统设计方案",       # 页眉
            "---",              # 分隔线
            "## 目录",
            "",
            "1. 系统概述",
            "2. 系统架构",
            "3. 详细设计",
            "",
            "---",              # 分隔线
            "第2页"             # 页脚
        ],
        [  # 第3页 - 正文页（带注释和警告）
            "系统设计方案",       # 页眉
            "修订历史",          # 子页眉
            "",
            "### 2.1.1 详细设计",
            "各层详细设计如下：",
            "1. 表示层：负责...",
            "2. 业务层：包含...",
            "",
            "警告：请勿外传",     # 页脚1
            "第3页"             # 页脚2
        ],
        [  # 第4页 - 错误页（页码超出范围）
            "系统设计方案",
            "## 无效内容",
            "第999页"
        ]
    ]
    
    # 构造删除信息
    remove_infos = [
        HeadingRemoveInfo(  # 第1页 - 多行页眉页脚
            page=1,
            lines=[1, 2, 7, 8],  # 删除双行页眉和页脚
            reason="header",
            pattern=HeadingHeaderPattern.TITLE_PAGE,
            confidence=0.95
        ),
        HeadingRemoveInfo(  # 第2页 - 带分隔线
            page=2,
            lines=[1, 2, 9, 10],  # 删除页眉、分隔线和页脚
            reason="separator",
            pattern=HeadingHeaderPattern.TITLE_NUMBER,
            confidence=0.98
        ),
        HeadingRemoveInfo(  # 第3页 - 带子页眉
            page=3,
            lines=[1, 2, 9, 10],  # 删除页眉、子页眉和页脚
            reason="footer",
            pattern=HeadingHeaderPattern.CHAPTER_TITLE,
            confidence=0.90
        ),
        HeadingRemoveInfo(  # 第4页 - 错误测试
            page=4,
            lines=[1, 99],  # 包含无效行号
            reason="header",
            pattern=HeadingHeaderPattern.CUSTOM,
            confidence=0.85
        )
    ]
    
    # 创建处理器实例
    logger.info("Creating processor instance...")
    md_info = MdInfo(info_path)
    processor = HeaderFooterProcessor(md_info)
    
    # 处理页眉页脚
    logger.info(f"Starting to process {len(test_pages)} pages with {len(remove_infos)} remove instructions...")
    result = processor.process(test_pages, remove_infos)
    
    # 打印处理结果
    if result:
        logger.info("Processing completed successfully")
        print("\n=== 原始内容 ===")
        for idx, page in enumerate(test_pages, 1):
            print(f"\n--- 第{idx}页 ---")
            print("\n".join(page))
            
        print("\n=== 处理后内容 ===")
        for idx, page in enumerate(result, 1):
            print(f"\n--- 第{idx}页 ---")
            print("\n".join(page))
            
        # 验证结果
        logger.info("Validating results...")
        for idx, (orig, proc) in enumerate(zip(test_pages, result), 1):
            removed = len(orig) - len(proc)
            logger.info(f"Page {idx}: Removed {removed} lines")
    else:
        logger.error("Processing failed!") 