# Markdown 源码处理模块

## 快速导航

### 关键文件索引
- `ctn2md_fix_heading_plc.py` - 标题层级修复主入口
- `ctn2md_inject_section_hierarchy.py` - 章节层级注入主入口
- `ctn2md_summarize_content.py` - 内容总结主入口
- `make_final_result.py` - 最终结果生成
- `page_spe_md.py` - 页面特殊处理
- `heading_plc_md.py` - 标题位置处理

### 按功能查找
- 需要修复标题层级? → 使用 `fix_heading_plc` 模块
- 需要注入章节结构? → 使用 `inject_section_hierarchy` 模块
- 需要生成内容总结? → 使用 `summarize_content` 模块

## 核心功能

### 1. 标题层级修复
```python
from ctn2md.src.ctn2md_fix_heading_plc import fix_headings_plc_by_llm

# 修复标题层级
md_info_path = fix_headings_plc_by_llm(md_info_path, src_step_num=0, dst_step_num=1)
```

### 2. 章节层级注入
```python
from ctn2md.src.ctn2md_inject_section_hierarchy import inject_section_hierarchy

# 注入章节层级并分割文件
md_info_path = inject_section_hierarchy(md_info_path, src_step_num=1, dst_step_num=2)
```

### 3. 内容总结生成
```python
from ctn2md.src.ctn2md_summarize_content import summarize_content_by_llm

# 生成文档总结
md_info_path = summarize_content_by_llm(md_info_path, src_step_num=2)
```

## 处理流程

### 1. 标题层级处理流程
1. **收集标题信息**
   - 使用 `heading_collector.py` 收集标题
   - 分析标题层级关系
   - 生成初始标题映射

2. **计算标题映射**
   - 使用 LLM 优化标题层级
   - 缓存计算结果
   - 验证映射有效性

3. **更新文档内容**
   - 应用标题映射
   - 保存处理结果
   - 更新处理状态

### 2. 章节层级注入流程
1. **处理层级结构**
   - 分析文档结构
   - 注入层级描述
   - 验证层级正确性

2. **文件分割**
   - 按章节分割文件
   - 生成章节索引
   - 保存分割结果

### 3. 内容总结流程
1. **文档分析**
   - 读取文档内容
   - 移除注释信息
   - 提取关键信息

2. **生成总结**
   - 使用 LLM 生成关键词
   - 生成文档摘要
   - 保存总结结果

## 最佳实践

### 开发建议
1. **步骤编号管理**
   - 合理设置 src_step_num
   - 正确指定 dst_step_num
   - 保持步骤连续性

2. **错误处理**
   - 检查文件存在性
   - 验证处理结果
   - 保存处理状态

### 性能优化
1. **缓存使用**
   - LLM 结果缓存
   - 文件内容缓存
   - 定期清理缓存

2. **资源管理**
   - 及时关闭文件
   - 清理临时文件
   - 释放内存资源 