from dotenv import load_dotenv
import os
from dataclasses import dataclass
from typing import Dict, List, Optional

load_dotenv()

if __name__ == "__main__":
    from dotenv import find_dotenv
    _root_dir = os.path.abspath(os.path.dirname(find_dotenv()))
    os.chdir(_root_dir)

@dataclass
class PageAnalysisResult:
    """页面分析结果"""
    simple_patterns: Dict[str, List[str]]    # 简单模式（页眉页脚等）
    llm_analyzed: Dict[str, Dict]            # LLM分析结果
    page_actions: Dict[int, List[Dict]]      # 需要执行的动作，按页码索引

@dataclass
class PageAction:
    """页面动作"""
    type: str                # 动作类型：remove/modify/merge
    target: str             # 目标：header/footer/heading/table
    position: Dict          # 位置信息
    params: Dict            # 动作参数
    page_number: Optional[int] = None  # 页码（可选） 