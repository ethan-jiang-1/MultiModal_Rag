# Converters Module

文档转换器模块，提供各种文档格式到Markdown的转换接口，是连接上层应用和底层生成引擎的桥梁。

## 功能特点

- 统一的转换接口
- 智能引擎选择
- 错误处理和恢复
- 转换进度跟踪

## 模块组成

```
converters/
├── converter_pdf_lvlm.py       # LVLM引擎PDF转换器
├── converter_pdf_textin.py     # TextIn引擎PDF转换器
├── converter_all_llamaparse.py # LlamaParse通用转换器
├── converter_ppt_pptx2md.py   # PPT专用转换器
├── converter_md_plain.py       # Markdown纯文本转换器
└── converter_all_markitdown.py # Markitdown通用转换器
```

## 核心功能

### 1. 格式转换
- 自动格式检测
- 引擎选择和调度
- 转换流程控制

### 2. 质量保证
- 转换质量检查
- 错误自动修复
- 格式标准化

### 3. 进度管理
- 转换状态追踪
- 断点续传支持
- 日志记录

## 使用方法

```python
# 1. PDF文档转换 (LVLM引擎)
from ctn2md.converters.converter_pdf_lvlm import do_content2md_convert
result = do_content2md_convert("doc.pdf")

# 2. PDF文档转换 (TextIn引擎)
from ctn2md.converters.converter_pdf_textin import do_content2md_convert
result = do_content2md_convert("doc.pdf")

# 3. 通用格式转换 (LlamaParse引擎)
from ctn2md.converters.converter_all_llamaparse import do_content2md_convert
result = do_content2md_convert("doc.*")

# 4. PPT专用转换
from ctn2md.converters.converter_ppt_pptx2md import do_content2md_convert
result = do_content2md_convert("slide.pptx")

# 5. 批量转换
from ctn2md.batch_cvt_papers import batch_convert
batch_convert(["doc1.pdf", "doc2.pdf"])
```

## 最佳实践

1. 引擎选择：
   - 复杂排版PDF使用LVLM引擎
   - 文本为主PDF使用TextIn引擎
   - 其他格式使用LlamaParse引擎

2. 错误处理：
   - 设置合适的重试策略
   - 保存中间转换结果
   - 记录详细错误日志

3. 性能优化：
   - 合理设置并发数
   - 使用批量转换
   - 启用缓存机制 