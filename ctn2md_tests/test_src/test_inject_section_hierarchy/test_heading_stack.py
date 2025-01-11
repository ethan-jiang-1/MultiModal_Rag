"""
测试 heading_stack 模块
主要测试标题层级管理的基础功能
"""
from ctn2md.src.inject_section_hierarchy.heading_stack import HeadingStack

def test_heading_stack_init():
    """测试 HeadingStack 初始化"""
    stack = HeadingStack()
    assert stack._stack == []
    assert stack._chapter_numbers == []
    assert stack._log == []

def test_first_level_heading():
    """测试一级标题处理"""
    stack = HeadingStack()
    chapter_num = stack.push_level(1, "引言")
    assert chapter_num == "1"
    assert stack.get_hierarchy_desc() == "引言"

def test_second_level_heading():
    """测试二级标题处理"""
    stack = HeadingStack()
    stack.push_level(1, "引言")
    chapter_num = stack.push_level(2, "研究背景")
    assert chapter_num == "1.1"
    assert stack.get_hierarchy_desc() == "引言 __ 研究背景"

def test_skip_level_heading():
    """测试跳级（从二级到四级）"""
    stack = HeadingStack()
    stack.push_level(1, "引言")
    stack.push_level(2, "研究背景")
    chapter_num = stack.push_level(4, "具体问题")
    assert chapter_num == "1.1.1.1"
    assert stack.get_hierarchy_desc() == "引言 __ 研究背景 __ PL3 __ 具体问题"

def test_return_to_upper_level():
    """测试返回上级（从三级返回到二级）"""
    stack = HeadingStack()
    stack.push_level(1, "引言")
    stack.push_level(2, "研究背景")
    stack.push_level(3, "问题1")
    chapter_num = stack.push_level(2, "研究方法")
    assert chapter_num == "1.2"
    assert stack.get_hierarchy_desc() == "引言 __ 研究方法"

def test_new_first_level_heading():
    """测试新的一级标题（重置堆栈）"""
    stack = HeadingStack()
    stack.push_level(1, "引言")
    stack.push_level(2, "研究背景")
    chapter_num = stack.push_level(1, "实验结果")
    assert chapter_num == "2"
    assert stack.get_hierarchy_desc() == "实验结果"

def test_multiple_sections_at_same_level():
    """测试同级标题的编号递增"""
    stack = HeadingStack()
    stack.push_level(1, "第一章")
    stack.push_level(2, "1.1节")
    stack.push_level(2, "1.2节")
    chapter_num = stack.push_level(2, "1.3节")
    assert chapter_num == "1.3"
    assert stack.get_hierarchy_desc() == "第一章 __ 1.3节" 