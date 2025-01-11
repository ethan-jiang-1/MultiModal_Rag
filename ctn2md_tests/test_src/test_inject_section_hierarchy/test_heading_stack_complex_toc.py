"""
测试 heading_stack 模块的复杂 TOC 场景
主要测试各种复杂的目录结构和层级变化
"""
from ctn2md.src.inject_section_hierarchy.heading_stack import HeadingStack

def test_complex_toc_deep_nesting():
    """测试复杂TOC场景1：深度嵌套
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

def test_complex_toc_irregular_jumps():
    """测试复杂TOC场景2：不规则的层级跳转
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

def test_complex_toc_mixed_patterns():
    """测试复杂TOC场景3：混合模式
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