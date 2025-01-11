"""
测试 heading_stack 模块的混合模式场景
主要测试各种模式的混合使用，包括深层级、跳级、返回等
"""
from ctn2md.src.inject_section_hierarchy.heading_stack import HeadingStack

def test_mixed_patterns_toc():
    """测试混合模式的TOC结构
    测试各种模式的混合使用，包括深层级、跳级、返回等
    
    1. 引言
            1.0.1 核心概念 (直接三级)
        1.1 背景介绍 (返回二级)
                1.1.1.1 详细说明 (跳到四级)
        1.2 研究意义 (返回二级)
    2. 分析
        2.1 方法
            2.1.1 步骤
        2.2 结果
                2.2.1.1 数据分析 (跳到四级)
            2.2.2 结论 (返回三级)
                    2.2.2.1.1 补充说明 (跳到五级)
        2.3 讨论 (返回二级)
    """
    stack = HeadingStack()
    
    # 1. 引言
    assert stack.push_level(1, "引言") == "1"
    assert stack.get_hierarchy_desc() == "引言"
    
    # 1.0.1 核心概念 (直接三级)
    assert stack.push_level(3, "核心概念") == "1.1.1"
    assert stack.get_hierarchy_desc() == "引言 __ PL2 __ 核心概念"
    
    # 1.1 背景介绍 (返回二级)
    assert stack.push_level(2, "背景介绍") == "1.2"
    assert stack.get_hierarchy_desc() == "引言 __ 背景介绍"
    
    # 1.1.1.1 详细说明 (跳到四级)
    assert stack.push_level(4, "详细说明") == "1.2.1.1"
    assert stack.get_hierarchy_desc() == "引言 __ 背景介绍 __ PL3 __ 详细说明"
    
    # 1.2 研究意义 (返回二级)
    assert stack.push_level(2, "研究意义") == "1.3"
    assert stack.get_hierarchy_desc() == "引言 __ 研究意义"
    
    # 2. 分析
    assert stack.push_level(1, "分析") == "2"
    assert stack.get_hierarchy_desc() == "分析"
    
    # 2.1 方法
    assert stack.push_level(2, "方法") == "2.1"
    assert stack.get_hierarchy_desc() == "分析 __ 方法"
    
    # 2.1.1 步骤
    assert stack.push_level(3, "步骤") == "2.1.1"
    assert stack.get_hierarchy_desc() == "分析 __ 方法 __ 步骤"
    
    # 2.2 结果
    assert stack.push_level(2, "结果") == "2.2"
    assert stack.get_hierarchy_desc() == "分析 __ 结果"
    
    # 2.2.1.1 数据分析 (跳到四级)
    assert stack.push_level(4, "数据分析") == "2.2.1.1"
    assert stack.get_hierarchy_desc() == "分析 __ 结果 __ PL3 __ 数据分析"
    
    # 2.2.2 结论 (返回三级)
    assert stack.push_level(3, "结论") == "2.2.2"
    assert stack.get_hierarchy_desc() == "分析 __ 结果 __ 结论"
    
    # 2.2.2.1.1 补充说明 (跳到五级)
    assert stack.push_level(5, "补充说明") == "2.2.2.1.1"
    assert stack.get_hierarchy_desc() == "分析 __ 结果 __ 结论 __ PL4 __ 补充说明"
    
    # 2.3 讨论 (返回二级)
    assert stack.push_level(2, "讨论") == "2.3"
    assert stack.get_hierarchy_desc() == "分析 __ 讨论" 