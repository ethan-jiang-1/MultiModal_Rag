import os
import pytest
from ctn2md.utils.util_file import get_root_dir, get_crc32_id


def test_get_root_dir():
    """测试获取项目根目录功能"""
    root_dir = get_root_dir()
    
    # 验证返回的是字符串类型
    assert isinstance(root_dir, str)
    
    # 验证返回的是绝对路径
    assert os.path.isabs(root_dir)
    
    # 验证目录确实存在
    assert os.path.exists(root_dir)
    
    # 验证是否包含关键项目文件/目录
    essential_items = ['ctn2md', 'tests', '.env']
    for item in essential_items:
        assert os.path.exists(os.path.join(root_dir, item)), f"项目根目录应该包含 {item}"


@pytest.mark.parametrize("input_str", [
    "Hello, World!",      # 基本ASCII字符串
    "测试中文",           # 中文字符串
    "",                   # 空字符串
    "!@#$%^&*()",        # 特殊字符
    "1234567890",         # 数字字符串
    "a" * 1000,          # 长字符串
    " ",                 # 空格
    "Hello\nWorld",       # 包含换行符
])
def test_get_crc32_id_format(input_str):
    """测试CRC32校验和计算的格式"""
    result = get_crc32_id(input_str)
    
    # 验证返回值类型
    assert isinstance(result, str)
    
    # 验证返回值长度为8（8位十六进制）
    assert len(result) == 8
    
    # 验证返回值是有效的十六进制字符串
    assert all(c in '0123456789abcdef' for c in result)


def test_get_crc32_id_consistency():
    """测试CRC32计算的一致性"""
    test_cases = [
        "Hello, World!",
        "测试中文",
        "!@#$%^&*()",
        "a" * 1000,
    ]
    
    for test_str in test_cases:
        # 多次计算同一字符串应该得到相同的结果
        first_result = get_crc32_id(test_str)
        for _ in range(5):
            assert get_crc32_id(test_str) == first_result


def test_get_crc32_id_uniqueness():
    """测试不同输入产生不同的CRC32值"""
    test_cases = [
        "Hello, World!",
        "Hello, world!",  # 大小写不同
        "Hello,World!",   # 空格不同
        "HelloWorld!",    # 完全不同
    ]
    
    # 收集所有结果
    results = [get_crc32_id(s) for s in test_cases]
    
    # 验证所有结果都是唯一的
    assert len(set(results)) == len(results), "不同的输入应该产生不同的CRC32值"


@pytest.mark.parametrize("invalid_input", [
    None,
    123,
    1.23,
    [],
    {},
    True,
])
def test_get_crc32_id_invalid_input(invalid_input):
    """测试CRC32计算对无效输入的处理"""
    with pytest.raises(AttributeError):
        get_crc32_id(invalid_input) 