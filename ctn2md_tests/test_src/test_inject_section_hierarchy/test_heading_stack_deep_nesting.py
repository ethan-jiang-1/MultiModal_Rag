"""
测试 heading_stack 模块的深度嵌套场景
主要测试连续的深层级嵌套和在深层级间的跳转
"""
from ctn2md.src.inject_section_hierarchy.heading_stack import HeadingStack

def test_deep_nesting_toc():
    """测试深度嵌套的TOC结构
    测试连续的深层级嵌套和在深层级间的跳转
    
    1. 前言
        1.1 背景
            1.1.1 历史
                1.1.1.1 早期阶段
                1.1.1.2 发展期
            1.1.2 现状
        1.2 目标
            1.2.1 主要目标
            1.2.2 具体目标
    2. 方法论
        2.1 概述
    """
    stack = HeadingStack()
    
    # 1. 前言
    assert stack.push_level(1, "前言") == "1"
    assert stack.get_hierarchy_desc() == "前言"
    
    # 1.1 背景
    assert stack.push_level(2, "背景") == "1.1"
    assert stack.get_hierarchy_desc() == "前言 __ 背景"
    
    # 1.1.1 历史
    assert stack.push_level(3, "历史") == "1.1.1"
    assert stack.get_hierarchy_desc() == "前言 __ 背景 __ 历史"
    
    # 1.1.1.1 早期阶段
    assert stack.push_level(4, "早期阶段") == "1.1.1.1"
    assert stack.get_hierarchy_desc() == "前言 __ 背景 __ 历史 __ 早期阶段"
    
    # 1.1.1.2 发展期
    assert stack.push_level(4, "发展期") == "1.1.1.2"
    assert stack.get_hierarchy_desc() == "前言 __ 背景 __ 历史 __ 发展期"
    
    # 1.1.2 现状 (返回到三级)
    assert stack.push_level(3, "现状") == "1.1.2"
    assert stack.get_hierarchy_desc() == "前言 __ 背景 __ 现状"
    
    # 1.2 目标 (返回到二级)
    assert stack.push_level(2, "目标") == "1.2"
    assert stack.get_hierarchy_desc() == "前言 __ 目标"
    
    # 1.2.1 主要目标
    assert stack.push_level(3, "主要目标") == "1.2.1"
    assert stack.get_hierarchy_desc() == "前言 __ 目标 __ 主要目标"
    
    # 1.2.2 具体目标
    assert stack.push_level(3, "具体目标") == "1.2.2"
    assert stack.get_hierarchy_desc() == "前言 __ 目标 __ 具体目标"
    
    # 2. 方法论 (新的一级标题)
    assert stack.push_level(1, "方法论") == "2"
    assert stack.get_hierarchy_desc() == "方法论"
    
    # 2.1 概述
    assert stack.push_level(2, "概述") == "2.1"
    assert stack.get_hierarchy_desc() == "方法论 __ 概述" 