"""
测试 heading_stack 模块的不规则跳转场景
主要测试各种不规则的层级跳转，包括跳级和返回
"""
from ctn2md.src.inject_section_hierarchy.heading_stack import HeadingStack

def test_irregular_jumps_toc():
    """测试不规则跳转的TOC结构
    测试各种不规则的层级跳转，包括跳级和返回
    
    1. 概述
        1.1 简介
    2. 主要内容
            2.0.1 前置说明 (跳级到三级)
        2.1 第一部分
                2.1.1.1 细节描述 (跳级到四级)
            2.1.2 补充说明 (返回到三级)
    3. 结论
            3.0.1 要点总结 (直接跳到三级)
        3.1 最终结论 (返回到二级)
    """
    stack = HeadingStack()
    
    # 1. 概述
    assert stack.push_level(1, "概述") == "1"
    assert stack.get_hierarchy_desc() == "概述"
    
    # 1.1 简介
    assert stack.push_level(2, "简介") == "1.1"
    assert stack.get_hierarchy_desc() == "概述 __ 简介"
    
    # 2. 主要内容
    assert stack.push_level(1, "主要内容") == "2"
    assert stack.get_hierarchy_desc() == "主要内容"
    
    # 2.0.1 前置说明 (跳级到三级)
    assert stack.push_level(3, "前置说明") == "2.1.1"
    assert stack.get_hierarchy_desc() == "主要内容 __ PL2 __ 前置说明"
    
    # 2.1 第一部分 (返回到二级)
    assert stack.push_level(2, "第一部分") == "2.2"
    assert stack.get_hierarchy_desc() == "主要内容 __ 第一部分"
    
    # 2.1.1.1 细节描述 (跳级到四级)
    assert stack.push_level(4, "细节描述") == "2.2.1.1"
    assert stack.get_hierarchy_desc() == "主要内容 __ 第一部分 __ PL3 __ 细节描述"
    
    # 2.1.2 补充说明 (返回到三级)
    assert stack.push_level(3, "补充说明") == "2.2.2"
    assert stack.get_hierarchy_desc() == "主要内容 __ 第一部分 __ 补充说明"
    
    # 3. 结论
    assert stack.push_level(1, "结论") == "3"
    assert stack.get_hierarchy_desc() == "结论"
    
    # 3.0.1 要点总结 (直接跳到三级)
    assert stack.push_level(3, "要点总结") == "3.1.1"
    assert stack.get_hierarchy_desc() == "结论 __ PL2 __ 要点总结"
    
    # 3.1 最终结论 (返回到二级)
    assert stack.push_level(2, "最终结论") == "3.2"
    assert stack.get_hierarchy_desc() == "结论 __ 最终结论" 