# TextIn 转换器

基于OCR技术的高质量文档转换引擎，专注于文本提取和版面分析。

## 特点

### 1. 核心能力
- **精准的OCR识别**
  - 多语言文本支持
  - 版面布局分析
  - 表格结构识别
  - 列表格式处理

- **智能版面分析**
  - 自动分栏处理
  - 页眉页脚识别
  - 文本流重建
  - 段落智能合并

### 2. 性能特性
- **异步处理支持**
  - 页面并行处理
  - 资源智能调度
  - 进度实时监控

- **增量更新**
  - 页面级缓存
  - 智能差异检测
  - 选择性重处理

## 技术实现

### 主要组件
```
gen_ti/
├── ti_gen_pages.py          # 页面生成核心
├── ti_pdf_pages_to_images.py # PDF转图像
└── ti_pdf_images_to_mds.py   # 图像转Markdown
```

### 处理流程
1. PDF文档预处理
2. 页面图像提取
3. OCR文本识别
4. 版面结构分析
5. Markdown生成
6. 质量优化

## 使用指南

### 基本用法
```python
from ctn2md.ctn2md_converter_ti import do_content2md_convert

# 单文件转换
result = do_content2md_convert("document.pdf")

# 使用自定义配置
controls = {
    "mctl_ge_md_async": True,     # 启用异步处理
    "mctl_ocr_quality": "high",   # OCR质量设置
    "mctl_layout_optimize": True  # 启用版面优化
}
result = do_content2md_convert("document.pdf", mdcontrols=controls)
```

### 配置选项
- `mctl_ge_md_async`: 异步处理开关
- `mctl_ocr_quality`: OCR质量级别
- `mctl_layout_optimize`: 版面优化开关
- `mctl_cache_enabled`: 缓存功能开关

## 最佳实践

### 1. 性能优化
- 使用异步模式处理大文档
- 启用缓存减少重复处理
- 合理设置OCR质量参数

### 2. 质量提升
- 对扫描质量差的文档进行预处理
- 使用高质量OCR设置
- 启用版面优化功能

### 3. 常见问题
- 处理大文件时内存使用
- 特殊字符识别优化
- 表格复杂度处理

## 系统要求

- Python 3.12+
- 内存：4GB+
- 支持的文件格式：
  - PDF（推荐）
  - DOC/DOCX
  - 扫描文档
