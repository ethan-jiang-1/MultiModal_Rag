# LlamaParse Engine

通用文档解析引擎，支持多种格式（PDF、DOCX、PPTX、TXT、MD、HTML等）的文档转换，提供统一的Markdown输出。

## 功能特点

- 多格式支持
- 内容结构化
- 智能图片处理
- 格式自动优化

## 模块组成

```
gen_llamaparse/
├── lp_base.py               # 基础功能实现
├── lp_page2markdown.py      # 页面到Markdown转换
├── lp_gen_normal_pages.py   # 普通页面生成
├── lp_gen_premium_pages.py  # 高级页面生成
├── gen_markdown_llamaparse.py # Markdown生成器
├── _download_images.py      # 图片下载
├── _download_table.py       # 表格下载
└── _download_image_status.py # 图片状态管理
```

## 核心功能

### 1. 文档解析
- 多格式解析支持
- 内容提取
- 结构识别

### 2. 资源处理
- 图片智能处理
- 表格结构化
- 资源状态管理

### 3. Markdown生成
- 格式标准化
- 内容优化
- 引用管理

## 使用方法

```python
from ctn2md.converters.converter_all_llamaparse import do_content2md_convert

# 基本使用
result = do_content2md_convert("your_doc.pdf")  # 或 .docx, .pptx 等

```

## 最佳实践

1. 格式选择：
   - 优先使用原生格式
   - 避免扫描版PDF
   - 保持格式一致性

2. 性能优化：
   - 合理设置相关性阈值
   - 使用适当的语言模型
   - 控制并发下载数

3. 质量控制：
   - 验证格式转换
   - 检查资源完整性
   - 保持结构一致性 