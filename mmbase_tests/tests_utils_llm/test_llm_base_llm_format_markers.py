#import pytest
from mmbase.utils_llm.llm_base import strip_llm_format_markers

def test_strip_llm_format_markers():
    """测试清理LLM输出中的markdown格式标记"""
    
    # 测试基本场景
    result = strip_llm_format_markers("```markdown\n内容\n```")
    print("\n=== 测试基本场景 ===")
    print(f"实际结果: '{result}'")
    print(f"预期结果: '内容'")
    assert result == "内容"
    
    assert strip_llm_format_markers("```\n内容\n```") == "内容"
    assert strip_llm_format_markers("```内容```") == "内容"
    
    # 测试带有额外空白字符的场景
    result = strip_llm_format_markers("  ```markdown  \n内容\n  ```  ")
    print("\n=== 测试空白字符场景 ===")
    print(f"实际结果: '{result}'")
    print(f"预期结果: '内容'")
    assert result == "内容"
    
    result = strip_llm_format_markers("\n```\n内容\n```\n")
    print("\n=== 测试换行场景 ===")
    print(f"实际结果: '{result}'")
    print(f"预期结果: '内容'")
    assert result == "内容"
    
    result = strip_llm_format_markers("\n\n```markdown\n内容\n```\n\n")
    print("\n=== 测试多换行场景 ===")
    print(f"实际结果: '{result}'")
    print(f"预期结果: '内容'")
    assert result == "内容"
    
    # 测试多行内容
    result = strip_llm_format_markers("```\n第一行\n第二行\n```")
    print("\n=== 测试多行内容 ===")
    print(f"实际结果: '{result}'")
    print(f"预期结果: '第一行\n第二行'")
    assert result == "第一行\n第二行"
    
    result = strip_llm_format_markers("```markdown\n第一行\n第二行\n```")
    print("\n=== 测试多行内容带markdown ===")
    print(f"实际结果: '{result}'")
    print(f"预期结果: '第一行\n第二行'")
    assert result == "第一行\n第二行"
    
    # 测试特殊标记替换
    result = strip_llm_format_markers("内容[ocr_end]后续")
    print("\n=== 测试特殊标记替换 ===")
    print(f"实际结果: '{result}'")
    print(f"预期结果: '内容 后续'")
    assert result == "内容 后续"
    
    result = strip_llm_format_markers("```\n内容[ocr_end]后续\n```")
    print("\n=== 测试特殊标记替换带代码块 ===")
    print(f"实际结果: '{result}'")
    print(f"预期结果: '内容 后续'")
    assert result == "内容 后续"
    
    # 测试边界情况
    assert strip_llm_format_markers("") == ""
    assert strip_llm_format_markers(None) is None
    assert strip_llm_format_markers("   ") == ""
    assert strip_llm_format_markers("纯文本内容") == "纯文本内容"
    
    # 测试不完整或异常的标记
    result = strip_llm_format_markers("```markdown\n内容")
    print("\n=== 测试不完整标记 ===")
    print(f"实际结果: '{result}'")
    print(f"预期结果: '内容'")
    assert result == "内容"
    
    result = strip_llm_format_markers("内容\n```")
    print("\n=== 测试不完整标记2 ===")
    print(f"实际结果: '{result}'")
    print(f"预期结果: '内容'")
    assert result == "内容"
    
    result = strip_llm_format_markers("``` ```")
    print("\n=== 测试空内容标记 ===")
    print(f"实际结果: '{result}'")
    print(f"预期结果: ''")
    assert result == ""


def test_strip_llm_format_markers_complex0():
    """测试包含SQL代码块的复杂内容"""
    content = """```markdown
以下是一个SQL查询示例：
```
sql
SELECT
...
```
这个查询统计了活跃用户的订单数量。
```"""

    expected = """以下是一个SQL查询示例：
```
sql
SELECT
...
```
这个查询统计了活跃用户的订单数量。"""

    result = strip_llm_format_markers(content)
    print("\n=== 实际结果 ===\n")
    print(result)
    print("\n=== 预期结果 ===\n")
    print(expected)
    assert strip_llm_format_markers(content) == expected


def test_strip_llm_format_markers_complex1():
    """测试包含SQL代码块的复杂内容"""
    content = """  ```markdown
以下是一个SQL查询示例：
```
sql
SELECT
...
```
这个查询统计了活跃用户的订单数量。
```
"""

    expected = """以下是一个SQL查询示例：
```
sql
SELECT
...
```
这个查询统计了活跃用户的订单数量。"""

    result = strip_llm_format_markers(content)
    print("\n=== 实际结果 ===\n")
    print(result)
    print("\n=== 预期结果 ===\n")
    print(expected)
    assert strip_llm_format_markers(content) == expected


def test_strip_llm_format_markers_complex2():
    """测试包含SQL代码块的复杂内容"""
    content = """  
    
    ```markdown
以下是一个SQL查询示例：
```
sql
SELECT
...
```
这个查询统计了活跃用户的订单数量。
```


"""

    expected = """以下是一个SQL查询示例：
```
sql
SELECT
...
```
这个查询统计了活跃用户的订单数量。"""

    result = strip_llm_format_markers(content)
    print("\n=== 实际结果 ===\n")
    print(result)
    print("\n=== 预期结果 ===\n")
    print(expected)
    assert strip_llm_format_markers(content) == expected

