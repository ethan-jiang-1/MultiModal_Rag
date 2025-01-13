# Source Module

核心功能实现模块，提供文档转换的基础功能和流程控制。

## 功能特点

- 信息管理
- 流程控制
- 内容处理
- 结果生成

## 模块组成

```
src/
├── md_info_base.py                    # 基础信息处理
├── md_info_ctrl.py                    # 控制逻辑
├── md_process_plc.py                  # 处理流程
├── ctn2md_fix_heading_plc.py          # 标题修复
├── ctn2md_inject_section_hierarchy.py # 章节层级注入
├── ctn2md_summarize_content.py        # 内容总结
└── make_final_result.py               # 最终结果生成
```

## 核心功能

### 1. 信息管理
- 文档信息维护
- 状态追踪
- 配置管理

### 2. 内容处理
- 标题层级优化
- 章节结构注入
- 内容智能总结

### 3. 结果生成
- 格式标准化
- 质量检查
- 结果输出

## 使用方法

```python
# 1. 基础信息处理
from ctn2md.src.md_info_base import MdInfo
md_info = MdInfo("path/to/info.json")

# 2. 标题修复
from ctn2md.src.ctn2md_fix_heading_plc import fix_headings_plc_by_llm
result = fix_headings_plc_by_llm("path/to/md")

# 3. 章节层级注入
from ctn2md.src.ctn2md_inject_section_hierarchy import inject_section_hierarchy
result = inject_section_hierarchy("path/to/md")

# 4. 内容总结
from ctn2md.src.ctn2md_summarize_content import summarize_content_by_llm
summary = summarize_content_by_llm("path/to/md")

# 5. 最终结果生成
from ctn2md.src.make_final_result import make_final_json
final_result = make_final_json("path/to/md")
```

## 最佳实践

1. 信息管理：
   - 及时更新状态
   - 保持配置一致
   - 处理异常情况

2. 内容处理：
   - 验证标题层级
   - 检查章节完整性
   - 优化摘要质量

3. 结果生成：
   - 执行质量检查
   - 保存中间结果
   - 记录处理日志 