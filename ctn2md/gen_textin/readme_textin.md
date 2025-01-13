# TextIn Engine

基于OCR技术的文档转换引擎，专门用于处理以文本为主的PDF文档，提供可靠的文本提取和结构化能力。

## 功能特点

- 精确OCR文本识别
- 智能布局分析
- 图片描述生成
- 文本结构重建

## 模块组成

```
gen_textin/
├── _ti_gen_md.py          # Markdown生成核心
├── _ti_get_image.py       # 图片获取模块
├── _ti_img_description.py # 图片描述生成
├── _ti_update_img_ref.py  # 图片引用更新
├── ti_pdf_pages_to_images.py  # PDF页面转图片
└── ti_pdf_images_to_mds.py    # 图片到Markdown转换
```

## 核心功能

### 1. 文本处理
- OCR文本提取
- 文本格式保持
- 段落智能分割

### 2. 图片处理
- 图片区域识别
- 智能描述生成
- 引用关系维护

### 3. 结构化转换
- 文档结构分析
- 层级关系重建
- 格式标准化

## 使用方法

```python
from ctn2md.converters.converter_pdf_textin import do_content2md_convert

# 基本使用
result = do_content2md_convert("your_doc.pdf")

```

## 最佳实践

1. OCR优化：
   - 使用高质量PDF源文件
   - 合理设置DPI参数
   - 预处理图片提高质量

2. 性能优化：
   - 启用指令和描述缓存
   - 使用异步处理大文件
   - 合理设置批处理大小

3. 质量控制：
   - 验证OCR准确性
   - 检查图文对应关系
   - 保持格式一致性 