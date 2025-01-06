import pytest
import os
import json
from pathlib import Path

@pytest.fixture
def test_data_dir(tmp_path):
    """创建临时测试数据目录"""
    return tmp_path / "test_data"

@pytest.fixture
def sample_doc_meta(test_data_dir):
    """创建示例文档元数据"""
    meta_data = {
        "doc_id": "test_doc_123",
        "doc_summary": "这是一个测试文档，主要讨论机器学习和人工智能相关内容。",
        "sections": [
            {
                "title": "机器学习简介",
                "content": "机器学习是人工智能的一个分支，主要研究计算机怎样模拟或实现人类的学习行为。"
            },
            {
                "title": "深度学习",
                "content": "深度学习是机器学习的一个重要分支，它使用多层神经网络来学习数据的特征。"
            }
        ]
    }
    
    # 创建目录结构
    doc_dir = test_data_dir / meta_data["doc_id"]
    doc_dir.mkdir(parents=True, exist_ok=True)
    
    # 写入元数据文件
    meta_file = doc_dir / "doc_meta.json"
    meta_file.write_text(json.dumps(meta_data, ensure_ascii=False, indent=2))
    
    return meta_data

@pytest.fixture
def sample_sections():
    """返回示例文档片段列表"""
    return [
        "机器学习是人工智能的一个分支，主要研究计算机怎样模拟或实现人类的学习行为。",
        "深度学习是机器学习的一个重要分支，它使用多层神经网络来学习数据的特征。",
        "强化学习是一种通过与环境交互来学习的机器学习方法。",
        "自然语言处理是人工智能的重要应用领域之一。"
    ]

@pytest.fixture
def sample_queries():
    """返回示例查询列表"""
    return [
        "什么是机器学习",
        "深度学习神经网络",
        "强化学习应用",
        "自然语言处理"
    ]

@pytest.fixture
def cleanup_test_files():
    """测试后清理临时文件的fixture"""
    yield
    # 在这里添加需要清理的文件路径模式
    patterns_to_clean = [
        "**/bm25_*.msgpack",
        "**/cached_bm25/*"
    ]
    
    def remove_file(file_path):
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Warning: Failed to remove {file_path}: {e}")
    
    # 清理文件
    for pattern in patterns_to_clean:
        for file_path in Path().glob(pattern):
            remove_file(str(file_path)) 